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


class ToImage:
    def __call__(self, sample):
        sample = torch.from_numpy(sample)
        zeros = torch.zeros(1, 200, 200)
        return torch.cat((sample, zeros))


class Denormalize:
    def __init__(self, means, stdev):
        self.means = means
        self.stdev = stdev

    def __call__(self, sample):
        for dim in range(2):
            sample[dim].mul_(self.stdev[dim]).add_(self.means[dim])
        return sample


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
