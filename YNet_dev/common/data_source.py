import pickle, os
import numpy as np
from pathlib import Path
import skimage.external.tifffile as tiff
from resources.conv_learner import *
from typing import Union, List


def dataset_source(source: Union[str, Path]) -> tuple:
    test_dirs , train_dirs = [], []

    for ds_dir in source.iterdir():
        if 'DS_Store' not in str(ds_dir):
            for class_dir in ds_dir.iterdir():
                if 'DS_Store' not in str(class_dir):
                    if 'test' in str(class_dir): test_dirs.append(class_dir)
                    elif 'train' in str(class_dir): train_dirs.append(class_dir)
    return test_dirs, train_dirs

class Statistics:
    @staticmethod
    def per_class(test_dirs: List[Path], train_dirs: List[Path], norm_value=65536, save_name='') -> dict:
        stats = {}

        class_dirs = zip(test_dirs, train_dirs)
        for test, train in class_dirs:

            class_name = test.name
            class_images = []
            for dir_ in [test, train]:
                # read from each dir and append to the images
                for file in dir_.iterdir():
                    image = tiff.imread(str(file))
                    class_images.append(image)

            print(f"working on: {class_name}")
            mean = np.mean(class_images, axis=(0, 2, 3)) / norm_value
            stdev = np.std(class_images, axis=(0, 2, 3)) / norm_value

            stats[class_name] = (mean, stdev)

        if save_name:
            Statistics.pickle(stats, save_name)  # if save is given it should be a string; empty strings are false

        return stats

    @staticmethod
    def pickle(stats, name="stats.dict") -> None:
        with open(name, 'wb') as file:
            pickle.dump(stats, file)