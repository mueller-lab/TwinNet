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
Twin Network uses deep learning algorithms to learn features of embryos that can be extracted from two-dimensional images. Manual annotation of a training dataset for this type of algorithm, however, would have the same difficulties as classical descriptions of embryonic development:
- Transitions between distinct developmental stages may be fluid, which makes drawing sharp boundaries difficult and subjective
- Phenotypes may vary even at similar developmental stages due to biological variations
- Imaging artifacts may appear due to technical variations
- Laborious annotations would have to be repeated for each species to be studied, due to variations of embryonic development between different species

All of these steps are ultimately limited to prior knowledge of the process being studied.

By its design, on the other hand, Twin Network circumvents these limitations: During training, the network is incentivised to learn features that can be found at specific developmental stages from image-to-image comparisons, using images of embryos at similar and different developmental stages as training data. To require a minimum of preliminary information, only the time stamps of the time-lapse images of the embryos are needed for dataset preparation.

### How to use Twin Network
This repository contains training and testing applications for Twin Network, including pre-trained models for the model organisms _Caenorhabditis elegans_, Medaka (_Oryzias latipes_), Stickleback (_Gasterosteus aculeatus_), and Zebrafish (_Danio rerio_). Installation instructions are listed below.

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

*Option 1*: Create Python environment from [twinnetworkenv.yml](https://github.com/mueller-lab/TwinNet/blob/main/installation/twinnetworkenv.yml) file:
```
conda env create -f twinnetworkenv.yml
```

*Option 2*: Create Python environment from [requirements.txt](https://github.com/mueller-lab/TwinNet/blob/main/installation/requirements.txt) file:
```
conda create --name 'twinnet' --file requirements.txt
```

*Option 3*: Create environment manually
- Create a python environment with Python 3.9
- Install [Tensorflow](https://www.tensorflow.org/install/)
- Install other dependencies ([requirements.txt](https://github.com/mueller-lab/TwinNet/blob/main/installation/requirements.txt))

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

Typical installation time on a standard desktop computer with standard internet connection speeds is approximately 20 min. For installation of CUDA and cuDNN, additional installation time of approximately 1 h and system reboots are required.

# Demo
To run the demo scripts for Twin Network on a local PC, please follow the [installation instructions](https://github.com/mueller-lab/TwinNet#installation-guide) to install Python with the required packages. The demo script access configuration files located in the [Scripts/twinnet_config](https://github.com/mueller-lab/TwinNet/tree/main/code/Scripts/twinnet_config) directory. Before running the scripts, update the corresponding data paths in the config files for Windows or Linux, depending on your operating system, with the required file paths.

A description of the scripts is given here: [Overview of scripts](https://github.com/mueller-lab/TwinNet/tree/main/code/Scripts/README.md). Training and testing files are located in the folder [Scripts](https://github.com/mueller-lab/TwinNet/tree/main/code/Scripts).

Run times depend on installed hardware, sample and batch sizes used for the analysis. Examples for approximate durations tested on our system:
- The duration of the generation of embeddings and the calculation of similarities for 1 test image and 1 reference image sequence with 720 frames is 18 s
- Calculation of embeddings and similarities for 1 test image sequence with 418 frames and 3 reference datasets with each 360 frames is 160 s
- Image ordering of a test image sequence with 300 frames is 20 s
- Calculation of similarities for each image of a test embryo with all previous images of the same embryo for an image sequence with 360 images is 5-10 s
- Calculation of similarity values between 77 embryos at 360 different acquisition timepoints is 11 min

# Results
Examples of results using the testing demo scripts are stored within the ["results"-directory](https://github.com/mueller-lab/TwinNet/tree/main/results).

# License
The content of this project is licensed under the the GNU General Public License version 3.0 (GPL-3.0).
