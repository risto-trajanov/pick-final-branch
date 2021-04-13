import pandas as pd
import os
import time
import json
import pipeline_settings as settings

images = settings.images_after_ocr
output_file_name = settings.image_doc_csv
json_dir = settings.json_after_ocr
fields = settings.fields
keep_docs = set()


def output_results(output_list):
    similarity_output_df = pd.DataFrame(output_list, columns=['file', 'doc'])
    similarity_output_df.to_csv(output_file_name)


def filter_images():
    for json_file in os.listdir(json_dir):
        json_path = os.path.join(json_dir, json_file)
        doc_name = os.path.splitext(os.path.basename(json_file))[0]
        # UNCOMMENT 25-41 FOR FILTER

        with open(json_path, "r") as f:
            data = json.load(f)

        passed = True

        for field in fields:
            if field not in data or data[field] == "" or (
                    field in ["insuranceType", "insuranceSum", "fee"]
                    and len(data[field]) == 0):
                passed = False
                break

        if not passed:
            # Skip if at least one is empty/missing
            print(f'Skipping doc: {doc_name} because it doesn\'t include all fields')
            continue
        keep_docs.add(doc_name)


def main():
    start_time = time.time()
    image_files = os.listdir(images)
    output_list = []

    filter_images()

    for image in image_files:
        splited = image.split('.')[:-1]
        image_name = '.'.join(splited)
        doc_name = image_name.split('_')[:-1]
        index_policy = doc_name.index("POLICY")
        doc = '_'.join(doc_name[:index_policy + 1])
        if doc in keep_docs:
            output_list.append([image_name, doc])

    output_results(output_list)
    return time.time() - start_time


if __name__ == '__main__':
    main()
