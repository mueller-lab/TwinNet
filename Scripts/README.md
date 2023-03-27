# Twin Network scripts
This directory of the Twin Network repository contains code implementations for training and testing of the Twin Network.

## Overview
- [Commonly used scripts](https://github.com/mueller-lab/TwinNet/tree/main/Scripts/tools_V1)
- [Training](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Training.ipynb)
- [Testing - Similarities_developmental_stages](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Similarities_developmental_stages/): Assessment of developmental stages and trajectories with Twin Network generated similarities
- [Testing - Similarities_variability](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Similarities_variability/): Assessment of variability of similarities and predicted stages within a batch of embryos.
- [Testing - Autoregression](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Inference_autoregression.ipynb): Calculation of similarities for each image of a test embryo with all previous images of the same embryo for an image sequence
- [Testing - DTS](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/DTS/): A tool to analyze cosine similarity matrices, i.e., results of autoregression.

# Training
Instructions and descriptions are listed in the corresponding .ipynb file.

# Testing
## Prediction of developmental stages and developmental trajectories
The directory "Similarities_developmental_stages" contains data, code, and example results for the usage of Twin Network to assess and compare developmental stages, and construct developmental trajectories based on predicted developmental stages.
Instructions and descriptions are listed in the corresponding .ipynb file.

![Similarity profile](https://github.com/mueller-lab/TwinNet/blob/main/data/images/Figure1b.png)

## Assessment of variability of similarities and predicted stages
The directory "Similarities_variability" contains data, code, and example results for the analysis of the variability of predicted similarities and developmental stages using Twin Network. Instructions and descriptions are listed in the corresponding .ipynb file.

![Variability](https://github.com/mueller-lab/TwinNet/blob/main/data/images/Figure2a.png)

## Autoregression
This part of the testing files contains the code for "autoregression" using Twin Network. This means that Twin Network is used to calculate similarities between an image of a test embryo from an image sequence with all previous images of the same embryo. Expected outputs are two-dimensional matrices with values in the range of 0 - 1. Values should be close to 1 when similarities are high. This is expected to be in the period closest to the latest tested acquisition timepoint. High similarity values are expected to form plateaus.

Self-similarity matrices can be plotted by color-coding high similarity values. The viridis palette was used as color map and adjusted to a range that matches the similarity values for clear visualization. High similarity values are expected to arrange along the diagonal of the similarity matrix as rectangles of different sizes, corresponding to the duration of plateaus of high similarity values.

Instructions and descriptions are listed in the corresponding .ipynb file. To recreate similarity matrices generated for the zebrafish embryo in Fig. 4, use data from Twin Network Dataset 024, well -A005--PO01, embryo E003.

## DTS
This is a custom software package to study cosine similarity matrices of image sequences. It contains the dts commandline tool to import and prepare the matrices/images. There is a comprehensive user-interface to browse the results, and explore the images underlying the matrices.
