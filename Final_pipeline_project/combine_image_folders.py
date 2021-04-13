import os
import shutil
import time


def combine_folders(folder_path, out_path):
    """
    This function copies images from subfolders in the folder_path path into the out_path folder (flattens).
    :param folder_path: Folder containing document subfolders each containing images
    :param out_path: Folder where the images are to be copied to
    :return:
    """
    os.makedirs(out_path, exist_ok=True)
    for folder in os.listdir(folder_path):
        subfolder = os.path.join(folder_path, folder)
        for image in os.listdir(subfolder):
            image_path = os.path.join(subfolder, image)
            image_new_path = os.path.join(out_path, image)
            shutil.copy(image_path, image_new_path)


if __name__ == "__main__":
    folder_path = r'C:\Users\mbogoevs\Output_testing_folder\FromPDF'
    out_path = r'C:\Users\mbogoevs\Output_testing_folder\Flattened_2'
    start_time = time.time()
    combine_folders(folder_path, out_path)
    print(f'Elapsed time: {(time.time() - start_time) / 60}s.')
