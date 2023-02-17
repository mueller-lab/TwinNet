import cv2
import json
import glob
import numpy as np
import os
import random
import re
import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow_io as tfio


class DatasetCreator:

    def __init__(self, batch_size, buffer_size, img_height, img_height_min, img_width, img_width_min):
        self.batch_size = batch_size
        self.buffer_size = buffer_size

        self.img_height = img_height
        self.img_height_min = img_height_min
        self.img_width = img_width
        self.img_width_min = img_width_min

        self.it = ImageTools(img_height, img_height_min, img_width, img_width_min)
        self.pg = PathsGenerator(img_height, img_height_min, img_width, img_width_min)

    @staticmethod
    def generator_fn(paths, labels):
        """Generate dataset from image paths and labels.

        Parameters
        ----------
        paths: list
            Filepaths of images to be included in dataset.
        labels: list
            Labels of images to be included in dataset.

        Yields
        ------
        path_pair: list
            Two tensorflow.python.framework.ops.Tensors with path to image file.
        label: int
            Label corresponding to image paths.
        """
        for path_pair, label in zip(paths, labels):
            input_1 = path_pair[0]
            input_2 = path_pair[1]
            yield {'input_1': input_1, 'input_2': input_2}, label

    def performance_fn(self, ds):
        """Adjust dataset for improved training speed."""
        ds = ds.shuffle(self.buffer_size)
        ds = ds.batch(self.batch_size)
        ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)

        return ds

    def dataset_prepare(self, paths, labels, from_gen=False):
        """Generate tf.data.Dataset.from_tensor_slices from image paths and labels.

        Parameters
        ----------
        paths: list
            Filepaths of images to be included in dataset.
        labels: list
            Labels of images to be included in dataset.
        from_gen: bool
            Boolean indicating which type of dataset should be used.
            If true, dataset will be created from generator.

        Returns
        -------
        ds: tf.data.Dataset
            Tensorflow dataset with mapped function for image loading.
        """
        print(len(paths[:, 0]))
        if from_gen:
            ds = tf.data.Dataset.from_generator(self.generator_fn,
                                                args=(paths, labels),
                                                output_types=({"input_1": tf.string,
                                                               "input_2": tf.string},
                                                              tf.float32))
        else:
            ds_images = tf.data.Dataset.from_tensor_slices({'input_1': paths[:, 0],
                                                            'input_2': paths[:, 1]})
            ds_labels = tf.data.Dataset.from_tensor_slices(labels)
            ds = tf.data.Dataset.zip((ds_images, ds_labels))

        print("\033[1m" + "Number of files total" + "\033[0m:\t\t\t",
              tf.data.experimental.cardinality(ds).numpy())
        # ds = ds.map(self.it.parse_double_fn)

        return ds

    def dataset_procedure(self, paths, labels, from_gen=False):
        """
        Convenience function to split dataset and
        apply augmentation and performance functions.

        Parameters
        ----------
        paths: list
            Filepaths of images to be included in dataset.
        labels: list
            Labels of images to be included in dataset.
        from_gen: bool
            Boolean indicating which type of dataset should be used.
            If true, dataset will be created from generator.

        Returns
        -------
        ds_train: tf.data.Dataset
            Dataset with no augmentation method.
        ds_test: tf.data.Dataset
            Dataset with no augmentation method.
        """
        ds = self.dataset_prepare(paths, labels, from_gen)

        num_test = int(tf.data.experimental.cardinality(ds).numpy() * 0.1)
        print("\033[1m" + "Number of files train" + "\033[0m:\t\t\t",
              tf.data.experimental.cardinality(ds).numpy() - num_test)
        print("\033[1m" + "Number of files test" + "\033[0m:\t\t\t",
              num_test)

        ds_test = ds.take(num_test)
        ds_train = ds.skip(num_test)

        ds_train = self.performance_fn(ds_train)
        ds_test = self.performance_fn(ds_test)

        return ds_train, ds_test


