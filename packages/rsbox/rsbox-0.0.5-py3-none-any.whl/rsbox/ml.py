"""
File: ml.py 
-------------- 
Contains useful functions that I may import while programming 
machine learning projects.  
""" 

from matplotlib import pyplot as plt
from PIL import Image
import torch 
import numpy as np 
from glob import glob
import random


def plot_png(file_path, color):
	"""
	Plots a png file (or jpeg really) using matplotlib. Color is a bool value. 
	If true, image will be displayed in color. Else, it will be displayed in 
	greyscale.
	"""
	image = Image.open(file_path)
	if color == True:
		plt.imshow(image, interpolation='nearest')
		plt.show()
	else:
		plt.imshow(image, interpolation='nearest', cmap='Greys_r')
		plt.show()


def plot_np_img(image_array, color):
	"""
    (Here for longevity purposes... use plot instead)
	Plots a numpy array using matplotlib. Color is a bool value. If true, 
	image will be displayed in color. Else, it will be displayed in 
	greyscale.

    input: image_array must be of shape (1, H, W) or (H, W) for greyscale
    and (3, H, W) for color. 
	"""
	if color == True:
		plt.imshow(image_array, interpolation='nearest')
		plt.show()
	else:
		plt.imshow(image_array, interpolation='nearest', cmap='Greys_r')
		plt.show()


def plot(image_array, color=True):
    """
    Plots a numpy array using matplotlib. Color is a bool value which
    is true by default. If passed in as False, image will be displayed in 
    greyscale. 

    input: image_array must be of shape (1, H, W) or (H, W, 1) or (H, W) for greyscale
    and (3, H, W) or (H, W, 3) for color. 
    """

    # move to numpy is not already in numpy array format 
    image_array = np.array(image_array)
    image_array = np.squeeze(image_array)

    if color == True:
        if image_array.shape[0] == 3:
            image_array = np.moveaxis(image_array, 0, -1)
        plt.imshow(image_array, interpolation='nearest')
        plt.show()
    else:
        plt.imshow(image_array, interpolation='nearest', cmap='Greys_r')
        plt.show()


def image_dir_to_data(dirpath, extension):
    """
    Takes in a directory containing images
    and returns a list of numpy arrays representing
    those images. 
    Args:
        - dirpath: path to directory 
        - extension: image extension type (e.g. png) (string)
    """
    data_subset = []
    sub_set = glob(dirpath + '/*.' + extension)
    for elem in sub_set:
        image = Image.open(elem)
        image_array = np.array(image)
        data_subset.append(image_array)
    return data_subset  


def image_dir_to_data_norm(dirpath, extension):
    """
    (Same as image_dir_to_data but with max value 
    (255) normalization). 
    Takes in a directory containing images
    and returns a list of numpy arrays representing
    those images. 
    Args:
        - dirpath: path to directory 
        - extension: image extension type (e.g. png) (string)
    """
    data_subset = []
    sub_set = glob(dirpath + '/*.' + extension)
    for elem in sub_set:
        image = Image.open(elem)
        image_array = np.array(image)
        image_array = image_array.astype(float)
        image_array = image_array/255.0
        data_subset.append(image_array)
    return data_subset    


def gen_label_pair(data_samples, label):
	"""
	Takes in a list of data samples (i.e. images, x)
	and a corresponding label and returns a list of tuples
	where each tuple is an (x, y) pair. 
	"""
	d_set = []
	for elem in data_samples:
	    sample_pair = (elem, label)
	    d_set.append(sample_pair)
	return d_set 


def gen_distro(master_list):
    """
    Takes in a list of lists who each contain
    (x, y) tuple samples for that class and returns 
    a randomly concatenated version. 
    """
    generated_distro = []
    for class_list in master_list:
        generated_distro = generated_distro + class_list
    random.shuffle(generated_distro)
    return generated_distro
