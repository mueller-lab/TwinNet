# Twin Network scripts
This directory of the Twin Network repository contains code implementations for training and testing of the Twin Network.

# Overview
- [Configuration files](#Configuration-files)
- [Training scripts](#Training-scripts)
- [Testing scripts](#Testing-scripts)
- [Data access](#Data-access)

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
5. [Training Zebrafish](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Training_Zebrafish2.ipynb) with the same image as anchor and positive image

# Testing scripts
Testing scripts for different usecases of Twin Network are provided with this repository. Sample results are stored inside the [results folder](https://github.com/mueller-lab/TwinNet/tree/main/results).

### 1. [Image ordering](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Image_ordering.ipynb)

Order shuffled images from one image time series acquisition based on image similarities. Compare ordering results to results generated from benchmark (Dsilva et al., 2015).

### 2. [Prediction of developmental stages and developmental trajectories](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Similarities_developmental_stages.ipynb)

Assess and compare developmental stages, and construct developmental trajectories based on predicted developmental stages.

<img src="https://raw.githubusercontent.com/mueller-lab/TwinNet/main/data/images/Figure1b.png" width="400">

### 3. [Assessment of variability of predicted developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Similarities_variability_predicted_developmental_stages_variability.ipynb)

Assess the variability of predicted developmental stages within a batch of embryos at a similar age using Twin Network. 

<img src="https://raw.githubusercontent.com/mueller-lab/TwinNet/main/data/images/Figure2a.png" width="800">

### 4. [Assessment of variability of similarities at selected developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Similarities_variability_predicted_similarities_variability.ipynb)

Assess the variability of similarity values within a batch of embryos at a similar age using Twin Network.

<img src="https://raw.githubusercontent.com/mueller-lab/TwinNet/main/data/images/Variability_similarities.svg" width="500">

### 5. [In-batch detection of deviation of development](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Deviation_development_in-batch_detection.ipynb)

Based on similarities between individual sibling embryos from the same batch, assess if an embryo shows deviation from normal embryonic development.

### 6. [Deviation of development based on predicted developmental stages](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Deviation_development_predicted_developmental_stages.ipynb)

Based on predicted developmental stages for images of individual sibling embryos from a time series image acquisition, assess if an embryo shows deviation from normal embryonic development.

### 7. [Deviation of development between groups of drug-treated embryos](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Deviation_development_inhibitor_detection.ipynb)

Assess average cosine similarities between individual sibling embryos from multiple batches with different treatment conditions. For example, compare similarities between all embryos from a batch of small molecule inhibitor treated embryos with untreated wildtype embryos. Plot the similarities between different treatment groups for each acquisition timepoint of a time series image acquisition.

### 8. Autoregression

Calculation of similarities for each image of a test embryo with all previous images of the same embryo for an image sequence. This part of the testing files contains the code for "autoregression" using Twin Network. This means that Twin Network is used to calculate similarities between an image of a test embryo from an image sequence with all previous images of the same embryo. Expected outputs are two-dimensional matrices with values in the range of 0 - 1. Values should be close to 1 when similarities are high. This is expected to be in the period closest to the latest tested acquisition timepoint. High similarity values are expected to form plateaus.

Self-similarity matrices can be plotted by color-coding high similarity values. The viridis palette was used as color map and adjusted to a range that matches the similarity values for clear visualization. High similarity values are expected to arrange along the diagonal of the similarity matrix as rectangles of different sizes, corresponding to the duration of plateaus of high similarity values.

Instructions and descriptions are listed in the corresponding .ipynb files.

- [Autoregression C. elegans](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Autoregression_Celegans.ipynb)
- [Autoregression Medaka](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Autoregression_Medaka.ipynb)
- [Autoregression Stickleback](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Autoregression_Stickleback.ipynb)
- [Autoregression Zebrafish](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/Autoregression_Zebrafish.ipynb)

### 9. [DTS](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/DTS/)
Analysis of cosine similarity matrices, e.g. results of self-similarity calculation in autoregression. This is a custom software package to study cosine similarity matrices of image sequences. It contains the dts commandline tool to import and prepare the matrices/images. There is a comprehensive user-interface to browse the results, and explore the images underlying the matrices.

### 10. [Image segmentation](https://github.com/mueller-lab/TwinNet/blob/main/code/Scripts/segmentation)
Segment images containing multiple zebrafish embryos and create a JSON file for each image with annotations of the positions of the zebrafish embryos. This is a commandline tool for the segmentation of images of multiple zebrafish embryos.
Track individual embryo positions in time series image acquisitions of a batch of embryos. Cut out the annotated zebrafish embryo image segments and save them sorted by embryos.

In the first step, annotations of the test image data are created. To segment images and store image annotations, run the following command with adjusted paths:
```
"python main.py -i /path/to/input/data -m /path/to/segmentation/model -o /path/to/save/outputs/to"
```
In the second step, the annotations are used and loaded to cut out the image segments. Please note that in order to load the images for cutting, the second script loads the image paths from the annotation files. Thus, moving the image files after generating the annotations and before cutting out the image segments might hinder the second step.
```
"python segment.py -i /path/to/annotation/data -o /path/to/save/segments/to"
```
<img src="https://raw.githubusercontent.com/mueller-lab/TwinNet/main/data/images/Segmentation.png" width="800">

# Data access
The image data for the Twin Network zebrafish applications are published under https://dx.doi.org/10.48606/50, and are publicly retrievable for the Twin Network C. elegans, Medaka, and Stickleback applications. The following table provides an overview on where to load the used datasets.

| Application | Test dataset | File paths in test dataset | Reference dataset |
| ---------- | --- | --- | --- |
| Reference dataset 1 | https://dx.doi.org/10.48606/80 | File paths for three reference data sets listed in three [JSON files](https://github.com/mueller-lab/TwinNet/tree/main/data/twinnet_data/images_jsons_reference)| n/a |
| Reference dataset 2 | https://dx.doi.org/10.48606/80 | File paths for three reference data sets listed in one [JSON file](https://github.com/mueller-lab/TwinNet/tree/main/data/twinnet_data/images_jsons_reference2/dataset_reference2_paths_anchors.json), 8 additional images provided separately in the [dataset folder](https://github.com/mueller-lab/TwinNet/tree/main/data/twinnet_data/images_jsons_reference2/) | n/a |
| Image ordering | https://dx.doi.org/10.48606/68 | TwinNetworkDataset010/-B003--PO35/E005 | n/a |
| Prediction of developmental stages and developmental trajectories | https://dx.doi.org/10.48606/75 | TwinNetworkDataset018/-C012--PO01/E000 | Reference dataset 1 |
| Assessment of variability of predicted developmental stages | https://dx.doi.org/10.48606/82 | File paths for test embryos are listed in a [JSON file](https://github.com/mueller-lab/TwinNet/tree/main/data/twinnet_data/data_test_similarities_variability/test_embryos_sorted.json) | Reference dataset 1 |
| Assessment of variability of similarities at selected developmental stages | https://dx.doi.org/10.48606/82 | File paths for test embryos are listed in a [JSON file](https://github.com/mueller-lab/TwinNet/tree/main/data/twinnet_data/data_test_similarities_variability/test_embryos_sorted.json) | n/a |
| In-batch detection of deviation of development | https://dx.doi.org/10.48606/76 | TwinNetworkDataset017/-B006--PO01/ | n/a |
| Deviation of development based on predicted developmental stages | https://dx.doi.org/10.48606/79 | File paths for test embryos are listed in a [JSON file](https://github.com/mueller-lab/TwinNet/tree/main/data/twinnet_data/data_test_deviation_development_predicted_developmental_stages/embryos_test.json) | Reference dataset 2 |
| Deviation of development between groups of drug-treated embryos, Wildtype | https://dx.doi.org/10.48606/76 | TwinNetworkDataset017/-B002--PO01/ | n/a |
| Deviation of development between groups of drug-treated embryos, BMP-inhibitor treated | https://cloud.uni-konstanz.de/index.php/s/kX7Z3PoZ2g2qHyC | Segments_BMP/-C001--PO01/ | n/a |
| Deviation of development between groups of drug-treated embryos, Nodal-inhibitor treated | https://cloud.uni-konstanz.de/index.php/s/eFGpMn9bTPncQc7 | Segments_Nodal/C002/ | n/a |
| Autoregression C. elegans | | | n/a |
| Autoregression Medaka | | | n/a |
| Autoregression Stickleback | | | n/a |
| Autoregression Zebrafish | https://dx.doi.org/10.48606/82 | TwinNetworkDataset024/-A003--PO01/E003/ | n/a |
| Image segmentation | [Segmentation demo data](https://github.com/mueller-lab/TwinNet/tree/main/data/segmentation_data/) | Demo test data is stored in the [dataset folder](https://github.com/mueller-lab/TwinNet/tree/main/data/segmentation_data/)| n/a |
