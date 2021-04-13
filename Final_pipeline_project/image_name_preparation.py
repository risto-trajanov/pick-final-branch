import os
import re
import time


def rename_subfolder(subfolder, doc_name):
    # Renaming the images
    for image_name in os.listdir(subfolder):
        page_num = os.path.splitext(os.path.basename(image_name))[0].split("_")[-1]
        image_name = os.path.join(subfolder, image_name)
        image_new_name = doc_name + "_" + f'{int(page_num):03d}' + ".jpg"
        image_new_name = os.path.join(subfolder, image_new_name)
        print(f'Old name {image_name}')
        print(f'New name {image_new_name}')
        if image_name == image_new_name:
            continue
        os.rename(image_name, image_new_name)


def prepare_names(image_path):
    """
    Transforms image names to be compatabile for the pipeline
    :param image_path: The absolute/relative folder path of the images folder. The folder should contain document
    subfolders, where each of the subfolders contains the images for the document. The subfolders should be named
    in the format '{policyNumber}_POLICY' with the images in it in format ..._{page}.jp*g.
    :return: None
    """
    for file in os.listdir(image_path):
        # Check if the json file exists using the folder name
        print(f'Currently processing folder: {file}.')
        if not str(file).__contains__("_POLICY"):
            print("Folder name not as expected. Skipping...")
        policy_num = file.split("_POLICY")[0]
        # Making the doc name
        doc_name = '_'.join(re.split('\W+', str(policy_num))) + "_POLICY"
        subfolder = os.path.join(image_path, file)
        rename_subfolder(subfolder, doc_name)


if __name__ == "__main__":
    input_path = r'C:\Users\mbogoevs\Output_testing_folder\FromPDF'
    start_time = time.time()
    prepare_names(input_path)
    print(f'Elapsed time: {(time.time() - start_time) / 60}s.')
