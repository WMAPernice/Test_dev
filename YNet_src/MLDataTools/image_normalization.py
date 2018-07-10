import numpy as np
import torch
import torchvision.transforms as transforms
from pathlib import Path
from skimage.external.tifffile import imread
from torch.utils.data import DataLoader, Dataset
from typing import Generator, List


class RandomDihedral:
    def __init__(self):
        self.rot_times = np.random.randint(0, 3)
        self.do_flip = np.random.random() < 0.5

    def __call__(self, x):
        x = np.rot90(x, self.rot_times)
        return np.fliplr(x).copy() if self.do_flip else x


def trainloader(root_path: str, batch_size: int = 140) -> Generator:
    """
    Normalized generator
    :param root_path: path to root folder which contains train and test directories
    :param batch_size: size of batch
    :return: Generator
    """
    ds_transforms = [
        RandomDihedral()
    ]
    dataset = YeastDataset(root_path, tfms=ds_transforms)
    print(f"length of yeast dataset: [{len(dataset)}]")
    loader = DataLoader(dataset,
                        batch_size=batch_size, num_workers=5)
    for batch in loader:
        yield batch


class YeastDataset(Dataset):

    def __init__(self, root_dir: str, tfms: List = None, shuffle: bool = False):
        """
        Args:
            root_dir (string): Directory with all the images.
            transforms (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_dir = root_dir
        self.root_path = Path(root_dir)
        self.all_files = get_all_files(self.root_path)
        if shuffle:
            np.random.shuffle(self.all_files)

        # will need to calculate stdev and mean across the whole data-set
        self.images = []
        for file in self.all_files:
            tensor = imread(str(file))
            self.images.append(tensor)

        # get labels from images file names
        self.labels = [str(filename).split('/')[-2] for filename in self.all_files]

        # convert to one hot labels
        self.classes = list(set(self.labels))
        self.num_classes = len(self.classes)

        # calc mean and stdev
        self.mean = np.mean(self.images)
        self.std = np.std(self.images)

        # create a normalize transformations
        normalize = transforms.Normalize([self.mean], [self.std])
        tfms.append(normalize)
        self.transform = transforms.Compose(tfms)

    def __len__(self):
        return len(self.all_files)

    def __getitem__(self, idx) -> tuple:
        img_path = self.all_files[idx]
        sample = imread(str(img_path)).astype(np.uint8)
        tensor = torch.from_numpy(sample).type(torch.DoubleTensor)
        if tensor.size() != torch.Size([2, 200, 200]):
            print("smt went wrong")

        if self.transform:
            tensor = self.transform(tensor)

        raw_label = self.labels[idx]
        ready_label = self.classes.index(raw_label)

        return tensor, ready_label


def get_all_files(root_path: Path, files=[]) -> list:
    for item in root_path.iterdir():
        if item.is_dir():
            df = get_all_files(item)
            files.extend(df)
        elif item.is_file() and '.DS_Store' not in str(item):
            # check if image is square
            files.append(item)
    return list(set(files))


if __name__ == '__main__':
    t = RandomDihedral()
    m = np.diag([1, 2, 3])
    print(m)
    print(t(m))

# [[0 0 1]
#  [0 2 0]
#  [3 0 0]]
# [[0 0 3]
#  [0 2 0]
#  [1 0 0]]
