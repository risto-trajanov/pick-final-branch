import csv
import os
import time
import pipeline_settings as settings

path = settings.model_input_boxes_and_transcripts
out_path = settings.boxes_and_transcripts_for_testing


def main():
    start_time = time.time()
    for file in os.listdir(path):
        file_full = os.path.join(path, file)
        tsv_file = open(file_full, "r", encoding='utf-8')
        read_tsv = csv.reader(tsv_file, delimiter=",")
        new_file = []
        for row in read_tsv:
            new_row = ','.join(row[:-1]) + "\n"
            new_file.append(new_row)
        write_file = os.path.join(out_path, file)
        with open(write_file, "w", encoding='utf-8') as f:
            f.writelines(new_file)

    return time.time() - start_time


if __name__ == '__main__':
    main()
