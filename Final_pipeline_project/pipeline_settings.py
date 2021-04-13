import os

# ID OF TRY
ID = 1

# VALIDATION SIZE
validation_size = 0.2  # change for split.py

# ROOT
root_folder = f'data/try_no_{ID}'

# FOLDERS
# FOLDERS AND FILES OF DATA AFTER OCR PIPELINE
after_ocr_folder = r"/home/nca/Projects/vzd/FINAL_DATA_RENAMED/"  # CHANGE THIS <============
images_after_ocr = os.path.join(after_ocr_folder, 'images')
json_after_ocr = os.path.join(after_ocr_folder, 'json')
coords_after_ocr = os.path.join(after_ocr_folder, 'coords')

# UTILITY FOLDER/
valid_folder = 'Valid'
boxes_and_transcripts_folder = 'boxes_and_transcripts'
helper_csv_folder = 'helper_csv_files'
boxes_and_transcripts_for_testing_folder = 'boxes_and_transcripts_for_testing'

# MODEL ALL INPUT DATA (NO SPLIT)
model_all_data = 'initial_bt_ent'  # Change this path to specify where you want
# to generate the initial boxes and transcripts and entities files

# MODEL INPUT FOLDER
model_input_folder = 'model_input'

# MODEL OUTPUT FOLDER
model_output_folder = 'model_output'

# REPORT FILES/FOLDERS
report_output_folder = 'report_output'

# SIMILARITY FILES/FOLDERS
similarity_output_folder = 'similarity_output'

# AGGREGATION FOLDERS
document_level_aggregated_folder = 'document_level_output_aggregated'
label_document_level_folder = 'label_document_level_aggregated'

# TESTING
boxes_and_transcripts_for_testing = boxes_and_transcripts_for_testing_folder

# ADD FOLDERS TO ROOT FOLDER
helper_csv_folder = os.path.join(root_folder, helper_csv_folder)
model_input_folder = os.path.join(root_folder, model_input_folder)
model_output_folder = os.path.join(root_folder, model_output_folder)
document_level_aggregated_folder = os.path.join(root_folder, document_level_aggregated_folder)
label_document_level_folder = os.path.join(root_folder, label_document_level_folder)
similarity_output_folder = os.path.join(root_folder, similarity_output_folder)
report_output_folder = os.path.join(root_folder, report_output_folder)
boxes_and_transcripts_for_testing = os.path.join(root_folder, boxes_and_transcripts_for_testing)

# FIELDS
fields = ["insuranceCompany", "policyNumber", "policyEnd", "insuranceType", "fee", "insuranceSum"]

# UTILITY FOLDERS/FILES

image_doc_csv = os.path.join(helper_csv_folder, 'image_doc.csv')
doc_bin_csv = os.path.join(helper_csv_folder, 'doc_bin.csv')

# MODEL INPUT SAMPLES
valid_samples_list = os.path.join(model_input_folder, valid_folder) + '/valid_samples_list.csv'
document_valid_samples_list = os.path.join(model_input_folder, valid_folder) + '/valid_samples_list_doc.csv'
model_input_boxes_and_transcripts = os.path.join(os.path.join(model_input_folder, valid_folder),
                                                 boxes_and_transcripts_folder)

# SIMILARITY FILE
similarity_output_file = similarity_output_folder + '/similarity_output.csv'

# REPORT FILE
report_document_level_output_file = report_output_folder + "/report_document_level.txt"
report_time_per_function = report_output_folder + 'report_time.txt'

# POPPLER PATH
poppler_path = r'C:\Users\mbogoevs\Release-20.12.1\poppler-20.12.1\bin'  # Change for pdf_to_image.py script

# OCR
pre_ocr_all_images = r'C:\Users\mbogoevs\Output_testing_folder\Collected_data_renamed\images'  # Change for image_to_coords.py script(ocr)
after_ocr_path = r'C:\Users\mbogoevs\Output_testing_folder\OCRd_3'  # Change for image_to_coords.py script(ocr)


def create_folders():
    os.makedirs(root_folder, exist_ok=True)
    os.makedirs(helper_csv_folder, exist_ok=True)
    os.makedirs(model_input_folder, exist_ok=True)
    os.makedirs(model_output_folder, exist_ok=True)
    os.makedirs(document_level_aggregated_folder, exist_ok=True)
    os.makedirs(label_document_level_folder, exist_ok=True)
    os.makedirs(similarity_output_folder, exist_ok=True)
    os.makedirs(report_output_folder, exist_ok=True)
    os.makedirs(boxes_and_transcripts_for_testing, exist_ok=True)

    file = open(report_time_per_function, "w")
    file.write("Generated report for time spent per function\n")
    file.close()


if __name__ == '__main__':
    create_folders()
