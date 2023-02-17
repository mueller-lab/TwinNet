import cv2
import itertools
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
import scipy.io

plt.rcParams['svg.fonttype'] = 'none'


class PlotSimilaritiesSelf2D:
    """
    Plot similarities which were calculated by
    "self-similarity-calculation" of a test
    embedding with embeddings at previous
    acquisition timepoints of the same embryo.
    """
    def __init__(self):
        self.plot_line_alpha_fg = 1
        self.plot_figsize = (5, 3)
        self.plot_fontsize_large = 8
        self.plot_fontsize_small = 6
        self.plot_linewidth = 1
        self.plot_size_marker = self.plot_linewidth * 5

    def fn_cmap_custom_exponential(self, **kwargs):
        """
        Creates a colormap based on predefined
        'matplotlib' colormaps. Colors are adjusted
        such that color changes occur mainly in
        upper range of values.
        """
        samples = self.fn_samples_exponential(**kwargs)
        temp_cmap = mpl.cm.get_cmap(kwargs.get("cmap", "viridis"))
        list_colors = [temp_cmap(s) for s in samples]
        lscmap = mpl.colors.LinearSegmentedColormap.from_list("cmap_custom", list_colors)
        return lscmap

    @staticmethod
    def fn_samples_exponential(lamb=0.2, **kwargs):
        """
        Generates 100 samples based
        on a decaying exponential
        distribution.
        """
        n_samples = 100
        xs = np.linspace(0, n_samples, n_samples)
        ys = np.exp(lamb * xs)
        ys = (ys - np.min(ys)) / (np.max(ys) - np.min(ys))

        grads = np.gradient(ys)
        tp_grad = next(grad for grad in grads if grad >= 1 / n_samples)
        x_tp_grad = np.where(np.isclose(grads, tp_grad))

        if kwargs.get("verbose", False):
            print(f"Index of change: {x_tp_grad[0] / n_samples}")

        return ys

    def fn_similarities_list_to_similarities_arrays(self, similarities_list, paths_imgs_list):
        """
        Create numpy arrays for similarity values in similarities_list.

        Parameters
        ----------
        similarities_list: list
            List of similarity values, each of which
            Should be a list of lists of length num_frames - 1.
        paths_imgs_list: list
            List of lists of image paths corresponding
            to similarity values.
        """
        similarities_arrays = [
            self.fn_2d_sims_to_arrays(sims, len(ps_imgs), square=True)[2]
            for sims, ps_imgs in
            zip(similarities_list, paths_imgs_list)
        ]
        return similarities_arrays

    @staticmethod
    def fn_sims_to_arrays_1d_scatter(similarities):
        """
        This function maps values and positions of
        similarities to three 1d-arrays for scatter
        plotting.

        The parameter "similarities" is a list of lists.
        Perform following steps:
        1. Calculate indices of list of lists
        -> Use as x-values
        2. Calculate indices of values within sub-lists
        -> Use as y-values
        3. Use values of items in list to retrieve color
        -> Use for coloring of scatter plot

        atp = acquisition timepoints
        """
        cmap = mpl.cm.get_cmap('viridis')

        xs, ys, zs = list(), list(), list()

        for x in range(len(similarities)):
            sims = similarities[x]
            for y in range(len(sims)):
                xs.append(x)
                ys.append(y)
                zs.append(sims[y])
        colors = [cmap(z) for z in zs]

        return xs, ys, zs, colors

    @staticmethod
    def fn_2d_sims_to_arrays(similarities, num_images, **kwargs):
        """
        This function maps values and positions of
        similarities to three arrays for 3D plotting.

        atp = acquisition timepoints
        """
        square = kwargs.get('square', False)
        xs = list(range(1, num_images))
        ys = list(range(1, num_images))
        xs_grid, ys_grid = np.meshgrid(xs, ys)
        print(square)
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
        #zs_grid_plot[zs_grid_plot == 0] = np.nan

        return xs_grid, ys_grid, zs_grid_plot

    @staticmethod
    def fn_3d_sims_to_arrays(similarities, num_images):
        """
        This function maps values and positions of
        similarities to three arrays for 3D plotting.

        atp = acquisition timepoints
        """
        # x-values:
        # xs = [2, ..., maximum number of frames] based on atps
        # xs = [1, ..., maximum number of frames - 1] based on indices
        # xs = [1, ..., maximum number of frames - 1] also for plotting
        xs = list(range(1, num_images))
        # y-values
        # yes = [1, ..., atp of prior-to-last image] based on atps
        # yes = [0, ..., atp of prior-to-last image - 1] based on indices
        # yes = [1, ..., atp of prior-to-last image] for plotting
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
    def fn_3d_sims_to_arrays_square(similarities, num_images):
        """
        This function maps values and positions of
        similarities to three arrays for 3D plotting.

        atp = acquisition timepoints
        """
        # x-values:
        # xs = [2, ..., maximum number of frames] based on atps
        # xs = [1, ..., maximum number of frames - 1] based on indices
        # xs = [1, ..., maximum number of frames - 1] also for plotting
        xs = list(range(1, num_images))
        # y-values
        # yes = [1, ..., atp of prior-to-last image] based on atps
        # yes = [0, ..., atp of prior-to-last image - 1] based on indices
        # yes = [1, ..., atp of prior-to-last image] for plotting
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
                    zs_grid_plot[i, j] = sims[j]
                    zs_grid_colors[j, i] = sims[j]
                except Exception as e:
                    print(e, j, i)
        zs_grid_plot[zs_grid_plot == 0] = np.nan
        zs_grid_colors[zs_grid_colors == 0] = 0.0

        return xs_grid, ys_grid, zs_grid_plot, zs_grid_colors

    def plot_similarities_standard_deviation(self, similarities_arrays,
                                             **kwargs):
        """
        Parameters
        ----------
        similarities_arrays: list
            List of numpy.ndarrays of similarity values
        """
        similarities_shapes = [
            sim_arr.shape[0] for sim_arr in similarities_arrays
        ]
        canv_overl = np.zeros((max(similarities_shapes),
                               max(similarities_shapes)))
        canv_counts = np.zeros(canv_overl.shape)
        collection_canvs = list()

        for sim_arr in similarities_arrays:
            if sim_arr.shape == canv_overl.shape:
                canv_overl += sim_arr
                canv_counts += np.ones(sim_arr.shape)
                collection_canvs.append(sim_arr)
            else:
                sim_arr_adjusted = np.zeros(canv_overl.shape)
                sim_arr_adjusted[
                    :sim_arr.shape[0] - 1, :sim_arr.shape[1] - 1] =\
                    sim_arr[:-1, :-1]

                canv_overl += sim_arr_adjusted
                canv_counts += np.ones(sim_arr_adjusted.shape)
                collection_canvs.append(sim_arr_adjusted)

        canv_overl = np.flipud(canv_overl / canv_counts)

        num_imgs = max(similarities_shapes)
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_fontsize = 10
        plot_labelpad = 5
        plot_xy_ticks = list(range(0, num_imgs, 50))

        if kwargs.get("color_adjust", False):
            plot_colors_hlf = self.fn_cmap_custom_exponential(**kwargs)
        else:
            plot_colors_hlf = mpl.cm.get_cmap(kwargs.get("cmap", "viridis"))

        fig, ax = plt.subplots(figsize=(5, 5), dpi=300)

        # ax[0].imshow(canv_overl, cmap=plot_colors_hlf)
        # ax[0].set_title("Similarity values")
        # ax[0].set_xticks(plot_xy_ticks,
        #                  [str(a * plot_atp_min_correction) for a in plot_xy_ticks],
        #                  fontsize=plot_fontsize)
        # ax[0].set_ylabel('t [min]', labelpad=plot_labelpad)
        # ax[0].set_yticks(plot_xy_ticks,
        #                  [str(a * plot_atp_min_correction) for a in reversed(plot_xy_ticks)],
        #                  fontsize=plot_fontsize)
        #
        # divider = make_axes_locatable(ax[0])
        # sm = plt.cm.ScalarMappable(cmap=plot_colors_hlf)
        # cax = divider.append_axes("right", size="5%", pad=0.05)
        # cbar = fig.colorbar(sm, cmap=plot_colors_hlf, cax=cax)
        #
        # cbar.ax.set_ylabel('Similarity values')

        collection_canvs_arr = np.array(collection_canvs)
        collection_canvs_std = np.flipud(np.std(collection_canvs_arr, axis=0))
        ax.set_title("Similarity standard deviations")
        ax.set_xlabel('Time (min)', fontsize=self.plot_fontsize_large)
        ax.set_ylabel('Time (min)', fontsize=self.plot_fontsize_large)
        ax.imshow(collection_canvs_std)
        ax.tick_params(axis='both', which='both',
                       labelsize=self.plot_fontsize_small)
        ax.set_xticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_yticks(plot_xy_ticks,
                         [str(a * plot_atp_min_correction)
                          for a in reversed(plot_xy_ticks)],
                      fontsize=self.plot_fontsize_small)

        divider2 = make_axes_locatable(ax)
        sm2 = plt.cm.ScalarMappable(cmap=plot_colors_hlf)
        cax2 = divider2.append_axes("right", size="5%", pad=0.05)
        cbar = fig.colorbar(sm2, cmap=plot_colors_hlf, cax=cax2)

        cbar.ax.set_ylabel('Cosine similarity standard deviation')

        plt.tight_layout()
        if kwargs.get("title", None) is not None:
            plt.title(kwargs.get("title", "Similarity thresholding"))
        if kwargs.get("path_save", None) is not None:
            plt.savefig(kwargs.get("path_save", "./figure.svg"))
            plt.close()
        else:
            plt.show()

    def plot_single_embryo_similarities_to_phases(self, similarities, paths_images, **kwargs):
        """
        Highlight triangles corresponding to developmental phases
        in autoregression similarity plots.

        Parameters
        ----------
        similarities: list
            Similarity values. Should be a list of lists of length num_frames - 1.
        paths_images: list
            List of image paths of original files.
        """
        num_imgs = len(paths_images)
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_fontsize = 10
        plot_labelpad = 10
        plot_xy_ticks = list(range(0, num_imgs, 50))
        print(plot_xy_ticks)

        xs, ys, zs_grid_plot, zs_grid_color = self.fn_3d_sims_to_arrays_square(
            similarities, num_imgs)

        thresh = np.uint8(np.flipud(zs_grid_plot * 255))

        # noise removal
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        zs_plot = cv2.dilate(opening, kernel, iterations=3)

        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        ax.imshow(np.rot90(zs_plot, k=3), cmap='gray', origin='lower')

        ax.set_xlabel('t [min]', labelpad=plot_labelpad)
        ax.set_ylabel('t [min]', labelpad=plot_labelpad)
        ax.set_xticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction) for a in plot_xy_ticks],
                      fontsize=plot_fontsize)
        ax.set_yticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction) for a in plot_xy_ticks],
                      fontsize=plot_fontsize)
        if kwargs.get("title", None) is not None:
            plt.title(kwargs.get("title", "Similarity thresholding"))
        if kwargs.get("path_save", None) is not None:
            plt.savefig(kwargs.get("path_save", "./figure.svg"))
            plt.close()
        else:
            plt.show()

    def plot_embryo_similarities_self_2d(self, similarities, paths_images, **kwargs):
        """
        Plot similarities of embryo compared to itself in 2d.

        Parameters
        ----------
        similarities: list
            Similarity values. Should be a list of lists of length num_frames - 1.
        paths_images: list
            List of image paths of original files.
        """
        # Plot parameters
        num_imgs_total = len(paths_images)
        print(num_imgs_total)

        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_dpi = int(kwargs.get('plot_dpi', 300))
        plot_xy_ticks = list(range(0, num_imgs_total, 50))

        if kwargs.get("color_adjust", False):
            plot_colors_hlf = self.fn_cmap_custom_exponential(**kwargs)
        else:
            plot_colors_hlf = mpl.cm.get_cmap(kwargs.get("cmap", "viridis"))

        xs_grid, ys_grid, zs_grid_plot = self.fn_2d_sims_to_arrays(
            similarities, len(paths_images), square=True)
            
        print(xs_grid.shape)
        print(zs_grid_plot.shape)
        #Export arrays as csvs
        #DF_xs_grid= pd.DataFrame(xs_grid)
        #DF_ys_grid= pd.DataFrame(ys_grid)
        
        #DF_xs_grid.to_csv(kwargs['path_saveX'])
        #DF_ys_grid.to_csv(kwargs['path_saveY'])


        #temp.tools_general.fn_mat_write({f'data': zs_grid_plot},kwargs['path_saveZ'])        
        content = {f'data': zs_grid_plot}
        assert type(content) == dict
        scipy.io.savemat(kwargs['path_saveZ'], content)
        DF_zs_grid= pd.DataFrame(zs_grid_plot)
        DF_zs_grid.to_csv(kwargs['path_saveCV'])
               
        # Figure
        f, ax = plt.subplots(dpi=plot_dpi, figsize=(4, 4))
        f.tight_layout(rect=[0.0, 0.00, 0.8, 1.0])

        # Plot
        ax.imshow(zs_grid_plot, cmap=plot_colors_hlf)

        # Labels and titles
        ax.tick_params(axis='both', which='both',
                       labelsize=self.plot_fontsize_small)
        ax.set_xlabel('Time (min)', fontsize=self.plot_fontsize_large)
        ax.set_ylabel('Time (min)', fontsize=self.plot_fontsize_large)
        ax.set_xlim(left=0, right=len(similarities))
        ax.set_ylim(bottom=0, top=len(similarities))
        ax.set_xticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_yticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)

        divider = make_axes_locatable(ax)
        sm = plt.cm.ScalarMappable(cmap=plot_colors_hlf)
        #sm.set_clim(-1.0, 1.0)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cax.tick_params(axis='both', which='both',
                        labelsize=self.plot_fontsize_small)
        cbar = f.colorbar(sm, cmap=plot_colors_hlf, cax=cax)
        cbar.ax.set_ylabel('Cosine similarity ϕ',
                           fontsize=self.plot_fontsize_large)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        else:
            plt.show()
        plt.close()

    def pplot_embryo_similarities_self_2d_scatter(self, similarities, paths_images, **kwargs):
        """
        Plot similarities of embryo compared to itself in 2d as scatter plot.

        Parameters
        ----------
        similarities: list
            Similarity values. Should be a list of lists of length num_frames - 1.
        paths_images: list
            List of image paths of original files.

        Returns
        -------
        None
        """
        # Plot parameters
        num_imgs_total = len(paths_images)

        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_dpi = int(kwargs.get('plot_dpi', 300))
        plot_fontsize = 6
        plot_labelpad = 20
        plot_grid_linewidth = 0.5
        plot_tick_pad = 2
        plot_xy_ticks = list(range(0, num_imgs_total, 50))

        mpl.rcParams.update({'axes.linewidth': plot_grid_linewidth,
                             'font.size': plot_fontsize,
                             'grid.linewidth': plot_grid_linewidth,
                             'xtick.major.width': plot_grid_linewidth,
                             'xtick.major.pad': plot_tick_pad,
                             'ytick.major.width': plot_grid_linewidth,
                             'ytick.major.pad': plot_tick_pad})

        x, y, z, colors = self.fn_sims_to_arrays_1d_scatter(similarities)
  
        # Figure
        f, ax = plt.subplots(dpi=plot_dpi, figsize=(4, 4))
        f.tight_layout(rect=[0.0, 0.00, 0.8, 1.0])

        # Labels and titles
        ax.set_xlabel('t [min]', labelpad=plot_labelpad)
        ax.set_ylabel('t [min]', labelpad=plot_labelpad)
        ax.set_xlim(left=0, right=len(similarities))
        ax.set_ylim(bottom=0, top=len(similarities))
        ax.set_xticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction) for a in plot_xy_ticks],
                      fontsize=plot_fontsize)
        ax.set_yticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction) for a in plot_xy_ticks],
                      fontsize=plot_fontsize)
        ax.set_title(f'Similarity autoregression.')
        ax = plt.gca()

        ax_scat = ax.scatter(x, y, color=colors, vmin=0.0, vmax=1.0)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = f.colorbar(ax_scat, cax=cax)

        cbar.ax.set_ylabel('Normalized similarity values')

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        else:
            plt.show()
        plt.close()

    @staticmethod
    def _plot_1d_distribution_values_similarities(similarities, **kwargs):
        """
        A method to visualize the distribution of similarity values
        before normalization, if applicable also after normalization

        Previous version in Archive:
        Scatter plot with Gaussian KDE instead of histograms.
        """
        similarities = list(itertools.chain.from_iterable(similarities))
        similarities_norm = kwargs.get('similarities_norm', None)
        plot_bins = 100

        f, ax = plt.subplots(1, 1, figsize=(5, 4))
        ax.hist(similarities, bins=plot_bins)

        if similarities_norm is not None:
            if len(similarities_norm) != len(similarities):
                similarities_norm = list(itertools.chain.from_iterable(similarities_norm))

            divider = make_axes_locatable(ax)
            ax_norm = divider.append_axes("bottom", size="100%", pad=0.05)
            ax_norm.hist(similarities_norm, bins=plot_bins)
        plt.show()
