import os

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from utils import read_txt

train_txt_COVID = './data/covid_ct_dataset/trainCT_COVID.txt'
train_txt_NonCOVID = './data/covid_ct_dataset/trainCT_NonCOVID.txt'
val_txt_COVID = './data/covid_ct_dataset/valCT_COVID.txt'
val_txt_NonCOVID = './data/covid_ct_dataset/valCT_NonCOVID.txt'
test_txt_COVID = './data/covid_ct_dataset/testCT_COVID.txt'
test_txt_NonCOVID = './data/covid_ct_dataset/testCT_NonCOVID.txt'


class CovidCTDataset(Dataset):
    def __init__(self, config, mode):
        """
        Args:
            txt_path (string): Path to the txt file with annotations.
            root_dir (string): Directory with all the images.

        File structure:
        - root_dir
            - CT_COVID
                - img1.png
                - img2.png
                - ......
            - CT_NonCOVID
                - img1.png
                - img2.png
                - ......
        """
        self.config = config
        self.root = self.config.dataset.input_data
        if mode == 'train':

            self.txt_path = [train_txt_COVID, train_txt_NonCOVID]
        elif mode == 'val':
            self.txt_path = [val_txt_COVID, val_txt_NonCOVID]
        elif mode == 'test':
            self.txt_path = [test_txt_COVID, test_txt_NonCOVID]
        self.class_dict = {'CT_COVID': 0, 'CT_NonCOVID': 1}
        self.num_cls = len(self.class_dict)
        self.img_list = []
        for c in range(self.num_cls):
            cls_list = [[os.path.join(self.root, self.class_dict[c], item), c] for item in
                        read_txt(self.txt_path[c])]
            self.img_list += cls_list

        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        train_transformer = transforms.Compose([
            transforms.Resize(256),
            transforms.RandomResizedCrop((224), scale=(0.8, 1.2)),
            transforms.RandomRotation(15),
            transforms.RandomHorizontalFlip(p=0.1),
            transforms.RandomVerticalFlip(p=0.1),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
            transforms.ToTensor(),
            normalize
        ])

        val_transformer = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            normalize
        ])
        if mode == 'train':
            self.transform = train_transformer
        else:
            self.transform = val_transformer
        print('samples = ', len(self.img_list))

    def __len__(self):
        return len(self.img_list)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.img_list[idx][0]

        image = Image.open(img_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(int(self.img_list[idx][1]), dtype=torch.long)
