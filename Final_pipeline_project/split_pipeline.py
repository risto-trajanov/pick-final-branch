import pipeline_run as run
import time
import pipeline_settings as settings


def main():
    start_time = time.time()
    times_dict = run.split_pipeline_in()
    split_time = time.time() - start_time
    split_time = split_time / 60
    print("--- %s minutes ---" % split_time)
    with open(settings.report_time_per_function, "w") as file:
        file.write("FUULL SPLIT PHASE TIME -> %s minutes.\n" % split_time)
        file.write("IMAGE DOC 2 CSV TIME -> %s minutes.\n" % times_dict['image_doc'])
        file.write("SPLIT PHASE TIME -> %s minutes.\n" % times_dict['split'])


if __name__ == "__main__":
    main()
