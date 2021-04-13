import pipeline_run as run
import time
import pipeline_settings as settings


def main():
    start_time = time.time()
    times_dict = run.gen_files_in()
    gen_files_time = time.time() - start_time
    gen_files_time = gen_files_time / 60
    print("--- %s minutes ---" % gen_files_time)
    with open(settings.report_time_per_function, "w") as file:
        file.write("GEN FILES PHASE TIME -> %s minutes.\n" % gen_files_time)
        file.write("GEN FILES TIME -> %s minutes. \n" % times_dict['gen_files'])


if __name__ == "__main__":
    main()
