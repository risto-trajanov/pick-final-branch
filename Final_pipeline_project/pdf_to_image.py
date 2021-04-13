import os
from pdf2image import convert_from_path
import time
import pipeline_settings as settings

poppler_path = settings.poppler_path


def pdf_to_image(pdf_folder_path, out_path):
    """
    This function converts pdf files to jp*g images.
    :param poppler_path: The path where the poppler bin file is located, for example the relative path
    'Release-20.12.1/poppler-20.12.1/bin'.
    :param pdf_folder_path: Folder which contains .pdf files of all documents. The pdf files should be named
    policy_number_POLICY.pdf.
    :param out_path: The path where to create the output folder which will contain subfolders for each pdf file and
    each of the subfolders will contain the images for the pdf.
    :return: None
    """
    # Creating output folder if it doesn't exist
    os.makedirs(out_path, exist_ok=True)

    for file in os.listdir(pdf_folder_path):
        if str(file).endswith(".pdf"):
            # Pdf file, converting to images
            pdf_file = os.path.join(pdf_folder_path, file)
            pdf_base_name = os.path.splitext(os.path.basename(file))[0]
            print(f'Currently processing pdf file: {pdf_base_name}')
            # Creating output subfolder for doc if it doesn't exist
            out_sub_path = os.path.join(out_path, pdf_base_name)
            os.makedirs(out_sub_path, exist_ok=True)
            images = convert_from_path(pdf_path=pdf_file, poppler_path=poppler_path)
            for page_num, image in enumerate(images):
                image_name = pdf_base_name + "_" + f'{page_num + 1:03d}' + ".jpg"
                image.save(os.path.join(out_sub_path, image_name), "JPEG")


if __name__ == "__main__":
    input_path = r'C:\Users\mbogoevs\Output_testing_folder\Documents_Policy'
    output_path = r'C:\Users\mbogoevs\Output_testing_folder\FromPDF'
    start_time = time.time()
    pdf_to_image(input_path, output_path)
    print(f'Elapsed time: {(time.time() - start_time) / 60}s.')
