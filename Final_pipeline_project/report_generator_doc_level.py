import json
import os
import time
from difflib import SequenceMatcher
import pandas as pd
import pipeline_settings as settings

output_folder_path = settings.document_level_aggregated_folder
true_json_folder_path = settings.json_after_ocr
validation_docs = settings.document_valid_samples_list
report_file = settings.report_document_level_output_file


def generate_report(output_folder_path, true_json_folder_path, validation_csv_file_path, report_file):
    validation_docs = validation_csv_file_path
    end_report_string = str()
    set_valid_files = set()
    wanted_labels = settings.fields
    val_docs = list(pd.read_csv(validation_docs)['doc'])
    end_report_string += f"All validation documnet names: \n {'; '.join(val_docs)} \n"
    end_report_string += "====================================================================\n"
    full_matches = 0
    best_matches = 0
    results_found = 0
    results_to_find = 0
    all_guessed = 0

    label_dict = {label: {'precision': 0.0, 'recall': 0.0, 'accuracy': 0.0} for label in wanted_labels}
    measure_dict = {label: {'tp': 0.0, 'tn': 0.0, 'fp': 0.0, 'fn': 0.0} for label in wanted_labels}

    for out_file in os.listdir(output_folder_path):
        file = os.path.splitext(os.path.basename(out_file))[0]
        if file in val_docs:
            end_report_string += f"Comparing validation file : {file} from output with the true json...\n"
            true_json_file = open(os.path.join(true_json_folder_path, file) + ".json", "r", encoding='utf-8').read()
            generated_json_file = open(os.path.join(output_folder_path, file) + ".json", "r", encoding='utf-8').read()
            processed_dict = json.loads(generated_json_file)
            json_file = json.loads(true_json_file)
            end_report_string += "============================================================\n"
            true_num = 0
            for wanted_label in wanted_labels:
                to_find = True
                end_report_string += '\n'
                if json_file[wanted_label] == "" or json_file[wanted_label] == []:
                    end_report_string += f'Label: {wanted_label} with true value: NONE(NOTHING TO BE FOUND)\n'
                    to_find = False
                else:
                    end_report_string += f'Label: {wanted_label} with true value: {json_file[wanted_label]}\n'
                type_list = [ins_type.lower() for ins_type in json_file[wanted_label]]
                if to_find == False:
                    if processed_dict[wanted_label] == '' or processed_dict[wanted_label] == []:  # not found some result
                        end_report_string += f'Label: {wanted_label} with extracted value: NONE(NOTHING TO BE FOUND)\n'
                        end_report_string += "Full match!\n"
                        full_matches += 1
                        true_num += 1
                        measure_dict[wanted_label]['tn'] += 1.0
                    else:
                        end_report_string += f'Label: {wanted_label} with extracted value: ' \
                                             f'{processed_dict[wanted_label]} ...FOUND RESULT BUT SHOULD NOT HAVE\n'
                        measure_dict[wanted_label]['fp'] += 1.0
                    best_matches += 1
                else:
                    results_to_find += 1
                    if processed_dict[wanted_label] != '' and processed_dict[wanted_label] != []:  # found some result
                        if wanted_label not in ['insuranceType', 'insuranceSum', 'fee']:

                            best_item = processed_dict[wanted_label]
                            best_sim = SequenceMatcher(None, json_file[wanted_label].lower(), best_item.lower()).ratio()

                            end_report_string += f'Label: {wanted_label} with extracted value: {best_item}\n'
                            if json_file[wanted_label].lower() == best_item.lower():
                                end_report_string += "Full match!\n"
                                full_matches += 1
                                results_found += 1
                                best_matches += 1
                                true_num += 1
                                measure_dict[wanted_label]['tp'] += 1.0
                            else:
                                if best_sim >= 0.9:  # SET THRESHOLD FOR MATCH
                                    end_report_string += f"String matching similarity: {best_sim} is " \
                                                         f"greater than 0.9 and thus labeled as a full match\n"
                                    full_matches += 1
                                    true_num += 1
                                    measure_dict[wanted_label]['tp'] += 1.0
                                else:
                                    end_report_string += f"String matching similarity is: {best_sim}\n"
                                    measure_dict[wanted_label]['fp'] += 1.0
                                results_found += 1
                                best_matches += 1
                        else:
                            for ins_type in list(set(processed_dict[wanted_label])):
                                if ins_type.lower() in type_list:
                                    end_report_string += f"Insurance type {ins_type} was found!\nFull match!\n"
                                    full_matches += 1
                                    true_num += 1
                                    measure_dict[wanted_label]['tp'] += 1.0
                                else:
                                    sim_dict = {json_file[wanted_label][index]: SequenceMatcher(None,
                                                                                                json_file[wanted_label][
                                                                                                    index].lower(),
                                                                                                ins_type.lower()).ratio()
                                                for index in range(len(json_file[wanted_label]))}
                                    best_sim = \
                                        [item for item in
                                         sorted(sim_dict.items(), key=lambda item: item[1], reverse=True)][
                                            0]
                                    end_report_string += f"Generated insurance type {ins_type} does not exist as a " \
                                                         f"true label, but the max similarity it has is with: {best_sim}\n"
                                    if best_sim[1] >= 0.9:  # SET THRESHOLD
                                        end_report_string += f"Similarity is greater than 0.9 so we classify " \
                                                             f"as a full match!\n"
                                        measure_dict[wanted_label]['tp'] += 1.0
                                        true_num += 1
                                    else:
                                        measure_dict[wanted_label]['fp'] += 1.0
                                best_matches += 1
                                results_found += 1
                    else:  # didn't find result
                        end_report_string += f'Label: {wanted_label} with extracted value: NOTHING FOUND, SHOULD HAVE\n'
                        measure_dict[wanted_label]['fn'] += 1.0
                        best_matches += 1
                end_report_string += '\n'
            end_report_string += "============================================================\n"
            all_sum = len(wanted_labels) + len(json_file['insuranceType']) - 1
            if true_num == all_sum:
                all_guessed += 1

    end_report_string += f"Total full matches: {full_matches} out of {best_matches}\n"
    end_report_string += f"Total results generated : {results_found} out of {results_to_find}\n"
    end_report_string += "============================================================\n"

    end_report_string += "Legend: \n"
    end_report_string += "TP: number of generated labels that have a full match with the true labels or have " \
                         "similarity greater than 0.9. This doesn't count true labels with empty string values\n"
    end_report_string += "TN: number of true labels that are None (empty strings) and their corresponding generated " \
                         "label value is also None(empty string)\n"
    end_report_string += "FP: number of true labels that are either not None and their corresponding generated label " \
                         "value is also not None, but they aren't fully matching (similarity<0.9) OR the true labels " \
                         "are None, but the generated label values are not None(generating results when not needed)\n"
    end_report_string += "FN: number of true labels that are not None, but their corresponding generated label values " \
                         "are None\n"
    end_report_string += "Precision: TP/(TP+FP) : In a way, tells us what fraction of the generated labels which are " \
                         "not None are correct(fully matched)\n"
    end_report_string += "Accuracy: (TP+TN)/(TP+FP+TN+FN): In a way, tells us what fraction of all of the generated " \
                         "labels(both None and not None) are correct(fully matched)\n"
    end_report_string += "Recall: TP/(TP+FN): In a way, tells us what fraction of true labels that are not None are " \
                         "found and are correct(fully matched)\n"
    end_report_string += "Priority(from highest to lowest): recall, precision, accuracy"

    end_report_string += "============================================================\n"
    end_report_string += "Summary for all the labels: \n"

    for wanted_label in wanted_labels:
        end_report_string += "======================================\n"
        tp_label = measure_dict[wanted_label]['tp']
        tn_label = measure_dict[wanted_label]['tn']
        fp_label = measure_dict[wanted_label]['fp']
        fn_label = measure_dict[wanted_label]['fn']
        if tp_label + fp_label != 0:
            label_dict[wanted_label]['precision'] = (tp_label) / (tp_label + fp_label)
        else:
            label_dict[wanted_label]['precision'] = 0

        if tp_label + tn_label + fp_label + fn_label != 0:
            label_dict[wanted_label]['accuracy'] = (tp_label + tn_label) / (tp_label + tn_label + fp_label + fn_label)
        else:
            label_dict[wanted_label]['accuracy'] = 0

        if tp_label + fn_label != 0:
            label_dict[wanted_label]['recall'] = (tp_label) / (tp_label + fn_label)
        else:
            label_dict[wanted_label]['recall'] = 0

        end_report_string += f"Printing information about label: {wanted_label}\n"
        end_report_string += f"TP: {tp_label}\n"
        end_report_string += f"TN: {tn_label}\n"
        end_report_string += f"FP: {fp_label}\n"
        end_report_string += f"FN: {fn_label}\n"
        end_report_string += f"Accuracy : {label_dict[wanted_label]['accuracy']}\n"
        end_report_string += f"Precision : {label_dict[wanted_label]['precision']}\n"
        end_report_string += f"Recall : {label_dict[wanted_label]['recall']}\n"
        end_report_string += "======================================\n"

    end_report_string += f"Number of points for which all of the labels were fully matched: {all_guessed} out of " \
                         f"{len(set_valid_files)}\n"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(end_report_string)
    f.close()


def main():
    start_time = time.time()
    generate_report(output_folder_path, true_json_folder_path, validation_docs, report_file)
    return time.time() - start_time


if __name__ == '__main__':
    main()
