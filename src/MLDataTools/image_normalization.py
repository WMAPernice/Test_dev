import numpy as np
import torch


class RandomDihedral:
    def __call__(self, x):
        # set state
        rot_times = np.random.randint(0, 3)
        do_flip = np.random.random() < 0.5
        # do the actual transformations
        x = np.rot90(x, rot_times, axes=(1, 2))
        y = np.fliplr(x).copy() if do_flip else x
        return y


if __name__ == '__main__':
    t = RandomDihedral()
    m = np.diag([1, 2, 3])
    print(m)
    print(t(m))


class GetInfo:
    def __init__(self, label=None):
        self.label = label

    def __call__(self, sample):
        try:
            print(sample.shape)
        except:
            pass
        finally:
            if self.label: print(self.label)
            print(type(sample))
            return sample


class AddDimension:
    def __init__(self, init_fn=torch.zeros):
        self.init_fn = init_fn

    def __call__(self, sample):
        size = sample.shape[-1]  # assuming image is square with dims Channels x Width x Height
        zeros = self.init_fn(1, size, size)
        return torch.cat((sample, zeros))


# avoids a pytorch error: negative strides not supported in .from_numpy
class ToTensorCopy:
    def __call__(self, sample):
        return torch.from_numpy(sample.copy())


class Denormalize:
    def __init__(self, means, stdev):
        self.means = means
        self.stdev = stdev

    def __call__(self, sample):
        for dim in range(3):
            sample[dim].mul_(self.stdev[dim]).add_(self.means[dim])
        return sample