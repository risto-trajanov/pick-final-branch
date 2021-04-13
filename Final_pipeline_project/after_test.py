import pipeline_run as run
import pipeline_settings as settings
import time


def main():
    start_time = time.time()
    times_dict = run.after_test_in()
    after_test_time = time.time() - start_time
    after_test_time = after_test_time / 60
    print("--- %s minutes ---" % after_test_time)
    with open(settings.report_time_per_function, "w") as file:
        file.write("AFTER TEST PHASE TIME -> %s minutes.\n" % after_test_time)
        file.write("CHECK SIMILARITY PHASE TIME -> %s minutes.\n" % times_dict['check_similarity'])
        file.write("AGGREGATOR PHASE TIME -> %s minutes.\n" % times_dict['aggregator'])
        file.write("REPORT DOCUMENT LEVEL PHASE TIME -> %s minutes.\n" % times_dict['report_generator_doc'])


if __name__ == "__main__":
    main()
