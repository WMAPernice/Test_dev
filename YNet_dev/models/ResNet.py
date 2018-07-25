import torch, torch.nn as nn, torch.nn.functional as F
from tensorboardX import SummaryWriter
from datetime import datetime
import os

class BnLayer(nn.Module):
    def __init__(self, ni, nf, stride=2, kernel_size=3):
        super().__init__()
        self.conv = nn.Conv2d(ni, nf, kernel_size=kernel_size, stride=stride,
                              bias=False, padding=1)
        self.a = nn.Parameter(torch.zeros(nf, 1, 1))
        self.m = nn.Parameter(torch.ones(nf, 1, 1))

    def forward(self, x):
        x = F.relu(self.conv(x))
        x_chan = x.transpose(0, 1).contiguous().view(x.size(1), -1)
        if self.training:
            self.means = x_chan.mean(1)[:, None, None]
            self.stds = x_chan.std(1)[:, None, None]
        return (x - self.means) / self.stds * self.m + self.a

class ResnetLayer(BnLayer):
    def forward(self, x): return x + super().forward(x)

class ResNet(nn.Module):
    def __init__(self, layers, num_classes, obj_name, exp_name="default", tb_log=True,):
        """

        :param layers:
        :param num_classes:
        :param obj_name: like 'C', 'A'
        :param tb_log: boolean; if true then log to tensorboard
        :param exp_name: for example "v5_per_class" as in training on yeast_v5 with per class normalization
        """
        self.arch = f"ResNet{len(layers)}"
        date = datetime.now().strftime("%m-%d_%H-%M")
        self.tag = f"{self.arch}_{exp_name}_{date}"

        if tb_log:
            base_dir = './results/'+'tensorboardx/'
            if not os.path.isdir(base_dir): os.makedirs(base_dir)
            self.writer = SummaryWriter(base_dir+obj_name+'/'+self.tag)

        super().__init__()
        self.conv1 = nn.Conv2d(2, 10, kernel_size=5, stride=1, padding=2)
        self.layers = nn.ModuleList([BnLayer(layers[i], layers[i + 1])
                                     for i in range(len(layers) - 1)])

        self.layers2 = nn.ModuleList([ResnetLayer(layers[i + 1], layers[i + 1], 1)
                                      for i in range(len(layers) - 1)])

        self.layers3 = nn.ModuleList([ResnetLayer(layers[i + 1], layers[i + 1], 1)
                                      for i in range(len(layers) - 1)])
        self.out = nn.Linear(layers[-1], num_classes)

    def forward(self, x):
        x = self.conv1(x)
        for l, l2, l3 in zip(self.layers, self.layers2, self.layers3):
            x = l3(l2(l(x)))
        x = F.adaptive_max_pool2d(x, 1)
        x = x.view(x.size(0), -1)
        return F.log_softmax(self.out(x), dim=-1)