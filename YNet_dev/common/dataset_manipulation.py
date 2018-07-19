import os
import random
import shutil
import zipfile
from os.path import \
    basename  # required to use in zipfile.Zipfile.write(file, basename(file)) to avoid completed path to be archived
from pathlib import Path
from skimage.external import tifffile as tiff
from typing import List
from zipfile import ZipFile


def shuffle_zip(zips_path: str, output_path: str, ready_path: str, val=False):
    """
    Function to unzip, shuffle, re-zip and store a set of images at a specified location.
    Arguments:
    Dataset_name: name of the dataset, e.g. WT_175 - should be descriptive
    input_path: path to input .zip file
    output_path: path for shuffled .zip-file to be stored
    -> creates temp folder in same directory as .zip file to store unzipped files in, but deletes it once done.
    -> shuffles and splits unzipped files between train, test and optionally val datasets.
    -> optionally re-zip or storage in hdf5 object (TODO)
    """
    temp_dir = 'TEMP_UNZIP'  # Path definition, also for later use
    nclasses = 0
    if os.path.exists(temp_dir):
        raise ValueError('temp folder already exists in directory; consider deleting and re-run')
    else:
        os.makedirs(temp_dir)

    zips_path = Path(zips_path)
    for class_dir in zips_path.iterdir():

        dataset_name = extract_ds_name(class_dir)
        print(f"working on [{dataset_name}] class")

        temp_ds_path = temp_dir + '/' + dataset_name
        # unzips files into temp folder


        zip_ref = zipfile.ZipFile(class_dir, 'r')
        zip_ref.extractall(temp_ds_path)
        zip_ref.close()

        test_addrs, train_addrs = split_images(temp_ds_path)

        # zip shuffled images and store at output_path
        zipup(output_path, test_addrs, train_addrs, dataset_name, class_dir)

        ready_data(dataset_name, output_path, ready_path)

        shutil.rmtree(temp_dir)



def split_images(temp_path, shuffle_data=True):
    if not isinstance(temp_path, Path): temp_path = Path(temp_path)
    random.seed(1)  # reproducible randomness
    ntest = 35 # per experiment per class

    # get list of files in TempPath
    addrs = [addr for addr in temp_path.iterdir()]  # e.g. /mmr1/mmr1_WP_E1_S2_F1_I6_C10_A0.tifstack.tif
    # create shuffled list
    if shuffle_data:
        addrs = random.sample(addrs, k=len(addrs))  # creates shuffled list by random sampling from original list.

    is_exp1 = [True if "E1" in str(addr) else False for addr in addrs]
    test, train = [], []
    sampling = set(is_exp1)
    print(sampling)
    print(is_exp1.count(True), is_exp1.count(False))
    for i in range(ntest):
        for condition in sampling:
            idx = is_exp1.index(condition)
            test.append(addrs[idx])
            del addrs[idx]
            del is_exp1[idx]

    print(f"length of train: [{len(addrs)}]; length of test: [{len(test)}]")
    return test, addrs


def zipup(save_path, test_addrs, train_addrs, dataset_name, temp_path, verbose=False, val_addrs=None):
    # Creating .zip file of train, test and potentially validation images.

    # make subdirectory to store suffled zip files
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # writing files to a zipfile
    with ZipFile(save_path + dataset_name + '_train_data.zip', 'w') as zip:
        # writing each file one by one
        for addrs in train_addrs:
            zip.write(addrs, basename(addrs))

    # writing files to a zipfile
    with ZipFile(save_path + dataset_name + '_test_data.zip', 'w') as zip:
        # writing each file one by one
        for addrs in test_addrs:
            zip.write(addrs, basename(addrs))

    #     zip_ref.close()

    print('Files moved to:' + save_path)


def ready_data(dataset_name: str, input_path, output_path, data_struct=['train', 'test']):
    # To be used with shuffled data in zip files.
    # Extracts these to specified dataset folder in train/test subfolders
    ### OPTIONS ###

    # choose path where target zip-files are stored
    ZPath = input_path

    for i in data_struct:

        if not os.path.exists(output_path + '/' + i):
            os.makedirs(output_path + '/' + i)
            print(i + ' created')
            if not os.path.exists(output_path + '/' + i + dataset_name):
                os.makedirs(output_path + '/' + i + '/' + dataset_name)
                print(i + '/' + dataset_name + ' created')
            else:
                raise ValueError(
                    'WARNING:' + i + '/' + dataset_name + ' exists already - process cancelled to avoid overwriting')

        zip_ref = zipfile.ZipFile(ZPath + '/' + dataset_name + '_' + i + '_data.zip', 'r')
        zip_ref.extractall(output_path + '/' + i + '/' + dataset_name)
        zip_ref.close()


def extract_ds_name(input_path: Path) -> str:
    dataset_name = Path(input_path).name
    dataset_name = dataset_name.replace(".zip", "")
    return dataset_name


def delete_non_square(paths: List[Path], size=200):
    deleted = 0
    for path in paths:
        image = tiff.imread(str(path))
        shape = image.shape
        if shape[-1] != size or shape[-2] != size:
            os.remove(str(path))
            deleted += 1
            paths.remove(path)

    print(f"deleted {deleted} non square images.")


def get_files(root_path: Path, files=[]) -> list:
    for item in root_path.iterdir():
        if item.is_dir():
            df = get_files(item)
            files.extend(df)
        elif item.is_file() and '.DS_Store' not in str(item):
            # check if image is square

            files.append(item)
    return list(set(files))