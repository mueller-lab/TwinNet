# Twin Network
This repository provides implementation materials for our manuscript "Uncovering developmental time and tempo using deep learning".

## Content
- [Overview](https://github.com/mueller-lab/TwinNet#overview)
- [System Requirements](https://github.com/mueller-lab/TwinNet#system-requirements)
- [Installation Guide](https://github.com/mueller-lab/TwinNet#installation-guide)
- [Demo](https://github.com/mueller-lab/TwinNet#Demo)

# Overview
During animal development, embryos undergo complex morphological changes over time. Classical atlases of developmental stages are based on careful - but tedious - manual microscopic observation. Idealized images capture the essence of characteristic stages but are subjective, and embryos rarely look the same. We present an automated, unbiased deep learning application for multimodal analyses of developing embryos.

### What is the key part of the Twin Network approach?
Twin Network uses deep learning algorithms to learn features of embryos that can be extracted of two-dimensional images. If a dataset had to be manually annotated for Twin Network training, however, one would have the same difficulties as in the classical description of embryonic processes (and developmental processes in general): 
- Transition between phenotypically distinct developmental stages may be fluid, drawing sharp boundaries is difficult and subjective.
- Possibly high degree of phenotypic variance even at one developmental stage due to biological variations. Imaging artifacts may make it difficult to image embryos in the same way.
- Great variation of duration, expression, etc., of embryogenesis between unrelated species, so that this laborious work would have to be performed anew for each species to be studied.

All of these steps are ultimately limited to prior knowledge of the process being studied.

Twin Network, on the other hand, uses image-by-image comparisons as the key part of the training. The datasets used for training contain "triplets" of images, consisting of two images of similar embryos and one image of a dissimilar embryo. A minimum of prior information, namely the time stamps of the time-lapse images of the embryos, is used to create these datasets.

# System Requirements
## Hardware requirements
TwinNet requires only a standard computer with enough RAM to support the operations defined by the user. We recommend the usage of a CUDA-enabled graphics processing unit (GPU) with enough GPU memory to utilize GPU-acceleration of applications.

## Software requirements
The applications have been tested on Windows 10.

CUDA 11.2 and cuDNN 8.1 were installed to enable GPU-acceleration of training and evaluation tasks (https://developer.nvidia.com/cuda-toolkit).

## Python dependencies
TwinNet was developed and tested with Python 3.9.7 and tensorflow 2.8.0. Please see the file "[requirements.txt](https://github.com/mueller-lab/TwinNet/blob/main/installation/requirements.txt)" under "Installation" for information on the used python packages.

# Installation Guide
We recommend creating an environment for the implementation of the code for Twin Network, for example using Miniconda (https://docs.conda.io/en/latest/miniconda.html).

A Python environment for TwinNet implementation can be created as follows:

Option 1: Create environment manually
- (Optional) Create a python environment with Python 3.9
- Install [Tensorflow](https://www.tensorflow.org/install/)
- Install other dependencies ([requirements.txt](https://github.com/mueller-lab/TwinNet/blob/main/Installation/requirements.txt))

```
conda create -n 'twinnet' python=3.9 
conda activate twinnet

pip install jupyter
pip install matplotlib
pip install opencv-python
pip install pandas
pip install scikit-learn
pip install scipy
pip install seaborn
pip install tensorflow-addons
pip install tensorflow_io
...
```
Option2: Create environment from [requirements.txt](https://github.com/mueller-lab/TwinNet/blob/main/installation/requirements.txt) file:
```
conda create --name 'twinnet' --file requirements.txt
```

Typical install time on a standard desktop computer for standard internet connection speeds is approximately 20 min. For installation of CUDA and cuDNN, additional installation time of approximately 1 h and system reboots are required.

# Demo
To run the demo scripts for Twin Network, corresponding data paths in the config files for Windows or Linux, depending on the operating system, should be adjusted.

## Run the notebooks for training and testing
The files are located in the folder [Scripts](https://github.com/mueller-lab/TwinNet/tree/main/code/Scripts). 
Modify the paths for the models and image data accordingly.

Run times depend on installed hardware, sample and batch sizes used for the analysis. Examples for approximate durations tested on our system:
- The duration of the generation of embeddings and the calculation of similarities for 1 test image and 1 reference image sequence with 720 frames is 18 s
- Calculation of embeddings and similarities for 1 test image sequence with 418 frames and 3 reference datasets with each 360 frames is 160 s
- Image ordering of a test image sequence with 300 frames is 20 s
- Calculation of similarities for each image of a test embryo with all previous images of the same embryo for an image sequence with 360 images is 5-10 s
- Calculation of similarity values between 77 embryos at 360 different acquisition timepoints is 11 min
