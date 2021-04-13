import glob
import os
import traceback
from shutil import copyfile
import cv2
import pandas as pd
import time
from sklearn.model_selection import StratifiedShuffleSplit
import pipeline_settings as settings

image_doc_csv = settings.image_doc_csv
doc_bin_csv = settings.doc_bin_csv
bt_path = os.path.join(settings.model_all_data, "boxes_and_transcripts")
entities_path = os.path.join(settings.model_all_data, "entities")
images_path = settings.images_after_ocr
valid_size = settings.validation_size
out_path = settings.model_input_folder
val_datasets = []


def copy_file(src, dest):
    copyfile(src, dest)


def save_image(image_file, folder_path):
    image = cv2.imread(image_file, 1)
    image_path_name = os.path.splitext(os.path.basename(image_file))
    image_full_name = image_path_name[0] + ".jpg"
    path = os.path.join(folder_path, image_full_name)
    cv2.imwrite(path, image)


def validation_split_by_doc(rand_state, test_size=0.2):
    df_count_doc = pd.read_csv(doc_bin_csv)
    df_image_doc = pd.read_csv(image_doc_csv)
    X = df_count_doc['doc']
    y = df_count_doc['bin'].astype(str)
    success = True

    sss_test = StratifiedShuffleSplit(n_splits=3, test_size=test_size, random_state=rand_state)
    for train_index, test_index in sss_test.split(X, y):
        X_train, X_test = X[train_index], X[test_index]

    X_test_values = X_test.values
    if not val_datasets:
        val_datasets.append(set(X_test_values))

    else:
        for val in val_datasets:
            overlap = len(val.intersection(set(X_test_values)))
            if overlap > 0.4 * len(X_test_values):
                success = False

        if success:
            print(X_test_values)
            val_datasets.append(set(X_test_values))

    training_images = df_image_doc[df_image_doc['doc'].isin(X_train.tolist())]['file'].tolist()
    validation_images = df_image_doc[df_image_doc['doc'].isin(X_test.tolist())]['file'].tolist()

    return training_images, validation_images, success


def split_sets(bt_path, entities_path, images_path, valid_size, out_path):
    define_bins()
    rand_state = 0
    output_csv_file_train = os.path.join(out_path, "Train/train_samples_list.csv")
    output_csv_file_valid = os.path.join(out_path, "Valid/valid_samples_list.csv")
    boxes_and_transcripts_folder_train = os.path.join(out_path + "/Train", "boxes_and_transcripts")
    boxes_and_transcripts_folder_valid = os.path.join(out_path + "/Valid", "boxes_and_transcripts")
    images_folder_train = os.path.join(out_path + "/Train", "images")
    images_folder_valid = os.path.join(out_path + "/Valid", "images")
    entities_folder_train = os.path.join(out_path, "Train/entities")
    entities_folder_valid = os.path.join(out_path, "Valid/entities")
    os.makedirs(boxes_and_transcripts_folder_train, exist_ok=True)
    os.makedirs(boxes_and_transcripts_folder_valid, exist_ok=True)
    os.makedirs(images_folder_train, exist_ok=True)
    os.makedirs(images_folder_valid, exist_ok=True)
    os.makedirs(entities_folder_train, exist_ok=True)
    os.makedirs(entities_folder_valid, exist_ok=True)

    # Shuffling the dataset and defining slices for train,valid,test
    image_files = glob.glob(images_path + "/*.jp*g")

    training_images, validation_images, success = validation_split_by_doc(rand_state, test_size=valid_size)
    if success:
        ffnum_train = 0  # for index
        ffnum_valid = 0
        with open(output_csv_file_train, "w", encoding="utf-8") as train_csv:
            with open(output_csv_file_valid, "w", encoding="utf-8") as valid_csv:
                try:
                    for image_file in image_files:
                        image_path_name = os.path.splitext(os.path.basename(image_file))
                        image_base_name = image_path_name[0]

                        if image_base_name in training_images:
                            train_csv.write("%d,%s,%s\n" % (ffnum_train, "invoice", image_base_name))
                            print(f'Processing image: {image_file} and labeling as training.')
                            ffnum_train += 1
                            # Write the csv file
                        elif image_base_name in validation_images:
                            valid_csv.write("%d,%s,%s\n" % (ffnum_valid, "invoice", image_base_name))
                            print(f'Processing image: {image_file} and labeling as validation.')
                            ffnum_valid += 1

                        # Saving image in train and valid folders
                        save_image(image_file, images_folder_train)
                        save_image(image_file, images_folder_valid)

                        # Save bt file in train and valid folders
                        boxes_and_transcripts_path_train = os.path.join(boxes_and_transcripts_folder_train,
                                                                        image_base_name + ".tsv")
                        boxes_and_transcripts_path_valid = os.path.join(boxes_and_transcripts_folder_valid,
                                                                        image_base_name + ".tsv")
                        true_bt_path = os.path.join(bt_path, image_base_name + ".tsv")
                        copyfile(true_bt_path, boxes_and_transcripts_path_train)
                        copyfile(true_bt_path, boxes_and_transcripts_path_valid)

                        # Save entities file in train and valid folders
                        entities_path_train = os.path.join(entities_folder_train, image_base_name + ".txt")
                        entities_path_valid = os.path.join(entities_folder_valid, image_base_name + ".txt")
                        true_ent_path = os.path.join(entities_path, image_base_name + ".txt")
                        copyfile(true_ent_path, entities_path_train)
                        copyfile(true_ent_path, entities_path_valid)
                except Exception as e:
                    print("Exception")
                    print(e)
                    traceback.print_tb(e.__traceback__)


def define_bins():
    df = pd.read_csv(image_doc_csv)
    df['count'] = df.groupby('doc')['doc'].transform('count')
    df_count_doc = df[['doc', 'count']].drop_duplicates(subset=['doc'])
    df_count_doc.index = range(len(df_count_doc.index))
    df_count_doc['bin'] = pd.concat([pd.cut(df_count_doc['count'], 3, labels=["small", "medium", "big"])])
    df_count_doc.to_csv(doc_bin_csv)


def main():
    start_time = time.time()
    split_sets(bt_path, entities_path, images_path, valid_size, out_path)
    return time.time()-start_time


if __name__ == "__main__":
    main()
