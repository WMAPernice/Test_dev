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


def shuffle_zip(input_path: str, output_path: str, ready_path: str, val=False):
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
    dataset_name = extract_ds_name(input_path)
    print("working on ", dataset_name)

    temp_dir = 'TEMP_UNZIP'  # Path definition, also for later use
    temp_ds_path = temp_dir + '/' + dataset_name
    # unzips files into temp folder
    if os.path.exists(temp_dir):
        raise ValueError('temp folder already exists in directory; consider deleting and re-run')
    else:
        os.makedirs(temp_dir)

    zip_ref = zipfile.ZipFile(input_path, 'r')
    zip_ref.extractall(temp_dir)
    zip_ref.close()

    # shuffle images and zip
    test_addrs, train_addrs = shuffle_images(temp_ds_path)

    # zip shuffled images and store at output_path
    zipup(output_path, test_addrs, train_addrs, dataset_name, temp_ds_path)

    shutil.rmtree(temp_dir)

    ready_data(dataset_name, output_path, ready_path)


def shuffle_images(temp_path, shuffle_data=True, val=False):
    random.seed(1)  # reproducible randomness

    # get list of files in TempPath
    addrs = os.listdir(temp_path)  # e.g. mmr1_WP_E1_S2_F1_I6_C10_A0.tifstack.tif

    # create shuffled list
    if shuffle_data:
        addrs = random.sample(addrs, k=len(addrs))  # creates shuffled list by random sampling from original list.

    """
    Question: 
    Generating train, test and optionally val datasets - Question: should there be the same absolute number of test/val 
    images for each class or should the number vary depending on total number of images per class e.g. 
    20 test images for a total of 100 class A images, but 40 for a total of 200 class B images?   

    """

    # # Divide the hata into 60% train, 20% test, and optionally 20% val
    # train_addrs = addrs[0:int(0.8*len(addrs))]
    # test_addrs = addrs[int(0.8*len(addrs)):]
    # # val_addrs = addrs[int(0.6*len(addrs)):int(0.8*len(addrs))]

    # Select == 35 images for test and optionally val datasets; put the rest into train
    test_addrs = addrs[0:35]
    train_addrs = addrs[35:]

    print(str(len(train_addrs)) + ' images assigned to train')
    print(str(len(test_addrs)) + ' images assigned to test')

    return test_addrs, train_addrs


def zipup(save_path, test_addrs, train_addrs, dataset_name, temp_path, verbose=False, val_addrs=None):
    # Creating .zip file of train, test and potentially validation images.

    # make subdirectory to store suffled zip files
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # processing train images:
    if verbose:
        print('Following files will be zipped:')
        for addrs in train_addrs:
            print(addrs)

    # writing files to a zipfile
    with ZipFile(save_path + dataset_name + '_train_data.zip', 'w') as zip:
        # writing each file one by one
        for addrs in train_addrs:
            zip.write(temp_path + '/' + addrs, basename(addrs))

        print('All training images zipped successfully!')

    ### processing Test images: ###
    if verbose:
        print('Following files will be zipped:')
        for addrs in test_addrs:
            print(addrs)

    # writing files to a zipfile
    with ZipFile(save_path + dataset_name + '_test_data.zip', 'w') as zip:
        # writing each file one by one
        for addrs in test_addrs:
            zip.write(temp_path + '/' + addrs, basename(addrs))

        print('All test images zipped successfully!')

    #     zip_ref.close()

    print('Files moved to:' + save_path)


def ready_data(dataset_name: str, input_path, output_path, data_struct=['train', 'test']):
    # To be used with shuffled data in zip files.
    # Extracts these to specified dataset folder in train/test subfolders
    ### OPTIONS ###

    # choose path where target zip-files are stored
    ZPath = input_path

    # define path for files to be unzipped and stored in train and test directories
    output_path = output_path

    # optionally add 'val' keyword if datasets (zip files) have been created accordingly
    data_struct = data_struct

    ### Execution --------------------------------------------------------------------------------###

    # unzips files correct folders or creates them

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


def extract_ds_name(input_path: str) -> str:
    path = input_path.split('.zip')
    dataset_name = path[-2].split('/')[-1]
    return dataset_name


def delete_non_square(paths: List[Path], size=200):
    deleted = 0
    for path in paths:
        image = tiff.imread(str(path))
        shape = image.shape
        if shape[-1] != size or shape[-2] != size:
            os.remove(str(path))
            deleted += 1
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
