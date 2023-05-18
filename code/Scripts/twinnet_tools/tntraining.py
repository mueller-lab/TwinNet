import cv2
import json
import glob
import os
import random
import re
import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow_io as tfio


class TNToolsTrainingImages:

    def __init__(self,
                 img_height,
                 img_height_min,
                 img_width,
                 img_width_min):
        self.img_height = img_height
        self.img_height_min = img_height_min
        self.img_width = img_width
        self.img_width_min = img_width_min

    @staticmethod
    def augment__brightness_contrast_fn(img):
        """
        Apply random brightness and contrast to image.
        """
        img = tf.image.random_brightness(img, 0.2)
        img = tf.image.random_contrast(img, 0.5, 2.0)
        return img

    def augment_crop_fn(self, img):
        """
        Crop image to random size and resize back to
        class variables img_height and img_width.
        """
        size = random.randint(int(self.img_height * 0.85),
                              self.img_height - 1)
        img = tf.image.random_crop(img,
                                   size=(size, size, 3))
        img = tf.image.resize(img,
                              (self.img_height, self.img_width))
        return img

    @staticmethod
    def augment_flip_lr_fn(img):
        """Flip image horizontally."""
        img = tf.image.random_flip_left_right(img)
        return img

    @staticmethod
    def augment_flip_ud_fn(img):
        """Flip image vertically."""
        img = tf.image.random_flip_up_down(img)
        return img

    @staticmethod
    def augment_rotate(img):
        """Rotate image."""
        angle = tf.cast(random.randint(0, 360), tf.float32)
        img = tfa.image.rotate(img, angle)
        return img

    def augment_combined_one_fn(self, img):
        """
        Combine horizontal flip, vertical flip and
        random contrast and brightness.
        """
        img = self.augment_flip_lr_fn(img)
        img = self.augment_flip_ud_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_combined_two_fn(self, img):
        """
        Combine horizontal flip, random crop and
        random contrast and brightness.
        """
        img = self.augment_flip_lr_fn(img)
        img = self.augment_crop_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_combined_three_fn(self, img):
        """
        Combine vertical flip, random crop and
        random contrast and brightness.
        """
        img = self.augment_flip_ud_fn(img)
        img = self.augment_crop_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_combined_four_fn(self, img):
        """
        Combine rotation, random crop and
        random contrast and brightness.
        """
        img = self.augment_rotate(img)
        img = self.augment_crop_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_triple_one(self, path1, path2, path3):
        img_1 = self.parse_fn(path1)
        img_1 = self.augment_combined_one_fn(img_1)
        img_2 = self.parse_fn(path2)
        img_2 = self.augment_combined_one_fn(img_2)
        img_3 = self.parse_fn(path3)
        img_3 = self.augment_combined_one_fn(img_3)

        return img_1, img_2, img_3

    def augment_triple_two(self, path1, path2, path3):
        img_1 = self.parse_fn(path1)
        img_1 = self.augment_combined_two_fn(img_1)
        img_2 = self.parse_fn(path2)
        img_2 = self.augment_combined_two_fn(img_2)
        img_3 = self.parse_fn(path3)
        img_3 = self.augment_combined_two_fn(img_3)

        return img_1, img_2, img_3

    def parse_triple_fn(self, path1, path2, path3):
        """Load three images from path.

        Parameters
        ----------
        path1: tensorflow.python.framework.ops.Tensors
            Path to image file.
        path2: tensorflow.python.framework.ops.Tensors
            Path to image file.
        path3: tensorflow.python.framework.ops.Tensors
            Path to image file.


        Returns
        -------
        img_1: tensorflow.python.framework.ops.Tensor
            Decoded grayscale image file of dtype tf.float32.
        img_2: tensorflow.python.framework.ops.Tensor
            Decoded grayscale image file of dtype tf.float32.
        img_3: tensorflow.python.framework.ops.Tensor
            Decoded grayscale image file of dtype tf.float32.
        """
        img_1 = self.parse_fn(path1)
        img_2 = self.parse_fn(path2)
        img_3 = self.parse_fn(path3)

        return img_1, img_2, img_3

    def parse_fn(self, path):
        """Load image from path.

        Parameters
        ----------
        path: tensorflow.python.framework.ops.Tensor
            Path to image file.

        Returns
        -------
        img: tensorflow.python.framework.ops.Tensor
            Decoded RGBA image file of dtype tf.float32.
        label: tensorflow.python.framework.ops.Tensor
            Label to corresponding image, unchanged.
        """
        img = tf.io.read_file(path)
        img = tfio.experimental.image.decode_tiff(img)
        img = tf.cast(img, tf.float32)

        img = tf.image.resize_with_crop_or_pad(img,
                                               self.img_height_min,
                                               self.img_width_min)
        img = tf.image.resize(img,
                              (self.img_height, self.img_width))
        img = tf.reshape(img,
                         (self.img_height, self.img_width, 4))
        img = tfio.experimental.color.rgba_to_rgb(img)
        return img