class ImageTools:

    def __init__(self, img_height, img_height_min, img_width, img_width_min):
        self.img_height = img_height
        self.img_height_min = img_height_min
        self.img_width = img_width
        self.img_width_min = img_width_min

    @staticmethod
    def augment__brightness_contrast_fn(img):
        """Apply random brightness and contrast to image."""
        img = tf.image.random_brightness(img, 0.2)
        img = tf.image.random_contrast(img, 0.5, 2.0)
        return img

    def augment_crop_fn(self, img):
        """Crop image to random size and resize back to class variables img_height and img_width."""
        size = random.randint(int(self.img_height * 0.85), self.img_height - 1)
        img = tf.image.random_crop(img, size=(size, size, 3))
        img = tf.image.resize(img, (self.img_height, self.img_width))
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
        """Combine horizontal flip, vertical flip and random contrast and brightness."""
        img = self.augment_flip_lr_fn(img)
        img = self.augment_flip_ud_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_combined_two_fn(self, img):
        """Combine horizontal flip, random crop and random contrast and brightness."""
        img = self.augment_flip_lr_fn(img)
        img = self.augment_crop_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_combined_three_fn(self, img):
        """Combine vertical flip, random crop and random contrast and brightness."""
        img = self.augment_flip_ud_fn(img)
        img = self.augment_crop_fn(img)
        img = self.augment__brightness_contrast_fn(img)
        return img

    def augment_combined_four_fn(self, img):
        """Combine rotation, random crop and random contrast and brightness."""
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

        img = tf.image.resize_with_crop_or_pad(img, self.img_height_min, self.img_width_min)
        img = tf.image.resize(img, (self.img_height, self.img_width))
        img = tf.reshape(img, (self.img_height, self.img_width, 4))
        img = tfio.experimental.color.rgba_to_rgb(img)
        # img = tf.image.rgb_to_grayscale(img)
        return img


class PathsGenerator:

    def __init__(self, img_height, img_height_min, img_width, img_width_min):
        self.img_height = img_height
        self.img_height_min = img_height_min
        self.img_width = img_width
        self.img_width_min = img_width_min
        self.timepoint_limit = 400
        self.max_timepoint_variation = 1

    @staticmethod
    def exclude_fn(list_paths_jsons_exclude):
        """Read json file specifying which, if any, embryo  directories should be excluded from dataset.

        Parameters
        ----------
        list_paths_jsons_exclude: list
            List of paths to json files specifying embryo dirs to be excluded from directory.

        Returns
        -------
        paths_to_exclude: list
            Filepaths of embryo subdirectories within dataset directory to be excluded from dataset.
        """
        paths_to_exclude = []

        for path_json_exclude in list_paths_jsons_exclude:
            with open(path_json_exclude, 'rb') as json_exclude:
                paths_to_exclude += json.load(json_exclude)

        return paths_to_exclude

    @staticmethod
    def filter_embryo_fn(paths_embryos, paths_to_exclude):
        """Discard embryo directories that are listed in 'paths_to_exclude'.

        Checks if list  of embryos to be excluded from dataset is empty. Second
        loops through paths_embryos and checks if single embryo dir path is in
        paths_to_exclude. Third checks if fileformat of files in embryo subdirectory
        is correct.

        Parameters
        ----------
        paths_embryos: list
            Filepaths of all embryo subdirectories within dataset directory.
        paths_to_exclude: list
            Filepaths of embryo subdirectories within dataset directory to be excluded from dataset.

        Returns
        -------
        paths_embryos_filtered: list
            Filepaths of embryo subdirectories within dataset directory to be included in dataset.
        """
        paths_embryos_filtered = list()
        num_passing = 0
        for path_embryo in paths_embryos:
            if path_embryo.replace('\\', '/') + '/' in paths_to_exclude:
                num_passing += 1
                pass
            else:
                paths_embryos_filtered.append(path_embryo)
        print('[INFO] Passing on {} embryo directories.'.format(num_passing))
        return paths_embryos_filtered

    def filter_fileformat_fn(self, path):
        """Function to check if format of specified file is correct.

        This function was implemented in order to exclude 'cut off' embryos, i.e.
        embryos located at the edge of the images, from dataset. First, checks if
        sizes of image height and image width are vary within 20 % of their sizes.
        Second, checks if size of image height or image width is large enough, based
        on class variables img_height and img_width.

        Parameters
        ----------
        path: str
            Filepath of image file.

        Returns
        -------
        keep: bool
            Boolean indicating whether format of file complies with standards.
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
        """Generate dict key of similar timepoint and different timepoint.

        Parameters
        ----------
        key_root: int
            Key of dict where root image is located.
        max_label: int
            Highest possible key in dict with filepaths.

        Returns
        -------
        key_positive: int
            Key for dict where filepath for image from similar timepoint might be located.
        key_negative: int
            Key for dict where filepath for image from different timepoint might be located.
        """
        if key_root + self.max_timepoint_variation > max_label:
            variation = random.randint(-1 * self.max_timepoint_variation,
                                       (max_label - key_root))
            key_positive = key_root + variation
            key_negative = key_root - random.randint(1, key_root - self.max_timepoint_variation)
        elif key_root - self.max_timepoint_variation < 1:
            variation = random.randint(-1 * (key_root - 1),
                                       self.max_timepoint_variation)
            key_positive = key_root + variation
            key_negative = key_root + random.randint(key_root + self.max_timepoint_variation, max_label)
        else:
            variation = random.randint(-1 * self.max_timepoint_variation,
                                       self.max_timepoint_variation)
            key_positive = key_root + variation

            if random.randint(0, 1):
                key_negative = key_root - random.randint(1, key_root - self.max_timepoint_variation)
            else:
                key_negative = key_root + random.randint(key_root + self.max_timepoint_variation, max_label)

        return key_positive, key_negative

    def label_fn(self, paths_complete):
        """Extract image loop timepoint of acquisition based on image name.

        Each path of image should contain a string in the following format:
        '*--LO' followed by timepoint followed by '--CO*', where timepoint
        represent the number of loop during which the image was acquired.

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
        pattern_timepoint = '--LO(.*)'
