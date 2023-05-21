# Twin Network scripts
This directory of the Twin Network repository contains code implementations for training and testing of the Twin Network.

# Overview
- [Configuration files](#Configuration-files)
- [Training scripts](#Training-scripts)
- [Testing scripts](#Testing-scripts)

# Configuration files
These files contain paths to saved tensorflow models and datasets. When running the demo test scripts of Twin Network, the operating system is either loaded automatically or specified by the user, and the corresponding data paths are loaded from the corresponding config file. 
- [Configuration file for Linux Operating Systems](https://github.com/mueller-lab/TwinNet/tree/main/code/Scripts/twinnet_config/Linux/config.json)
- [Configuration file for Windows Operating Systems](https://github.com/mueller-lab/TwinNet/tree/main/code/Scripts/twinnet_config/Windows/config.json)

# Training scripts
We trained and tested Twin Network for four model organisms: Caenorhabditis elegans (1.), Medaka (Oryzias latipes, 2.), Stickleback (Gasterosteus aculeatus, 3.), and Zebrafish (Danio rerio, 4.). In these training scripts, image triplets were built with three different images. For each image triplet, two images were selected from similar developmental phases and one image was selected from a different developmental phase. For Zebrafish (Danio rerio, 5.), a second training approach was used to train an additional Twin Network model. Instead of selecting two different images as anchor and positive images from similar developmental stages, the anchor image was augmented with image augmentation techniques and used as positive image.

Each training script can be used to train a Twin Network model for a new organism. To this end, image files should be provided with time stamps or acquisition image numbers in their image file names. The corresponding pattern, by which the time stamp or image numbers are indicated should be specified when loading the image paths for preparation of the Twin Network dataset.

1. [Training C. elegans](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Training_Celegans.ipynb)
2. [Training Medaka](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Training_Medaka.ipynb)
3. [Training Stickleback](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Training_Stickleback.ipynb)
4. [Training Zebrafish](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Training_Zebrafish.ipynb) with different images as anchor and positive images
5. [Training Zebrafish](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Training_Zebrafish2.ipynb) with the same image as anchor and positive image

## Testing scripts
1. [Image ordering](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/): Order shuffled images from one image time series acquisition based on image similarities
2. [Similarities developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/): Assessment of developmental stages and trajectories with Twin Network generated similarities
3. [Similarity variability, predicted developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/): Assessment of variability of predicted stages within a batch of embryos.
4. [Similarity variability, similarities at selected developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/): Assessment of variability of similarities within a batch of embryos.
5. [Deviation of development, in-batch](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
6. [Deviation of development based on predicted developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
7. [Deviation of development between groups of drug-treated embryos](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
8. Autoregression: Calculation of similarities for each image of a test embryo with all previous images of the same embryo for an image sequence
- [Autoregression C. elegans](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
- [Autoregression Medaka](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
- [Autoregression Stickleback](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
- [Autoregression Zebrafish](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/)
13. [DTS](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/): Analysis of cosine similarity matrices, e.g. results of self-similarity calculation in autoregression.

## Image segmentation scripts
- [Image segmentation](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/segmentation)

# Testing
## Prediction of developmental stages and developmental trajectories
The directory "Similarities_developmental_stages" contains data, code, and example results for the usage of Twin Network to assess and compare developmental stages, and construct developmental trajectories based on predicted developmental stages.
Instructions and descriptions are listed in the corresponding .ipynb file.

![Similarity profile](https://raw.githubusercontent.com/mueller-lab/TwinNet/main/data/images/Figure1b.png)

## Assessment of variability of similarities and predicted stages
The directory "Similarities_variability" contains data, code, and example results for the analysis of the variability of predicted similarities and developmental stages using Twin Network. Instructions and descriptions are listed in the corresponding .ipynb file.

![Variability](https://raw.githubusercontent.com/mueller-lab/TwinNet/main/data/images/Figure2a.png)

## Autoregression
This part of the testing files contains the code for "autoregression" using Twin Network. This means that Twin Network is used to calculate similarities between an image of a test embryo from an image sequence with all previous images of the same embryo. Expected outputs are two-dimensional matrices with values in the range of 0 - 1. Values should be close to 1 when similarities are high. This is expected to be in the period closest to the latest tested acquisition timepoint. High similarity values are expected to form plateaus.

Self-similarity matrices can be plotted by color-coding high similarity values. The viridis palette was used as color map and adjusted to a range that matches the similarity values for clear visualization. High similarity values are expected to arrange along the diagonal of the similarity matrix as rectangles of different sizes, corresponding to the duration of plateaus of high similarity values.

Instructions and descriptions are listed in the corresponding .ipynb file. To recreate similarity matrices generated for the zebrafish embryo in Fig. 4, use data from Twin Network Dataset 024, well -A005--PO01, embryo E003.

## DTS
This is a custom software package to study cosine similarity matrices of image sequences. It contains the dts commandline tool to import and prepare the matrices/images. There is a comprehensive user-interface to browse the results, and explore the images underlying the matrices.
