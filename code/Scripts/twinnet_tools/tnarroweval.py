import cv2
import glob
import numpy as np
import os
import pandas as pd
import pathlib
import re
import tensorflow as tf

from .tninference import TNToolsSimilarities


class TNToolsArrowEval:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used with tools in 'tnarrow.py' and
    'tnarrowplot.py' to utilize TN predicted developmental stages for
    detection of deviation from normal development.
    """
    def __init__(self, size_img=224, size_img_min=300):
        self.format_ljust = 50
        self.TNHelperTools = TNToolsArrowEvalHelperTools(size_img,
                                                         size_img_min)
        self.tools_similarities = TNToolsSimilarities()

    def embeddings_reference_get(self,
                                 model_embedding,
                                 paths_images_1,
                                 paths_images_2,
                                 paths_images_3):
        """Calculate embeddings for reference images."""
        embeddings_1 = self.TNHelperTools.embedding_multiple_get(
            model_embedding, paths_images_1
        )
        embeddings_2 = self.TNHelperTools.embedding_multiple_get(
            model_embedding, paths_images_2
        )
        embeddings_3 = self.TNHelperTools.embedding_multiple_get(
            model_embedding, paths_images_3
        )

        return embeddings_1, embeddings_2, embeddings_3

    def embeddings_test_get(self, model_embedding, dirs_embryos_test):
        """Calculate embeddings for test images."""
        # Prepare dictionary for embeddings
        embeddings_test = dict()

        # Loop through test embryo categories
        for k_cat, v_cat in dirs_embryos_test.items():
            embeddings_test[k_cat] = dict()
            num_embryos = len(v_cat)
        # Loop through test embryo directories of category
            for i in range(len(v_cat)):
                # Print info
                print(f"[INFO][{k_cat}] {str(i + 1).zfill(3)}/{num_embryos}"
                      .ljust(self.format_ljust))

                # Get path to embryo directory
                dir_embryo_test = v_cat[i]

                # Load image paths
                paths_images = glob.glob(os.path.join(dir_embryo_test,
                                                      '*CO6*.tif'))

                # Create an embryo key based on embryo name and position
                p_emb = pathlib.PurePath(dir_embryo_test)
                k_emb = f"{p_emb.parent.stem}--{p_emb.stem}"

                # Calculate embeddings
                embeddings_test[k_cat][k_emb] =\
                    self.TNHelperTools.embedding_multiple_get(
                        model_embedding,
                        paths_images
                    )
        return embeddings_test

    @staticmethod
    def cos_sim_embeddings_both(embeddings_1,
                                embeddings_2,
                                embeddings_3,
                                embedding_test,
                                verbose=0):
        """
        Calculate cosine similarity values between one test embedding
        and three reference embeddings.
        """
        cosine_similarity = tf.keras.metrics.CosineSimilarity()

        anchor_sim_1 = cosine_similarity(
            embeddings_1, embedding_test
        )
        anchor_sim_2 = cosine_similarity(
            embeddings_2, embedding_test
        )
        anchor_sim_3 = cosine_similarity(
            embeddings_3, embedding_test
        )

        if verbose == 0:
            pass
        else:
            print("Anchor similarity 1:", anchor_sim_1.numpy())
            print("Anchor similarity 2:", anchor_sim_2.numpy())
            print("Anchor similarity 3:", anchor_sim_3.numpy())

        return anchor_sim_1, anchor_sim_2, anchor_sim_3

    def similarities_calc_to_df_embeddings_both(self,
                                                embeddings_1,
                                                embeddings_2,
                                                embeddings_3,
                                                embedding_test,
                                                verbose=False):
        """
        Calculate similarities for all images in lists of images and
        return dataframe containing similarities.

        First assert that the numbers of images are equal in all three input
        arrays of images. Second, loop through the anchor images and compute
        cosine similarities between the test image and each image from a set
        of 3 anchor images for each index in the list of reference embryos.
        Append similarities to dataframe. Following, compute standard
        deviation and mean for all rows in the dataframe, corresponding to
        the image indices in the list of reference embryos.
        """
        df = pd.DataFrame(columns=['Anch_sim_1', 'Anch_sim_2', 'Anch_sim_3'])
        num_keys_ref_1 = len(list(embeddings_1.keys()))
        num_keys_ref_2 = len(list(embeddings_2.keys()))
        num_keys_ref_3 = len(list(embeddings_3.keys()))
        assert num_keys_ref_1 == num_keys_ref_2, \
            'Number of images not equal (embeddings_1, embeddings_2).'
        assert num_keys_ref_1 == num_keys_ref_3, \
            'Number of images not equal (embeddings_1, embeddings_3).'

        i = 0
        for emb_1, emb_2, emb_3 in zip(embeddings_1.values(),
                                       embeddings_2.values(),
                                       embeddings_3.values()):
            anch_sim_1, anch_sim_2, anch_sim_3 = self.cos_sim_embeddings_both(
                emb_1,
                emb_2,
                emb_3,
                embedding_test
            )
            df.loc[i] = [anch_sim_1.numpy(),
                         anch_sim_2.numpy(),
                         anch_sim_3.numpy()]
            i += 1
            if verbose:
                print(f'[LOADING][Dataframe] Row {str(i + 1).zfill(3)}.',
                      end='\r')
            else:
                pass

        df_std = df.std(axis=1)
        df_mean = df.mean(axis=1)
        df['Std'] = df_std
        df['Mean'] = df_mean

        return df


class TNToolsArrowEvalHelperTools:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used with tools in 'tnarrow.py' and
    'tnarrowplot.py' to utilize TN predicted developmental stages for
    detection of deviation from normal development.
    """
    def __init__(self, size_img, size_img_min):
        self.img_height_cut = size_img_min
        self.img_width_cut = size_img_min
        self.img_shape = (size_img, size_img)

    @staticmethod
    def center_fn(img):
        """Calculate center of image array."""
        return int(img.shape[0] / 2), int(img.shape[1] / 2)

    @staticmethod
    def df_save(df, path_save, name_df):
        """Save dataframe as '.csv' file to specified filepath."""
        try:
            df.to_csv(os.path.join(path_save, name_df))

        except FileExistsError as fee:
            print('[ERROR] TwinNetworkHelperTools/df_save \n', fee)
        except OSError as ose:
            print('[ERROR] TwinNetworkHelperTools/df_save \n', ose)
        except Exception as e:
            print('[ERROR] TwinNetworkHelperTools/df_save \n', e)

    @staticmethod
    def embedding_single_get(model_embedding, array):
        """Calculate embedding for array."""
        embedding = model_embedding(
            tf.keras.applications.resnet.preprocess_input(array)
        )
        return embedding

    def embedding_multiple_get(self, model_embedding, paths_images):
        """Get embeddings for multiple images and return as dictionary."""
        embeddings_batches = list()
        embeddings = dict()
        timepoints = list()
        imgs = list()
        size_batch = 20

        for path_image in paths_images:
            timepoints.append(self.timepoint_extract_fn(path_image))
            img = self.image_load(path_image)
            imgs.append(img)

        imgs = np.array(imgs)
        imgs = [imgs[i:i+size_batch, :, :, :]
                for i in range(0,
                               imgs.shape[0],
                               size_batch)
                ]

        for i in range(len(imgs)):
            b_img = imgs[i]
            embedding = self.embedding_single_get(model_embedding,
                                                  np.array(b_img))
            embeddings_batches.extend(embedding)
            print(str(i).zfill(3), end='\r')

        for k, v in zip(timepoints, embeddings_batches):
            embeddings[k] = v

        return embeddings

    def image_load(self, path_img):
        """Load image array."""
        img = cv2.imread(path_img, cv2.IMREAD_COLOR)
        centerx, centery = self.center_fn(img)
        img = img[int(centery - self.img_width_cut / 2):
                  int(centery + self.img_width_cut / 2),
                  int(centerx - self.img_width_cut / 2):
                  int(centerx + self.img_width_cut / 2)]
        img = cv2.resize(img, self.img_shape)
        assert img.shape == self.img_shape + (3,)

        return img

    @staticmethod
    def timepoint_extract_fn(path_image):
        """Return image index based on image name as integer."""
        pattern_timepoint = '--LO(.*)--CO'
        name_file = os.path.basename(path_image)
        try:
            timepoint = int(re.search(pattern_timepoint, name_file)
                            .group()[4:8])
            return timepoint
        except ValueError:
            timepoint = int(re.search(pattern_timepoint, name_file)
                            .group()[4:7])
            return timepoint
        except Exception as e:
            print(e)
