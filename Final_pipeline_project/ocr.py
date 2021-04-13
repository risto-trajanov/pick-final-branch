import pipeline_run as run
import time
import pipeline_settings as settings


def main():
    start_time = time.time()
    times_dict = run.ocr_in()
    ocr_time = time.time() - start_time
    ocr_time = ocr_time / 60
    print("--- %s minutes ---" % ocr_time)
    with open(settings.report_time_per_function, "w") as file:
        file.write("OCR PHASE TIME -> %s minutes.\n" % ocr_time)
        file.write("OCR FUNCTION TIME -> %s minutes.\n" % times_dict['ocr'])


if __name__ == "__main__":
    main()
