import pickle, os
import numpy as np
from pathlib import Path
import skimage.external.tifffile as tiff
from resources.conv_learner import *
from typing import Union, List


def dataset_source(source:  Path) -> tuple:
    test_dirs , train_dirs = [], []

    for ds_dir in [source / "train", source / "test"]:
        if 'DS_Store' not in str(ds_dir):
            for class_dir in ds_dir.iterdir():
                if 'DS_Store' not in str(class_dir):
                    if 'test' in str(class_dir): test_dirs.append(class_dir)
                    elif 'train' in str(class_dir): train_dirs.append(class_dir)
    return test_dirs, train_dirs

class Statistics:

    @staticmethod
    def source_class(root_path: Path):
        classes = {}
        for ds in root_path.iterdir(): # train, test, val
            if any(sub in str(ds) for sub in ['test', 'train', 'val']):
                classes[ds.name] = [dir_ for dir_ in ds.iterdir()]
        return classes

    @staticmethod
    def per_class(zipped: zip, norm_value=65536, save_name='') -> dict:
        stats = {}

        for t in zipped:
            for class_dir in t: # t is a tuple
                class_name = class_dir.name
                class_images = []
                # read from each dir and append to the images
                for file in class_dir.iterdir():
                    image = tiff.imread(str(file))
                    class_images.append(image)

                print(f"working on: {class_name}")
                mean = np.mean(class_images, axis=(0, 2, 3)) / norm_value
                stdev = np.std(class_images, axis=(0, 2, 3)) / norm_value

                stats[class_name] = (mean, stdev)

        if save_name:
            Statistics.pickle(stats, save_name+".per_class.dict")  # if save is given it should be a string; empty strings are false

        return stats

    @staticmethod
    def pickle(stats, name="stats.dict") -> None:
        with open(name, 'wb') as file:
            pickle.dump(stats, file)

    @staticmethod
    def per_dataset(test_dirs:[Path], train_dirs:[Path], norm_value=65536, save_name='') -> tuple:

        _dirs = [*test_dirs, *train_dirs]
        print(len(_dirs))
        images = []
        for _dir in _dirs:
            for file in _dir.iterdir():
                if ".tif" in str(file):
                    image = tiff.imread(str(file))
                    images.append(image)

        print(f"working on a dataset with length: {len(images)}")
        mean = np.mean(images, axis=(0, 2, 3)) / norm_value
        stdev = np.std(images, axis=(0, 2, 3)) / norm_value

        stats = (mean, stdev)
        if save_name:
            Statistics.pickle(stats, save_name+".per_dataset.tuple")
        return stats

    @staticmethod
    def source_images(root: Path) -> list:
        images = []
        for path in root.iterdir():# test and train
            if path.is_dir():
                for class_dir in path.iterdir():
                    if path.is_dir():
                        for image_path in class_dir.iterdir():
                            image = tiff.imread(str(image_path))
                            images.append(image)

        print(f"sources [{len(images)}] images")
        return images


