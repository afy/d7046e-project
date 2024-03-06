import os
import xarray as xr
from torch.utils.data import Dataset
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
import torchvision.transforms.functional as TF
import random

#Creates a dataset for our cloud images
class CloudDataset(Dataset):
    def __init__(self, image_dir,transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.images = os.listdir(image_dir)

    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, index):
        # Creates an path to specified image and reads it into xarray
        img_path = os.path.join(self.image_dir,self.images[index])
        df = xr.open_dataset(img_path, engine='netcdf4')

        # Extracts labels from image
        mask = torch.from_numpy(df["Label"].values).unsqueeze(0)
        # Create RGB image and normalizes it values by scaling so the 4th procentile is mapped 0 and the 96th is mapped to 1, then clips values outside 0 and 1.
        imagergb = np.dstack((df["B04"],df["B03"],df["B02"],df["B01"],df["B05"],df["B06"],df["B07"],df["B08"],df["B09"],df["B10"],df["B11"],df["B12"]))
        
        imagergb=np.log(imagergb+(imagergb==np.zeros_like(imagergb)).astype(int)*0.00001)
        cli=0
        image = np.clip((imagergb-np.percentile(imagergb,cli))/(np.percentile(imagergb,100-cli)-np.percentile(imagergb,cli)),0, 1).astype(float)

        image = torch.from_numpy(image)
        image = image.permute(2,0,1)
        if self.transform is not None:
            image = self.transform["image"](image)
            mask = self.transform["mask"](mask)
            i, j, h, w = transforms.RandomCrop.get_params(
            image, output_size=(128, 128))
            image = TF.crop(image, i, j, h, w)
            mask = TF.crop(mask, i, j, h, w)
            if random.random() > 0.5:
                image = TF.hflip(image)
                mask = TF.hflip(mask)

            # Random vertical flipping
            if random.random() > 0.5:
                image = TF.vflip(image)
                mask = TF.vflip(mask)

        onehot_mask =F.one_hot((mask[0]).to(torch.int64),num_classes=6).permute(2,0,1)

        return image,onehot_mask