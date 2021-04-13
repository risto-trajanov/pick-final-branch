import pandas as pd
import os
import json
import time
from difflib import SequenceMatcher
import pipeline_settings as settings

ocr_folder = settings.coords_after_ocr
model_output_folder = settings.model_output_folder
similarity_output_folder = settings.similarity_output_folder
test_data = settings.valid_samples_list
output_file_name = settings.similarity_output_file
fields = settings.fields
similarity_types = ['SequenceMatcher']


def get_subarray(arr, start, end, array_list):
    if end == len(arr):
        return
    elif start > end:
        return get_subarray(arr, 0, end + 1, array_list)
    else:
        array_list.append(arr[start:end + 1])
        return get_subarray(arr, start + 1, end, array_list)


def get_page_num(ocr_file):
    with open(ocr_file) as json_file:
        ocr_json = json.load(json_file)
    for elem in ocr_json:
        return elem['page']


def get_coords_of_label(ocr_file, label):
    with open(ocr_file) as json_file:
        ocr_json = json.load(json_file)
    for elem in ocr_json:
        if label in str(elem['text']):
            return elem['x_0'], elem['y_0'], elem['x_1'], elem['y_1']


def concat_ocr(ocr_file):
    with open(ocr_file) as json_file:
        ocr_json = json.load(json_file)

    all_segments = []
    for elem in ocr_json:
        text = elem['text']
        coords = (elem['x_0'], elem['y_0'], elem['x_1'], elem['y_1'])
        all_fields = str(text).split()
        all_segments.extend(all_fields)
        array_list = list()
        get_subarray(all_fields, 0, 0, array_list)
        res = [' '.join(inner_list) for inner_list in array_list]
        all_segments.extend(res)

    return all_segments


# similarity_type -> String
# output -> String
# label -> String
def get_similarity(similarity_type, output, label, field):
    output = output.lower()
    label = label.lower()
    if similarity_type == 'SequenceMatcher':
        return SequenceMatcher(None, output, label).ratio()
    elif similarity_type == 'CosineSimilarity':
        return
    else:
        return


# output -> DataFrame
# field -> String
def get_values_with_field(output, field):
    if field in ["insuranceType"]:
        values = output.loc[output[0] == field][1].values
        print(len(values))
        return values
    elif field in ['insuranceSum', 'fee']:
        return output.loc[output[0] == field][1].values

    else:
        list_values = list(output.loc[output[0] == field][1].values)
        values = list(sorted(set(list_values), key=list_values.index))
        value = " ".join(values)
        return [value]


def output_results(output_list):
    similarity_output_df = pd.DataFrame(output_list,
                                        columns=['file', 'doc', 'page', 'field', 'similarity_type', 'ocr',
                                                 'model_output',
                                                 'value', 'x_0', 'y_0', 'x_1', 'y_1'])
    similarity_output_df.to_csv(output_file_name)


def calc_similarity(test_data_list):
    output_files = os.listdir(model_output_folder)
    counter = 0
    counter_empty = 0
    output_list = []
    empty_files = []

    for model_output_file in output_files:
        # Not a validation file
        if not model_output_file.split('.')[0] in test_data_list:
            continue

        # No output in file
        if os.stat(os.path.join(model_output_folder, model_output_file)).st_size == 0:
            empty_files.append(model_output_file)
            counter_empty += 1
            continue

        split = model_output_file.split('.')[0].split('_')[:-1]
        index_policy = split.index("POLICY")
        doc = '_'.join(split[:index_policy + 1])
        data_output = pd.read_csv(os.path.join(model_output_folder, model_output_file), sep="\t", header=None)
        data_output = data_output.applymap(str)
        ocr_filename = model_output_file.split('.')[0]
        ocr_filename = ocr_filename + "_coords.json"
        data_label = concat_ocr(os.path.join(ocr_folder, ocr_filename))
        print(f'Currently at {counter}')
        counter += 1
        for field in fields:
            if field not in data_output[0].tolist():
                continue

            for similarity_type in similarity_types:
                data_output_values = get_values_with_field(data_output, field)
                for output in data_output_values:
                    predicted_value = ''
                    true_value = ''
                    max_ratio = 0
                    for ocr in data_label:
                        ratio = get_similarity(similarity_type, output, ocr, field)
                        if max_ratio < ratio:
                            predicted_value = output
                            true_value = ocr

                        max_ratio = max(max_ratio, ratio)

                    x_0, y_0, x_1, y_1 = get_coords_of_label(os.path.join(ocr_folder, ocr_filename), true_value)
                    page_number = get_page_num(os.path.join(ocr_folder, ocr_filename))
                    output_list.append(
                        [model_output_file, doc, page_number, field, similarity_type, true_value, predicted_value,
                         max_ratio, x_0, y_0,
                         x_1, y_1])
    output_results(output_list)
    print("EMPTY FILES: ", counter_empty, "OUT OF", len(test_data_list))
    print(empty_files)


def main():
    start_time = time.time()
    test_data_df = pd.read_csv(test_data, header=None)
    test_data_list = test_data_df[2].values
    if not os.path.exists(similarity_output_folder):
        os.makedirs(similarity_output_folder)
    calc_similarity(test_data_list)
    return time.time() - start_time


if __name__ == '__main__':
    main()
