import pipeline_run as run
import time
import pipeline_settings as settings


def main():
    start_time = time.time()
    times_dict = run.after_train_in()
    after_train_time = time.time() - start_time
    after_train_time = after_train_time / 60
    print("--- %s minutes ---" % after_train_time)
    with open(settings.report_time_per_function, "w") as file:
        file.write("AFTER TRAIN PHASE TIME -> %s minutes.\n" % after_train_time)
        file.write("REFACTOR BOXES PHASE TIME -> %s minutes.\n" % times_dict['refactor_boxes'])


if __name__ == "__main__":
    main()
