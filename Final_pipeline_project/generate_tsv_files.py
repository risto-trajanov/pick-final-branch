import os
import glob
import json
import pipeline_settings as settings
from coords_util import split_words
import time

input_image_dir = settings.images_after_ocr
input_coords_dir = settings.coords_after_ocr
input_json_dir = settings.json_after_ocr
output_dir = settings.model_all_data
fields = settings.fields


def get_boxes_and_coordinates(image_coords, labels=True):
    lines = []
    i = 1
    for box_coord_info in image_coords:
        if labels:
            training_point_line = "%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%s\n" % (
                i, box_coord_info['x_0'], box_coord_info['y_0'], box_coord_info['x_1'],
                box_coord_info['y_0'],
                box_coord_info['x_1'], box_coord_info['y_1'], box_coord_info['x_0'], box_coord_info['y_1'],
                box_coord_info['text'].replace(',', ''), box_coord_info['entity_type'])
            lines.append(training_point_line)
        else:
            testing_point_line = "%d,%d,%d,%d,%d,%d,%d,%d,%d,%s\n" % (
                i, box_coord_info['x_0'], box_coord_info['y_0'], box_coord_info['x_1'],
                box_coord_info['y_0'],
                box_coord_info['x_1'], box_coord_info['y_1'], box_coord_info['x_0'], box_coord_info['y_1'],
                box_coord_info['text'].replace(',', ''))
            lines.append(testing_point_line)
        i = i + 1
    return lines


def check_reference_equality(transcript_json, key_value, key):
    # Separate equality comparison for each type of entity(key field)
    transcript_json["text"] = ' '.join(transcript_json["text"].split('\n'))
    transcript = transcript_json["text"]
    if key in ["policyNumber", "policyEnd", "insuranceCompany"]:
        return transcript.lower() in [val.lower() for val in key_value.strip().split()]
    elif key in ["fee", "insuranceSum", "insuranceType"]:
        for val in key_value:
            if key in ["fee", "insuranceSum"]:
                val = str(val)  # Parsing
            if transcript in str(val).strip().split():
                return True
    else:
        raise Exception("Key not found (not a valid entity according to the provided input .json files).")


def write_entities_file(all_labels, all_fields, path):
    # All labels is a dict of key value pairs {entity_type:list of text segments}
    with open(path + ".txt", "w", encoding='utf-8') as f:
        f.write('{\n')
        fields_not_present = [field for field in all_fields if field not in list(all_labels.keys())]
        # Writing empty fields
        if len(fields_not_present) == len(all_fields):
            index = 0
            for field in fields_not_present:
                if index == len(fields_not_present) - 1:
                    f.write(' "' + field + '": ""\n}')
                else:
                    f.write(' "' + field + '": "",\n')
                index += 1
        else:
            for field in fields_not_present:
                f.write(' "' + field + '": "",\n')
            # Writing other fields
            string_list = []
            for entity, list_text in all_labels.items():
                for text_item in list_text:
                    string_list.append(' "' + entity + '": "' + text_item + '"')
            string_to_write = ",\n".join(string_list[:-1])
            if len(string_list) == 1:
                string_to_write += f"{string_list[-1]}\n" + "}"
            elif len(string_list) == 0:
                string_to_write += '}'
            else:
                string_to_write += f",\n{string_list[-1]}\n" + "}"
            f.write(string_to_write)


def write_boxes_and_transcripts_file(image_coords, data_json, fields, path):
    all_labels = {}
    for box_coord_info in image_coords:
        # Set a default label for each segment in the coordinates file
        if 'entity_type' not in box_coord_info:
            box_coord_info['entity_type'] = 'other'
        else:
            continue
        # Check for each wanted field, whether the current segment represents some part of it
        val = False
        for field in fields:
            val = check_reference_equality(box_coord_info, data_json[field],
                                           field)
            if val:
                # If yes, set the label to the field
                box_coord_info['entity_type'] = field
                if field in all_labels:
                    if box_coord_info["text"] not in all_labels[field]:
                        all_labels[field].append(box_coord_info["text"])
                else:
                    all_labels[field] = [box_coord_info["text"]]
                break
        if val:
            continue

    # For filling the boxes and coordinates file
    lines = get_boxes_and_coordinates(image_coords)

    # Write the lines in the boxes and transcripts folder
    with open(path + ".tsv", "w", encoding='utf-8') as f:
        f.writelines(lines)

    all_labels_final = {}
    for key, text_list in all_labels.items():
        text_list_unique = list(set(text_list))
        all_labels_final[key] = text_list_unique
    return all_labels_final


def gen_tsv_files(input_image_dir, input_coords_dir, input_json_dir, fields, output_dir):
    """
    Generates boxes and transcripts and entities folders for the images provided.
    :param input_image_dir: The images folder path
    :param input_coords_dir: The ocr coords folder path
    :param input_json_dir: The true label doc level json folder path
    :param fields: The fields to try to assign to the ocr segments
    :param output_dir: The path to the output dir
    :return:
    """
    boxes_and_transcripts_folder = os.path.join(output_dir, "boxes_and_transcripts")
    entities_folder = os.path.join(output_dir, "entities")
    os.makedirs(boxes_and_transcripts_folder, exist_ok=True)
    os.makedirs(entities_folder, exist_ok=True)

    image_files = glob.glob(input_image_dir + "/*.jp*g")
    for image_file in image_files:
        image_path_name = os.path.splitext(os.path.basename(image_file))
        image_base_name = image_path_name[0]
        doc_name = image_base_name.split("_POLICY")[0] + "_POLICY.json"
        print(f'Generating tsv files for image: {image_base_name}')

        # Get the image ocr coordinates file
        with open(input_coords_dir + "/" + image_base_name + "_coords.json") as coord_file:
            image_coords = json.load(coord_file)
        image_coords = split_words(image_coords)

        # Get the label json file for the doc
        with open(input_json_dir + "/" + doc_name) as label_file:
            data_json = json.load(label_file)

        boxes_and_transcripts_path = os.path.join(boxes_and_transcripts_folder, image_base_name)
        entities_path = os.path.join(entities_folder, image_base_name)

        # Write files
        all_labels_train = write_boxes_and_transcripts_file(image_coords, data_json, fields, boxes_and_transcripts_path)
        write_entities_file(all_labels_train, fields, entities_path)


def main():
    start_time = time.time()
    gen_tsv_files(input_image_dir, input_coords_dir, input_json_dir, fields, output_dir)
    return time.time() - start_time


if __name__ == "__main__":
    main()
