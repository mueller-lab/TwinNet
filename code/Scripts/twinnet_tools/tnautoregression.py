import numpy as np
import pandas as pd
from .tngeneral import TNToolsGeneral
from .tninference import TNToolsEmbeddings
from .tninference import TNToolsImages
from .tninference import TNToolsPaths
from .tninference import TNToolsSimilarities


class TNToolsAutoregression:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to calculate self-similarities
    at each index of a time-lapse image sequence.
    """
    def __init__(self, size_img=224, size_img_min=300):
        self.ljust = 50
        self.tools_general = TNToolsGeneral()
        self.tools_embeddings = TNToolsEmbeddings(size_img=size_img,
                                                  size_img_min=size_img_min)
        self.tools_images = TNToolsImages(size_img=size_img,
                                          size_img_min=size_img_min)
        self.tools_paths = TNToolsPaths()
        self.tools_similarities = TNToolsSimilarities()

    @staticmethod
    def fn_2d_sims_to_arrays(similarities, num_images, **kwargs):
        """
        This method maps values and positions of
        similarities to three arrays for plotting.
        """
        square = kwargs.get('square', False)
        xs = list(range(1, num_images))
        ys = list(range(1, num_images))
        xs_grid, ys_grid = np.meshgrid(xs, ys)

        # Prepare array for z values
        zs_grid_plot = np.zeros((len(xs), len(ys)))

        # Assign z values by looping through dict
        for i in range(len(similarities)):
            sims = similarities[i]

            for j in range(len(sims)):
                try:
                    zs_grid_plot[j, i] = sims[j]
                    if square:
                        zs_grid_plot[i, j] = sims[j]
                except Exception as e:
                    print(e, j, i)
        zs_grid_plot[zs_grid_plot == 0] = np.nan

        return xs_grid, ys_grid, zs_grid_plot

    @staticmethod
    def fn_3d_sims_line_plot(similarities, plot_index):
        """
        This function takes similarities of one acquisition timepoint
        calculated by image comparison with previous acquisition timepoints
        and returns values and positions in 3 arrays to be plotted as
        line plot.

        Why should we use plot_index - 2 to select the similarities
        at the "edge" of the similarity plot? We indexed images with
        1-based indexing, but similarity lists are indexed with 0-based
        indexing and should be smaller by 1 than number of images.
        """
        line_z = similarities[plot_index - 2]

        line_x = [plot_index] * len(line_z)
        # Because values on y-Axis start at frame 1
        line_y = [i for i in range(1, len(line_z) + 1)]

        return line_x, line_y, line_z

    @staticmethod
    def fn_3d_sims_to_arrays(similarities, num_images):
        """
        This function maps values and positions of
        similarities to three arrays for 3D plotting.
        """
        # x-values:
        # xs = [2, ..., maximum number of frames] based on image indices
        # xs = [1, ..., maximum number of frames - 1] based on similarity idxs
        # xs = [2, ..., maximum number of frames] for plotting
        xs = list(range(2, num_images + 1))
        # y-values
        # ys = [1, ..., id of prior-to-last image] based on image indices
        # ys = [0, ..., idx of prior-to-last image - 1] based on sim. idxs
        # ys = [1, ..., idx of prior-to-last image] for plotting
        # Exclude last image from y values as self-comparison is excluded
        ys = list(range(1, num_images))
        # Grid of x-values and grid of y-values of coordinates
        # "on the bottom" of the plot.
        xs_grid, ys_grid = np.meshgrid(xs, ys)

        # Prepare array for z values
        zs_grid_plot = np.zeros((len(xs), len(ys)))
        zs_grid_colors = zs_grid_plot.copy()

        # Assign z values by looping through dict
        for i in range(len(similarities)):
            sims = similarities[i]

            for j in range(len(sims)):
                try:
                    zs_grid_plot[j, i] = sims[j]
                    zs_grid_colors[j, i] = sims[j]
                except Exception as e:
                    print(e, j, i)
        zs_grid_plot[zs_grid_plot == 0] = np.nan
        zs_grid_colors[zs_grid_colors == 0] = 0.0

        return xs_grid, ys_grid, zs_grid_plot, zs_grid_colors

    @staticmethod
    def fn_polygon_under_graph(x, y, z):
        """
        Construct the vertex list which defines the polygon
        filling the space under the (x, y) line graph.
        This assumes x is in ascending order.

        From https://matplotlib.org/stable/gallery/mplot3d/polys3d.html.
        """
        return [(x[0], z), *zip(x, y), (x[-1], z)]

    def imgs_to_embeddings(self, model_embedding, array_images, **kwargs):
        """
        Generate embeddings from batch. This method is similar to the
        equally-named method in 'tninference.py'/TNToolsEmbeddings,
        but adds an image preprocessing step before calculating the
        embeddings.
        """
        # Prepare info string to output current state
        str_info = kwargs.get("info", "")
        # Make batches of images
        list_image_segments = self.tools_images.fn_images_slice(array_images)
        # Get number of image batches
        num_batches = len(list_image_segments)
        # Instantiate container to store embeddings
        embeddings = list()

        # Loop through image batches
        for i in range(num_batches):
            # Print information about number of done batches
            print(f'[LOADING][Embeddings]{str(i + 1).zfill(4)}/'
                  f'{str(num_batches).zfill(4)} {str_info}'.ljust(50),
                  end='\r')
            # Get array of batches
            batch_array = list_image_segments[i]
            # Preprocess images for a second time using a different
            # preprocessing step
            batch_array = self.tools_embeddings.fn_preprocess_array(
                batch_array)
            # Calculate embeddings for array of batches and
            # append embeddings to list of embeddings
            embeddings.extend(self.tools_embeddings.fn_array_to_embedding(
                batch_array, model_embedding
            ))

        print(f'[DONE][Embeddings] {str(num_batches).zfill(4)}/'
              f'{str(num_batches).zfill(4)} {str_info}'.ljust(self.ljust))
        return np.array(embeddings)

    def similarities_self_calculate(self, path_dir, model_embedding):
        """
        Calculate self-similarities for a time-lapse image sequence
        of an object, e.g. an embryo.
        """
        # Update parameters
        self.__init__()
        # Load image paths from directory
        paths_imgs = self.tools_paths.dir_to_img_paths(path_dir)
        # Load images
        array_imgs = self.tools_images.fn_images_tiff_parse(paths_imgs)
        # Calculate embeddings for images
        embeddings = self.imgs_to_embeddings(model_embedding, array_imgs)

        # Calculate similarities
        similarities = self.tools_similarities.cosine_similarities_self(
            embeddings
        )
        return similarities, paths_imgs
