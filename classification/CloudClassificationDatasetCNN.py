import os
import xarray as xr
from torch.utils.data import Dataset
import numpy as np
import torch
import torchvision

#Creates a dataset for our cloud images
class CloudClassificationDataset(Dataset):
    def __init__(self, image_dir, json, transform=None, channels:tuple=("b04","b03","b02")):
        self.image_dir = image_dir
        self.transform = transform
        self.channels = channels
        self.json = np.load(json,allow_pickle=True)

    def __len__(self):
        return len(self.json)
    
    def __getitem__(self, index):
        # Finds filename in json file and creates path to corresponding image
        filename = "skgs_"+self.json[index]['ValideringsobjektBildId']+".nc"
        img_path = os.path.join(self.image_dir,filename)

        # Opens NetCDF4 image
        df = xr.open_dataset(img_path, engine='netcdf4')

        # Extracts labels from the json file
        label = self.json[index]["MolnDis"]

        #Creates a tuple of dataArray objects with given channels from the tuple of channels and the dataArray
        channel_lst=[]
        for c in self.channels:
            channel_lst.append(df[c][0])
        channel_tup = tuple(channel_lst)

        # Stacks, normalizes, and cut the image to a (20, 20, C) format between 0 and 1
        imagergb = np.dstack(channel_tup)
        cli=1
        image = torch.from_numpy(np.clip((imagergb-np.percentile(imagergb,cli))/(np.percentile(imagergb,100-cli)-np.percentile(imagergb,cli)),0, 1)[:20,:20,:]).permute(2,0,1)
        
        if self.transform is not None:
            image = self.transform(image)

        return image,torch.nn.functional.one_hot(torch.Tensor([int(label)]).to(torch.int64),2)[0]