class TNToolsTrainingPaths:

    def __init__(self,
                 img_height,
                 img_height_min,
                 img_width,
                 img_width_min,
                 **kwargs):
        self.img_height = img_height
        self.img_height_min = img_height_min
        self.img_width = img_width
        self.img_width_min = img_width_min
        self.index_limit = 400
        self.max_timepoint_variation = 1
        self.pattern_glob_files = kwargs.get("pattern_glob_files",
                                             "*.tif")
        self.pattern_index = kwargs.get("pattern_index",
                                        "--LO(\d+)")
        self.pattern_index_start = int(kwargs.get("pattern_index_start",
                                                  4))

    @staticmethod
    def exclude_fn(list_paths_jsons_exclude):
        """
        Read json files specifying which, if any,
        embryo directories should be excluded from
        the dataset.

        Parameters
        ----------
        list_paths_jsons_exclude: list
            File paths to json files specifying
            embryo directories to be excluded from
            the dataset.

        Returns
        -------
        paths_to_exclude: list
            Directory paths of embryo subdirectories
            within the dataset directory to be excluded
            from the dataset.
        """
        paths_to_exclude = []

        for path_json_exclude in list_paths_jsons_exclude:
            with open(path_json_exclude, 'rb') as json_exclude:
                paths_to_exclude += json.load(json_exclude)

        return paths_to_exclude

    @staticmethod
    def filter_embryo_fn(paths_embryos, paths_to_exclude):
        """
        Remove embryo directories that are listed in
        'paths_to_exclude' from "paths_embryos".

        Checks if the list of embryos to be excluded from
        the dataset is empty. Second, checks for each
        directory path in paths_embryos if it is in paths_to_exclude.
        Third checks if the file format of the files in the embryo
        subdirectory is correct.

        Parameters
        ----------
        paths_embryos: list
            Directory paths of all embryo subdirectories
            within the dataset directory.
        paths_to_exclude: list
            Directory paths of embryo subdirectories within
            the dataset directory to be excluded from the dataset.

        Returns
        -------
        paths_embryos_filtered: list
            Directory paths of embryo subdirectories within
            the dataset directory to be included in the dataset.
        """
        paths_embryos_filtered = list()
        num_passing = 0
        for path_embryo in paths_embryos:
            if path_embryo.replace('\\', '/') + '/' in paths_to_exclude:
                num_passing += 1
                pass
            else:
                paths_embryos_filtered.append(path_embryo)
        print(f'[INFO] Excluding {num_passing} embryo directories.')
        return paths_embryos_filtered

    def filter_fileformat_fn(self, path):
        """
        Method to check if the format of specified file
        is correct.

        This function was implemented to exclude 'cut off'
        embryos, i.e. embryos located at the edge of the
        images, from the dataset. First, checks if the sizes
        of image height and image width vary within 20 %
        of their sizes. Second, checks if the size of the
        image height or image width is large enough, based
        on class variables img_height and img_width.

        Parameters
        ----------
        path: str
            File path of image file.

        Returns
        -------
        keep: bool
            Boolean indicating whether file should be included
            in the dataset based on the file format assessment.
        """
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        shape_y, shape_x = img.shape
        
        keep = True
