import pipeline_settings as settings
import aggregate_result as aggregator, report_generator_doc_level, check_similarity
import generate_tsv_files, split, \
    image_doc_csv_generator as image_doc_generator
import refactor_boxes_and_transcripts
import image_to_coords
import ocr, gen_files, split_pipeline, after_train, after_test


def ocr_in():
    ocr_time = image_to_coords.main()
    print("============================OCR FINISHED============================")
    print(f"============================OCR OUTPUT IS IN {settings.after_ocr_path}============================")
    return {'ocr': ocr_time / 60}


def gen_files_in():
    print("============================CREATING FOLDER STRUCTURE============================")
    settings.create_folders()
    print("============================GENERATING TSV AND ENTITIES FILES============================")
    generate_time = generate_tsv_files.main()
    print("============================FINISHED GENERATING INITIAL TSV AND ENTITIES FILES============================")
    print(
        f"============================FILES, WITHOUT IMAGES CAN BE FOUND IN {settings.model_all_data}============================")
    return {'gen_files': generate_time / 60}


def split_pipeline_in():
    print("============================SPLITTING THE DATASET============================")
    image_doc_time = image_doc_generator.main()
    print("============================IMAGE DOC GENERATOR FINISHED============================")
    split_time = split.main()
    print("============================SPLIT PIPELINE FINISHED============================")
    print("============================READY TO TRAIN THE MODEL============================")
    print(F"============================MODEL INPUT IS IN {settings.model_input_folder}============================")
    return {'image_doc': image_doc_time / 60, 'split': split_time / 60}


def after_train_in():
    refactor_boxes_time = refactor_boxes_and_transcripts.main()
    print("============================REFACTORED BOXES AND TRANSCRIPTS FINISHED============================")
    print("============================READY TO TEST THE MODEL============================")
    print(
        F"============================TEST DATA IS IN {settings.boxes_and_transcripts_for_testing}============================")
    return {'refactor_boxes': refactor_boxes_time / 60}


def after_test_in():
    check_similarity_time = check_similarity.main()
    print("============================CHECK SIMILARITY CSV CREATED============================")
    aggregator_time = aggregator.main()
    print("============================AGGREGATOR FINISHED============================")
    report_generator_doc_level_time = report_generator_doc_level.main()
    print(
        F"============================REPORT DOCUMENT LEVEL GENERATED IS IN {settings.report_document_level_output_file}============================")
    return {'check_similarity': check_similarity_time / 60,
            'aggregator': aggregator_time / 60,
            'report_generator_doc': report_generator_doc_level_time / 60}


if __name__ == '__main__':
    pass
    # Name refactor and pdf2image
    # ocr.main()  # DOES OCR
    # gen_files.main() # GENERATES INITIAL BT AND ENTITIES FILES
    # DocViewer app relabeling
    # split_pipeline.main() # SPLITS INTO VALIDATION AND TRAINING SETS AND PREPARES PICK INPUT
    # Train model
    # after_train.main() # REFACTOR BT FILES FOR VALIDATION SET, MAKE IT A TESTING SET
    # Test model
    # after_test.main() # POSTPROCESS AND GENERATE REPORT