#        pattern_timepoint = '--LO(.*)--'

        for path in paths_complete:
            name_file = os.path.basename(path)
 #           print(re.search(pattern_timepoint, name_file).group())
            timepoint = int(re.search(pattern_timepoint, name_file).group()[4:8])
            #print(timepoint)
            # if int(timepoint) <= 340:
            #     timepoint = int(math.ceil(int(timepoint) / 10)) - 1  # Loop timestamps start at 1
            # else:
            #     timepoint = 35 - 1
            # label = [.0] * 35
            # label[timepoint] = 1.0
            # labels.append(label)
            if timepoint < self.timepoint_limit:
                if timepoint in labels:
                    labels[timepoint] += [path]
                else:
                    labels[timepoint] = [path]
                # labels[path] += [timepoint]
        return labels

    def pair_fn(self, labels, num_pairs):
        """Build labeled image-pairs for training with siamese networks.

        Parameters
        ----------
        labels: dict
            Image labels extracted from image name.
        num_pairs: int
            Number of image pairs to be returned,
            i.e. the number of training instances in the dataset.

        Returns
        -------
        pair_paths: numpy array
            Pairs of image paths to be contained in dataset.
        label_distances: numpy array
            Distances of original image labels of image pairs.
            Intentionally not the euclidean distance.
        """
        pair_paths = list()
        label_distances = list()

        for i in range(1, num_pairs + 1):
            print(i, end='\r')
            source_1 = random.choice(list(labels.keys()))
            label_1 = labels[source_1]

            source_2 = random.choice(list(labels.keys()))
            label_2 = labels[source_2]

            pair_paths.append([source_1, source_2])
            if label_1 != label_2:
                label_distances.append(int(label_2 - label_1) / self.timepoint_limit)
            else:
                label_distances.append(0)

        return np.array(pair_paths), np.array(label_distances)

    def pair_binary_fn(self, labels, num_pairs):
        """Build labeled image-pairs for training with siamese networks.

        Parameters
        ----------
        labels: dict
            Image labels extracted from image name.
        num_pairs: int
            Number of image pairs to be returned,
            i.e. the number of training instances in the dataset.

        Returns
        -------
        pair_paths: numpy array
            Pairs of image paths to be contained in dataset.
        label_distances: numpy array
            Distances of original image labels of image pairs.
            Intentionally not the euclidean distance.
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
                key_positive, key_negative = self.key_fn(key_root, max_label)
                if key_positive in labels.keys() and key_negative in labels.keys():
                    no_key = False

            source_root = random.choice(labels[key_root])
            source_positive = random.choice(labels[key_positive])
            source_negative = random.choice(labels[key_negative])

            paths_anchor.append(source_root)
            paths_positive.append(source_positive)
            paths_negative.append(source_negative)
            num_total += 1
            print('[INFO] Labeling images: {}'.format(num_total), end='\r')
        return paths_anchor, paths_positive, paths_negative

    @staticmethod
    def pair_binary_eval_fn(labels):
        """Build labeled image-pairs for evaluation of siamese networks.

        This function differs from 'pair_binary_fn' only by its selection of key_root.
        Here, all keys are represented by looping through the keys, while
        in 'pair_binary_fn' a random key is drawn from all keys, thus it is possible
        that a single key is not represented.

        Parameters
        ----------
        labels: dict
            Image labels extracted from image name.

        Returns
        -------
        pair_paths: numpy array
            Pairs of image paths to be contained in dataset.
        label_distances: numpy array
            Distances of original image labels of image pairs.
            Intentionally not the euclidean distance.
        """
        paths_anchor_1 = list()
        paths_anchor_2 = list()
        paths_anchor_3 = list()

        num_total = 0

        for key_root in list(labels.keys()):
            source_anchor_1 = random.choice(labels[key_root])
            source_anchor_2 = random.choice(labels[key_root])
            source_anchor_3 = random.choice(labels[key_root])

            paths_anchor_1.append(source_anchor_1)
            paths_anchor_2.append(source_anchor_2)
            paths_anchor_3.append(source_anchor_3)

            num_total += 1
            print('[INFO] Labeling images: {}'.format(num_total), end='\r')
        return paths_anchor_1, paths_anchor_2, paths_anchor_3

    @staticmethod
    def paths_embryos_glob(list_paths_datasets_directories):
        """Glob through dataset directory and get all paths of embryo subdirectories.

        Embryo directories can later be used to assess whether selected directories should be
        excluded from dataset generation.

        Parameters
        ----------
        list_paths_datasets_directories: list
            List of filepaths to the dataset directories, i.e. directories containing well subdirectories.

        Returns
        -------
        paths_embryos: list
            Filepaths of all embryo subdirectories within dataset directory.
        """
        print("Analizing paths")
        paths_embryos = list()
        for path_dataset_directory in list_paths_datasets_directories:            	
            pattern_glob = path_dataset_directory + '/*/E*'
            paths_embryos += sorted(glob.glob(pattern_glob))
        return paths_embryos

    def paths_files_glob(self, paths_embryos_filtered):
        """Glob through embryo subdirectories and get paths of files within embryo subdirectories.

        Parameters
        ----------
        paths_embryos_filtered: list
            Filepaths of embryo subdirectories within dataset directory to be included in dataset.

        Returns
        -------
        paths_complete: list
            Filepaths of images to be included in dataset.
        """
        paths_complete = list()
        for path_embryo_filtered in paths_embryos_filtered:
            pattern_glob = path_embryo_filtered + '/*.tif'
            #print(pattern_glob)
            paths_images = sorted(glob.glob(pattern_glob))
            #print(paths_images[0])    
            #print(self.filter_fileformat_fn(paths_images[0]))        
            keep = self.filter_fileformat_fn(paths_images[0])
            if keep:
                paths_complete += paths_images
        return paths_complete

    def procedure_paths(self, list_paths_datasets_directories, list_paths_jsons_exclude, num_pairs=100):
        """Convenience function to get filepaths for dataset preparation.

        Parameters
        ----------
        list_paths_datasets_directories: list
            List of filepaths to the dataset directories, i.e. directories containing well subdirectories.
        list_paths_jsons_exclude: list
            List of paths to json files specifying embryo dirs to be excluded from directory.
        num_pairs: int
            Number of image pairs to be returned,
            i.e. the number of training instances in the dataset.

        Returns
        -------
        pair_paths: list
            Pairs of image paths to be contained in dataset.
        label_distances: list
            Euclidean distances of original image labels of image pairs.
        """
        # Step 1: Get paths of all embryo directories
        paths_embryos = self.paths_embryos_glob(list_paths_datasets_directories)
        # Step 2: Get paths of embryos to exclude from dataset
        paths_to_exclude = self.exclude_fn(list_paths_jsons_exclude)
        # Step 3: Filter paths based on exclude list
        paths_embryos_filtered = self.filter_embryo_fn(paths_embryos, paths_to_exclude)
        # Step 4: Get paths of images in filtered embryo directories
        paths_complete = self.paths_files_glob(paths_embryos_filtered)
        # Step 5: Extract labels
        labels = self.label_fn(paths_complete)
        # Step 6: Get image pairs and labels
        pair_paths, label_distances = self.pair_fn(labels, num_pairs=num_pairs)

        return pair_paths, label_distances

    def procedure_paths_binary(self, list_paths_datasets_directories, list_paths_jsons_exclude, num_pairs=100):
        """Convenience function to get filepaths for dataset preparation.

        Parameters
        ----------
        list_paths_datasets_directories: list
            List of filepaths to the dataset directories, i.e. directories containing well subdirectories.
        list_paths_jsons_exclude: list
            List of paths to json files specifying embryo dirs to be excluded from directory.
        num_pairs: int
            Number of image pairs to be returned,
            i.e. the number of training instances in the dataset.

        Returns
        -------
        pair_paths: list
            Pairs of image paths to be contained in dataset.
        label_distances: list
            Euclidean distances of original image labels of image pairs.
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
        # Step 6: Get image pairs and labels
        # pair_paths_labels = self.pair_binary_fn(labels, num_pairs=num_pairs)
        paths_anchor, paths_positive, paths_negative = self.pair_binary_fn(labels, num_pairs=num_pairs)

        return paths_anchor, paths_positive, paths_negative
