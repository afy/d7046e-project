import os
import xarray as xr
from torch.utils.data import Dataset
import numpy as np

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
        label = df["Label"].values

        # Create RGB image and normalizes it values by scaling so the 4th procentile is mapped 0 and the 96th is mapped to 1, then clips values outside 0 and 1.
        imagergb = np.dstack((df["B04"],df["B03"],df["B02"]))
        cli=4
        image = np.clip((imagergb-np.percentile(imagergb,cli))/(np.percentile(imagergb,100-cli)-np.percentile(imagergb,cli)),0, 1)
        
        return image,label