#        if shape_x * 0.8 > shape_y or shape_y * 0.8 > shape_x:
#            keep = False
#        else:
#            if shape_x < self.img_height_min or shape_x < self.img_width_min:
#                keep = False
#            else:
#                if shape_y < self.img_height_min or shape_y < self.img_width_min:
#                    keep = False
#                else:
#                    keep = True
        return keep

    def key_fn(self, key_root, max_label):
        """
        Generate a dictionary key of a similar image index
        and different image index.

        Parameters
        ----------
        key_root: int
            Key of dict where root image is located.
        max_label: int
            The highest possible key in the dictionary
            containing image filepaths.

        Returns
        -------
        key_positive: int
            Key for dictionary where filepath for image
            from similar image index might be located.
        key_negative: int
            Key for dictionary where filepath for image
            from different image index might be located.
        """
        if key_root + self.max_timepoint_variation > max_label:
            variation = random.randint(
                -1 * self.max_timepoint_variation,
                (max_label - key_root)
            )
            key_positive = key_root + variation
            key_negative = key_root - random.randint(
                1, key_root - self.max_timepoint_variation
            )

        elif key_root - self.max_timepoint_variation < 1:
            variation = random.randint(
                -1 * (key_root - 1),
                self.max_timepoint_variation
            )
            key_positive = key_root + variation
            key_negative = key_root + random.randint(
                key_root + self.max_timepoint_variation, max_label
            )

        else:
            variation = random.randint(
                -1 * self.max_timepoint_variation,
                self.max_timepoint_variation
            )
            key_positive = key_root + variation

            if random.randint(0, 1):
                key_negative = key_root - random.randint(
                    1, key_root - self.max_timepoint_variation
                )
            else:
                key_negative = key_root + random.randint(
                    key_root + self.max_timepoint_variation, max_label
                )

        return key_positive, key_negative

    def label_fn(self, paths_complete):
        """
        Extract the image index of the acquisition based on
        the image name.

        Each image file path should contain a string indicating
        the image's index within a time series acquisition
        in the following format: '*--LO', followed by a three-digit
        index, followed by '--CO*', where the index number represents
        the number of the loop during which the image was acquired.

        Parameters
        ----------
        paths_complete: list
            Filepaths of images to be included in dataset.

        Returns
        -------
        labels: dict
            Image labels extracted from image name.
        """
        labels = dict()

        for path in paths_complete:
            name_file = os.path.basename(path)
            index = int(re.search(self.pattern_index,
                                  name_file).group()[self.pattern_index_start:])
            if index < self.index_limit:
                if index in labels:
                    labels[index] += [path]
                else:
                    labels[index] = [path]
        return labels

    def pair_binary_fn(self, labels, num_pairs):
        """
        Build labeled image pairs for training with
        twin networks.

        Parameters
        ----------
        labels: dict
            Image labels extracted from image name.
        num_pairs: int
            Number of image pairs to be returned,
            i.e. the number of training instances
            in the dataset.

        Returns
        -------
        paths_anchor: list
            File paths of anchor images.
        paths_positive: list
            File paths of positive images.
        paths_negative: list
            File paths of negative images.
        """
        paths_anchor = list()
        paths_positive = list()
        paths_negative = list()
        max_label = max(list(labels.keys()))

        num_total = 0

        while num_total < num_pairs:
            key_root = random.choice(list(labels.keys()))
            no_key = True

            while no_key:
                key_positive, key_negative = self.key_fn(
                    key_root,
                    max_label
                )

                if key_positive in labels.keys() \
                        and key_negative in labels.keys():
                    no_key = False

            source_root = random.choice(labels[key_root])
            source_positive = random.choice(labels[key_positive])
            source_negative = random.choice(labels[key_negative])

            paths_anchor.append(source_root)
            paths_positive.append(source_positive)
            paths_negative.append(source_negative)
            num_total += 1
            if num_total % 1000 == 0:
                print(f'[INFO] Labeling images: {num_total}',
                      end='\r')
        return paths_anchor, paths_positive, paths_negative

    @staticmethod
    def paths_embryos_glob(list_paths_datasets_directories):
        """
        Glob through the dataset directory and get paths
        of embryo subdirectories.

        Parameters
        ----------
        list_paths_datasets_directories: list
            Directory paths to the dataset directories,
            i.e. directories containing subdirectories
            that contain the embryo directories.

        Returns
        -------
        paths_embryos: list
            Directory paths of the embryo subdirectories
            within the dataset directory.
        """
        paths_embryos = list()
        for path_dataset_directory in list_paths_datasets_directories:            	
            pattern_glob = path_dataset_directory + '/*/E*'
            paths_embryos += sorted(glob.glob(pattern_glob))
        return paths_embryos

    def paths_files_glob(self, paths_embryos_filtered):
        """
        Glob through the embryo subdirectories and get
        the paths of files within the embryo subdirectories.

        Parameters
        ----------
        paths_embryos_filtered: list
            Directory paths of embryo subdirectories within
            the dataset directory to be included in dataset.

        Returns
        -------
        paths_complete: list
            File paths of images to be included in dataset.
        """
        paths_complete = list()
        for path_embryo_filtered in paths_embryos_filtered:
            pattern_glob = f"{path_embryo_filtered}/{self.pattern_glob_files}"
            paths_images = sorted(glob.glob(pattern_glob))
            try:
                keep = self.filter_fileformat_fn(paths_images[0])
            except IndexError:
                pass
            if keep:
                paths_complete += paths_images
        return paths_complete

    def procedure_paths_binary(self,
                               list_paths_datasets_directories,
                               list_paths_jsons_exclude,
                               num_pairs=100):
        """
        Method to get prepare three sets of image file paths,
        anchor images, positive images, and negative images,
        for image triplet dataset preparation for training
        with twin network.

        Parameters
        ----------
        list_paths_datasets_directories: list
            Directory paths to the dataset directories,
            i.e. directories containing subdirectories
            that contain the embryo directories.
        list_paths_jsons_exclude: list
            File paths to json files specifying
            embryo directories to be excluded from
            the dataset.
        num_pairs: int
            Number of image triplet sets to be returned,
            i.e. the number of training instances in
            the dataset.

        Returns
        -------
        paths_anchor: list
            File paths of anchor images.
        paths_positive: list
            File paths of positive images.
        paths_negative: list
            File paths of negative images.
        """
        # Step 1: Get paths of all embryo directories
        print('[INFO] Loading image paths.')
        paths_embryos = self.paths_embryos_glob(list_paths_datasets_directories)
        # Step 2: Get paths of embryos to exclude from dataset
        paths_to_exclude = self.exclude_fn(list_paths_jsons_exclude)
        # Step 3: Filter paths based on exclude list
        paths_embryos_filtered = self.filter_embryo_fn(paths_embryos, paths_to_exclude)
        # Step 4: Get paths of images in filtered embryo directories
        paths_complete = self.paths_files_glob(paths_embryos_filtered)
        # Step 5: Extract labels
        labels = self.label_fn(paths_complete)
        # Step 6: Get image paths sorted to anchor, positive, and negative images
        paths_anchor, paths_positive, paths_negative = self.pair_binary_fn(labels, num_pairs=num_pairs)

        return paths_anchor, paths_positive, paths_negative
