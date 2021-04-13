import glob
import json
import os
import logging.config
import ocr_coordinates
import pipeline_settings as settings
import time

input_dir = settings.pre_ocr_all_images
output_dir = settings.after_ocr_path


class ImageToCoords:
    def __init__(self, directory, files, output_directory):
        self.directory = directory
        self.files = files
        self.output_path = output_directory

    def start(self):
        """
        This function expects the input dir to contain images where each image is in the name format:
        {policyNum}_POLICY_{pageNum}.jp*g. Will create OCR files for each image and set the page number
        correspondingly.
        :return:
        """

        if isinstance(self.files, str):
            f = [self.files]
            self.files = f
        amount_of_files = len(self.files)
        logger = logging.getLogger(__name__)
        for x, input_file in enumerate(self.files):
            print(f'Currently processing file: {input_file}')
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            pre_page = "_".join(base_name.split("_")[:-1])
            page_num = int(base_name.split("_")[-1])
            if x % 10 == 0:
                logger.debug('Converting pdf ' + str(x) + ' out of ' + str(amount_of_files))
            output_file = self.output_path + "/" + pre_page + f'_{int(page_num):03d}' + '_coords.json'
            coords = ocr_coordinates.get_coords_one_file(input_file, page_num)
            with open(output_file, "w") as f:
                json.dump(coords, f, indent=4)


def main():
    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(input_dir + "/*.jp*g")
    app = ImageToCoords(files=files, directory=input_dir, output_directory=output_dir)
    app.start()
    return time.time() - start_time


if __name__ == '__main__':
    main()
