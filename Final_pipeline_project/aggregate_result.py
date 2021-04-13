import pandas as pd
import numpy as np
import os
import json
import pipeline_settings as settings
import time


valid_data_folder = os.path.join(settings.model_input_folder,settings.valid_folder)
valid_data_csv = 'valid_samples_list.csv'
valid_samples_list = settings.valid_samples_list
all_data_label = settings.json_after_ocr
coords_folder = settings.coords_after_ocr
model_output_folder = settings.model_output_folder
similarity_output = settings.similarity_output_file
fields = settings.fields
out_folder = settings.document_level_aggregated_folder
label_doc_level_folder = settings.label_document_level_folder
document_valid_samples = settings.valid_samples_list
document_valid_samples_doc_level = settings.document_valid_samples_list

docs = set()


def valid_csv_to_doc_level():
    df = pd.DataFrame(data=list(set(docs)), columns=['doc'])
    df.to_csv(document_valid_samples_doc_level, index=False)


def initial_json():
    j = {"insuranceCompany": "",
         "insuranceType": [],
         "insuranceSum": [],
         "insurance": [],
         "policyNumber": "",
         "policyEnd": "",
         "fee": []}
    for file in docs:
        filename = os.path.join(out_folder,file + ".json")
        with open(filename, 'w') as outfile:
            json.dump(j, outfile)


def merge_type_sum_to_insurance():
    similarity = pd.read_csv(similarity_output, index_col=False)

    for file in docs:
        ocr_folder = coords_folder

        insurance = []
        sub_df_type = similarity.loc[(similarity['doc'] == file) & (similarity['field'] == 'insuranceType')]
        sub_df_sum = similarity.loc[(similarity['doc'] == file) & (similarity['field'] == 'insuranceSum')]
        sub_df_fee = similarity.loc[(similarity['doc'] == file) & (similarity['field'] == 'fee')]
        sub_df_type = sub_df_type.loc[
            (sub_df_type['ocr'] != '') & (sub_df_type['ocr'] != 'nan') & (sub_df_type['ocr'] != 0)]
        sub_df_sum = sub_df_sum.loc[(sub_df_sum['ocr'] != '') & (sub_df_sum['ocr'] != 'nan') & (sub_df_sum['ocr'] != 0)]
        sub_df_fee = sub_df_fee.loc[(sub_df_fee['ocr'] != '') & (sub_df_fee['ocr'] != 'nan') & (sub_df_fee['ocr'] != 0)]
        pages = list(set(sub_df_type['file']))
        if not sub_df_type.empty:
            for index, row in sub_df_type.iterrows():
                ocr_type = row['ocr']
                page_type = row['page']
                found_type = False
                found_sum = False
                found_fee = False
                for page in pages:
                    page = page.split('.')[:-1]
                    page = '_'.join(page)
                    page = page + '_coords.json'
                    with open(ocr_folder + page) as json_file:
                        ocr_json = json.load(json_file)
                    for elem in ocr_json:
                        if found_sum and found_fee:
                            found_type = False
                            found_sum = False
                            found_fee = False
                            break
                        page = elem['page']
                        text = elem['text']
                        if int(page) < int(page_type):
                            break
                        if ocr_type in str(text) or found_type:
                            found_type = True
                            if not sub_df_sum.empty:
                                for index, row in sub_df_sum.iterrows():
                                    ocr_sum = row['ocr']
                                    if ocr_sum in str(text):
                                        doc_label = out_folder + file + '.json'
                                        with open(doc_label) as json_file:
                                            doc_data = json.load(json_file)
                                        insurance_doc = doc_data['insurance']
                                        if not any(ins['insuranceType'] == ocr_type for ins in insurance_doc):
                                            type_sum = {'insuranceType': ocr_type, 'insuranceSum': ocr_sum, 'fee': ''}
                                            insurance_doc.append(type_sum)
                                        else:
                                            type_sum = next(item for item in insurance_doc if item["insuranceType"] == ocr_type)
                                            type_sum['insuranceSum'] = ocr_sum

                                        doc_data['insurance'] = insurance_doc
                                        with open(doc_label, 'w') as outfile:
                                            json.dump(doc_data, outfile)
                                        insurance.append(type_sum)
                                        found_sum = True
                                        sub_df_sum = sub_df_sum.drop(index)
                                        break
                            if not sub_df_fee.empty:
                                for index, row in sub_df_fee.iterrows():
                                    ocr_fee = row['ocr']
                                    if ocr_fee in str(text):
                                        doc_label = out_folder + file + '.json'
                                        with open(doc_label) as json_file:
                                            doc_data = json.load(json_file)
                                        insurance_doc = doc_data['insurance']
                                        if not any(ins['insuranceType'] == ocr_type for ins in insurance_doc):
                                            type_sum = {'insuranceType': ocr_type, 'insuranceSum': '', 'fee': ocr_fee}
                                            insurance_doc.append(type_sum)
                                        else:
                                            type_sum = next(item for item in insurance_doc if item["insuranceType"] == ocr_type)
                                            type_sum['fee'] = ocr_fee

                                        doc_data['insurance'] = insurance_doc
                                        with open(doc_label, 'w') as outfile:
                                            json.dump(doc_data, outfile)
                                        insurance.append(type_sum)
                                        found_fee = True
                                        sub_df_fee = sub_df_fee.drop(index)
                                        break


def get_documents():
    test_data_df = pd.read_csv(document_valid_samples, header=None)
    test_data_list = test_data_df[2].values
    for test_data_pic in test_data_list:
        split = test_data_pic.split('.')[0].split('_')[:-1]
        index_policy = split.index("POLICY")
        doc = '_'.join(split[:index_policy + 1])
        docs.add(doc)


def aggregate_pages(similarity):
    for file in docs:
        filename = out_folder + file + ".json"
        with open(filename) as json_file:
            doc_json = json.load(json_file)
        for field in fields:
            sub_df = similarity.loc[(similarity['doc'] == file) & (similarity['field'] == field)]
            sub_df = sub_df.loc[(sub_df['ocr'] != '') & (sub_df['ocr'] != 'nan') & (sub_df['ocr'] != 0)]
            if not sub_df.empty:
                value_series = list(sub_df['value'])
                indices = list(np.argwhere(value_series == np.amax(value_series)).reshape(1, -1)[0])
                max_values = list(sub_df['ocr'].iloc[indices].values)
                final_field = max(set(max_values), key=max_values.count)
                if field in ['insuranceType', 'insuranceSum', 'fee']:
                    types = doc_json[field]
                    for ins_type in set(max_values):
                        types.append(str(ins_type))
                    doc_json[field] = types
                else:
                    doc_json[field] = final_field
        with open(filename, 'w') as outfile:
            json.dump(doc_json, outfile, indent=4)


def main():
    start_time = time.time()
    if not os.path.isdir(out_folder):
        os.mkdir(out_folder)

    get_documents()
    initial_json()
    similarity = pd.read_csv(similarity_output)
    valid_csv_to_doc_level()
    merge_type_sum_to_insurance()
    aggregate_pages(similarity)
    return time.time() - start_time


if __name__ == '__main__':
    main()
