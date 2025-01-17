import os
import xarray as xr
from torch.utils.data import Dataset
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
import torchvision.transforms.functional as TF
import random
import torchvision.transforms.v2 as v2

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
        imagergb = np.dstack((df["B04"],df["B03"],df["B02"]))
        cli=5
        image = np.clip((imagergb-np.percentile(imagergb,cli))/(np.percentile(imagergb,100-cli)-np.percentile(imagergb,cli)),0, 1)

        image = torch.from_numpy(image)
        image = image.permute(2,0,1)
        image_disp=image

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

            image_disp=image
            image = v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])(image)

        #combine undefined and missing and create onehot
        mask=mask-((mask==5).to(torch.int8)*5)
        onehot_mask =F.one_hot((mask[0]).to(torch.int64),num_classes=5).permute(2,0,1)

        return image,onehot_mask,image_disp