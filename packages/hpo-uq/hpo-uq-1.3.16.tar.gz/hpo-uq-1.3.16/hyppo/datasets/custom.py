# System
import os
import glob
import random

# External
import numpy
from PIL import Image

def get_data(data_path,data_frac=1,train_frac=0.6,verbose=False,scheme='gray',**kwargs):
    if 'test' not in os.listdir(data_path):
        labels = sorted(os.listdir(data_path))
        # Select data to be used to create datasets
        data = [sorted(glob.glob(data_path+'/'+label+'/*')) for label in os.listdir(data_path)]
        sample_size = int(data_frac*min([len(label_data) for label_data in data]))
        data = [label_data[:sample_size] for label_data in data]
        # List of training images
        i_end_train = int(train_frac*sample_size)
        train_files = numpy.array([label_data[:i_end_train] for label_data in data]).flatten()
        train_set = make_dataset('train',train_files,labels,**kwargs)
        # List of testing images
        i_end_test = int(i_end_train+(sample_size-i_end_train)/2)
        test_files = numpy.array([label_data[i_end_train:i_end_test] for label_data in data]).flatten()
        test_set = make_dataset(test_files,labels,**kwargs)
        # List of validation images
        valid_files = numpy.array([label_data[i_end_test:] for label_data in data]).flatten()
        valid_set = make_dataset(valid_files,labels,**kwargs)
    elif library=='pt':
        import torchvision
        data_path = os.path.expandvars(os.path.join(data_path,'train'))
        transform = [transforms.Grayscale()] if scheme=='gray' else []
        transform = transforms.Compose(transform+[transforms.ToTensor()])
        
        train_set = torchvision.datasets.ImageFolder(
            root = os.path.join(data_path,'train'),
        #    By default the imageFolder loads images with 3 channels and we expect the image to be grayscale.
        #    So let's transform the image to grayscale
        transform =  transforms.Compose([transforms.Grayscale(), transforms.ToTensor()])
    )

    return {'dataset':'img_class', 'train':train_set, 'valid':valid_set, 'test':test_set}

def make_dataset(set_name,list_files,labels,library,scheme='binary'):
    for label in labels:
        os.mkdirs(os.path.join(set_name,),exist_ok=True)
    random.shuffle(list_files)
    X_data, y_data = [],[]
    for image_file in list_files:
        print(image_file)
        break
    return {'X_data':numpy.array(X_data), 'y_data':numpy.array(y_data)}
