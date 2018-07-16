import logging
import numpy as np
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.models as models
import torchvision.transforms as transforms
from datetime import datetime
from skimage.external import tifffile as tiff
from tensorboardX import SummaryWriter

from src.MLDataTools.image_normalization import RandomDihedral, Denormalize, AddDimension, ToTensorCopy

logger = logging.getLogger(__name__)

torch.set_default_tensor_type(torch.DoubleTensor)  # so it doesnt throw a incompatible type exception
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
device = torch.device(DEVICE)  # important for cloud compatability; different type from DEVICE

# CONSTANTS
NUM_CLASSES = 4
BATCH_SIZE = 40

global_step = 0

# TensorBoardX
date = datetime.now().strftime("%Y-%m-%d.%H:%M:%S")

writer = SummaryWriter('tensorboardx/ResNet50_' + date)
net = models.resnet50(num_classes=10).to(device)
net.to(device)
resnet_mean, resnet_stdev = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225] # visualize the images with this normalization

ds_transforms = transforms.Compose([
    RandomDihedral(), # doing this first gets rid of the negative stride error in .from_numpy
    ToTensorCopy(),
    AddDimension(torch.zeros),
    transforms.Normalize(mean=resnet_mean,
                         std=resnet_stdev),
])
# use this for saving images later
denormalize = Denormalize(means=resnet_mean,
                     stdev=resnet_stdev)


def tiff_read(path: str):
    image = tiff.imread(path).astype(np.double)
    return image


DATA_DIR = './datasets/yeast_ready'
DATA_ROOT = os.path.join(os.getcwd(), DATA_DIR)

trainset = torchvision.datasets.ImageFolder(DATA_ROOT + '/train', transform=ds_transforms, loader=tiff_read)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)

testset = torchvision.datasets.ImageFolder(DATA_ROOT + '/test', transform=ds_transforms, loader=tiff_read)
testloader = torch.utils.data.DataLoader(testset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

# invert class_to_id
idx_to_class = {v: k for k, v in trainset.class_to_idx.items()}

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.01)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min')


def train(epoch):
    net.train()  # affects only modules like Dropout
    trainiter = iter(trainloader)
    for batch_idx, (data, targets) in enumerate(trainiter, 1):
        # get the inputs

        data, targets = data.to(device), targets.to(device)

        # backprop
        optimizer.zero_grad()  # dont forget to do that
        output = net(data)
        loss = criterion(output, targets)
        loss.backward()
        optimizer.step()
        scheduler.step(loss)

        # tensorboard
        global global_step
        global_step += 1
        writer.add_scalar('Train_Loss', loss.data.item(), global_step)
        if batch_idx % 2 == 0:  # every 2nd batch add to our embedding writer
            targets = targets.type(torch.DoubleTensor)
            writer.add_embedding(output, metadata=targets.data, label_img=data.data, global_step=global_step)
        if batch_idx % 5 == 0:
            samples_done = batch_idx * BATCH_SIZE
            percent = 100. * samples_done / len(trainloader.dataset)
            logger.info(f"Train Epoch: {epoch} [{samples_done}/{len(trainloader.dataset)} "
                        f"({percent:3.3}%)]\tLoss: {loss.item():10.5}")


def test(epoch):  # include one-time visualization to check that the images are ok
    with torch.no_grad():
        net.eval()
        test_loss = 0
        wcases = []  # list of worst cases
        classes_correct = list(0 for _ in range(NUM_CLASSES))
        classes_total = list(0 for _ in range(NUM_CLASSES))

        for data, targets in iter(testloader):
            data, targets = data.to(device), targets.to(device)

            output = net(data)
            # errors is a top 2 List[error:float, index of sample:int]
            errors = worst_cases(output, targets)

            for error, idx in errors:
                target = targets[idx].data.item()
                label = f"{idx_to_class[target]}_{error:0.5}"
                tensor = data[idx]
                wcases.append((tensor, label))

            # sum up batch loss
            test_loss += criterion(output, targets).item()

            # get the index of the max log-probability
            _, pred = output.max(1)  # returns a tuple the last element is the index Tensor
            c = (pred == targets).squeeze()
            l = c.size(0)  # to account for different batch sizes
            # this helps to identify which classes the network is struggling with
            for i in range(l):
                label = targets[i].item()
                classes_correct[label] += c[i].item()
                classes_total[label] += 1

        test_loss /= len(testloader.dataset)
        accuracy = 100. * (sum(classes_correct) / sum(classes_total))

        writer.add_scalar('Test_Loss', test_loss, epoch)
        writer.add_scalar('Test_Accuracy', accuracy, global_step=epoch)

        logger.info(f"\nTest set: Average loss: {test_loss:6.5}, Accuracy: {accuracy:10.5}%\n")

        for i, total, correct in zip(range(NUM_CLASSES), classes_total, classes_correct):
            cl = idx_to_class[i]
            cl_accuracy = 100. * (classes_correct[i] / classes_total[i])
            logger.info(f"class [{cl}]: accuracy {cl_accuracy:10.4}%")

        for image, label in wcases[:5]:  # List[image:np.array, class:str]
            # should be of dimensions (3, 200, 200)
            denorm_image = denormalize(image)
            writer.add_image(label, denorm_image, epoch)


def worst_cases(output: torch.Tensor, targets: torch.Tensor, top=2):
    assert output.size(0) == targets.size(0)
    length = output.size(0)
    errors = []
    for i in range(length):
        z = torch.zeros(NUM_CLASSES)
        label = targets[i].item()
        z[label] = 1
        diff = (output[i] - z).numpy().copy()
        diff = np.sum(np.abs(diff))
        errors.append((diff, i))

    errors.sort(key=lambda x: x[0], reverse=True)

    return errors[:top]
