# Twin Network scripts
This directory of the Twin Network repository contains code implementations for training and testing of the Twin Network.

## Overview
- [Commonly used scripts](https://github.com/mueller-lab/TwinNet/tree/main/Scripts/tools_V1)
- [Training](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Training.ipynb)
- [Testing - Autoregression](https://github.com/mueller-lab/TwinNet/blob/main/Scripts/Inference_autoregression.ipynb): Calculation of similarities for each image of a test embryo with all previous images of the same embryo for an image sequence

# Training
Instructions and descriptions are listed in the corresponding .ipynb file.

# Testing - Autoregression
Instructions and descriptions are listed in the corresponding .ipynb file. Expected outputs are two-dimensional matrices with values in the range of 0 - 1. Values should be close to 1 when similarities are high. This is expected to be in the period closest to the latest tested acquisition timepoint. High similarity values are expected to form plateaus.

Self-similarity matrices can be plotted by color-coding high similarity values. The viridis palette was used as color map and adjusted to a range that matches the similarity values for clear visualization. High similarity values are expected to arrange along the diagonal of the similarity matrix as rectangles of different sizes, corresponding to the duration of plateaus of high similarity values.

To recreate similarity matrices generated for the zebrafish embryo in Fig. 4, use data from Twin Network Dataset 024, well -A005--PO01, embryo E003.
