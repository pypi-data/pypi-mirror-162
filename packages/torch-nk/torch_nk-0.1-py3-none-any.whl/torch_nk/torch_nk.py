from requests import get
import os
import zipfile
import shutil
from torch.utils.data.dataset import Dataset
from torchvision import transforms
from torchvision import datasets
import torch

def cifar10_torch():

    # file down and process

    url = "https://github.com/nobug-code/test_nk_2/raw/main/airplane.zip"
    file_name = './down.zip'

    with open(file_name, "wb") as file:  # open in binary mode
        response = get(url)  # get request
        file.write(response.content)  # write to file

    if not os.path.exists("./cifar/"):
            os.makedirs("./cifar/")

    with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall('./cifar/')

    shutil.rmtree("./cifar/__MACOSX/")


    '''
    datasets 이라는 코드로 간단히 불러올 수도 있다. 대신 단점으로는 custom이 힘들다는점!
    '''
    trans = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])])

    file_path = './cifar/'
    custom_dataset = datasets.ImageFolder(file_path, transform=trans)
    my_dataset_loader = torch.utils.data.DataLoader(dataset=custom_dataset,
                                                    batch_size=1,
                                                    shuffle=True)

    return my_dataset_loader

cifar10_torch()

