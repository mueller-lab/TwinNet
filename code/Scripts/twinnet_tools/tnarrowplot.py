import glob
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class TNToolsArrowPlot:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used with tools in 'tnarrow.py' and
    'tnarroweval.py' to utilize TN predicted developmental stages for
    detection of deviation from normal development.
    """
    def __init__(self, **kwargs):
        self.format_ljust = 50

        self.plot_indices_pred_normal = []
        self.plot_indices_df_normal = []
        self.plot_indices_pred_maldev = []
        self.plot_indices_df_maldev = []

        self.plot_atp_min_correction_reference = int(
            kwargs.get('intervals_x', 4)
        )
        self.plot_atp_min_correction_test = int(
            kwargs.get('intervals_y', 4)
        )

        self.plot_color_normal = "#c1d831"
        self.plot_color_maldev = 'Red'# "#431c53"
        self.plot_fontsize_large = 8
        self.plot_fontsize_small = 6
        self.plot_linewidth = 1
        self.plot_size_marker = self.plot_linewidth 

    def __call__(self, paths_normal, paths_maldev):
        """Calculate developmental speeds of embryos."""
        self.__init__()
        # Get number of embryos per category
        num_paths_normal = len(paths_normal)
        num_paths_maldev = len(paths_maldev)

        # Loop through paths to directories of normal embryos
        # containing similarity values to reference images.
        # Similarity values should be stored as '.csv' file
        # for each image in the image sequence of the test embryo
        for i in range(num_paths_normal):
            # Load path to embryo directory
            path_embryo = paths_normal[i]
            # Prepare info to print number of embryos
            str_info = f"[Normal] " \
                       f"{str(i + 1).zfill(len(str(num_paths_normal)))}/" \
                       f"{num_paths_normal}"
            # Get predicted stages of images of test embryo and
            # append to corresponding variables
            self.calc_speed_divergence_multiple_linear(
                path_embryo,
                self.plot_indices_pred_normal,
                self.plot_indices_df_normal,
                str_info=str_info
            )

        # Loop through paths to directories of maldeveloping embryos
        # containing similarity values to reference images.
        for i in range(num_paths_maldev):
            # Load path to embryo directory
            path_embryo = paths_maldev[i]
            # Prepare info to print number of embryos
            str_info = f"[Maldeveloping] " \
                       f"{str(i + 1).zfill(len(str(num_paths_maldev)))}/" \
                       f"{num_paths_maldev}"
            # Get predicted stages of images of test embryo and
            # append to corresponding variables
            self.calc_speed_divergence_multiple_linear(
                path_embryo,
                self.plot_indices_pred_maldev,
                self.plot_indices_df_maldev,
                str_info=str_info
            )

    def plots(self, **kwargs):
        """
        Plot maxima of similarities above threshold for
        multiple similarity '.csv' files from embryo directories,
        as calculated when calling an instance of this class.
        """
        self.plots_with_heatmap_scatter(self.plot_indices_pred_normal,
                                        self.plot_indices_df_normal,
                                        self.plot_indices_pred_maldev,
                                        self.plot_indices_df_maldev)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'], dpi=300)
        plt.show()

    def plots_with_heatmap_scatter(self,
                                   var_indices_pred_normal,
                                   var_indices_df_normal,
                                   var_indices_pred_maldev,
                                   var_indices_df_maldev):
        """
        Plot developmental speed graphs for multiple embryos
        as scatter plot.
        """
        # Make joint lists for original image indices and
        # predicted developmental stages of both normally developing
        # and maldeveloping embryos
        var_indices_df = var_indices_df_normal + var_indices_df_maldev
        var_indices_pred = var_indices_pred_normal + var_indices_pred_maldev

        # Calculate durations of data sets
        duration_query = \
            max(var_indices_df) * self.plot_atp_min_correction_test
        duration_reference = \
            max(var_indices_pred) * self.plot_atp_min_correction_reference

        # Get longer duration
        plot_range = max(duration_query,
                         duration_reference)

        # Make tick labels based on timepoints
        plot_tick_labels = [int(i) for i in list(range(0, plot_range, 200))]

        # Divide timepoints by acquisition time intervals
        # to get indices for plotting
        plot_x_ticks = [
            plot_tick_label / self.plot_atp_min_correction_reference
            for plot_tick_label in plot_tick_labels
        ]
        plot_y_ticks = [
            plot_tick_label / self.plot_atp_min_correction_test
            for plot_tick_label in plot_tick_labels
        ]

        # Plot figure
        fig = plt.figure(dpi=300,
                         figsize=(3 * duration_reference/duration_query,
                                  3))

        # Plot predicted stages for images of normal embryos
        # as scatter plot
        #plt.scatter(var_indices_pred_normal,
        #            var_indices_df_normal,
        #             c=self.plot_color_normal,
         #            s=self.plot_size_marker)
        sns.kdeplot(x=var_indices_pred_normal, y=var_indices_df_normal, cmap="Blues", shade=True, bw_adjust=.9)

        # Plot predicted stages for images of maldeveloping embryos
        # as scatter plot
        plt.scatter(var_indices_pred_maldev,
                    var_indices_df_maldev,
                    edgecolors='none',
                    c=[self.plot_color_maldev] * len(var_indices_df_maldev),
                    s=self.plot_size_marker)

        # Adjust plot parameters
        plt.tick_params(axis='both', which='both',
                        labelsize=self.plot_fontsize_small)
        plt.xlabel('Test dataset time (min)',
                   fontsize=self.plot_fontsize_large)

        plt.xticks(plot_x_ticks,
                   plot_tick_labels,
                   fontsize=self.plot_fontsize_small)
        plt.xlim(0, int(max(var_indices_pred) * 1.05))

        plt.ylabel('Reference dataset time (min)',
                   fontsize=self.plot_fontsize_large)

        plt.yticks(plot_y_ticks,
                   plot_tick_labels,
                   fontsize=self.plot_fontsize_small)
        plt.ylim(0, int(max(var_indices_df) * 1.05))

        return fig

    @staticmethod
    def calc_speed_divergence_linear(df):
        """
        Get predicted maximum of similarities of cosine similarities
        above 0.5 for similarities of one test image with reference
        images stored in a pandas.core.frame.DataFrame.
        """
        data_y = df['Anch_sim_1']
        data_y = data_y[data_y > 0.5]
        timepoint = data_y.idxmax()

        return timepoint
    
    def calc_speed_divergence_multiple_linear(self,
                                              path_dir,
                                              var_index_pred,
                                              var_index_df,
                                              **kwargs):
        """
        Calculate maxima of similarities with reference images
        for similarity values of images from an image sequence.
        """
        # Get additional info to print
        str_info = kwargs.get("str_info", "")

        # Load paths of dataframes containing similarities for one
        # test embryo
        paths_dataframes = list(sorted(glob.glob(path_dir + '/*.csv')))
        num_dataframes = len(paths_dataframes)

        # Print info
        print(f"[LOADING] {str_info} [NUM_FILES] {num_dataframes}"
              .ljust(self.format_ljust),
              end='\r')

        # Loop through list of paths of dataframes containing
        # calculated similarities
        for i in range(num_dataframes):
            # Load dataframe of similarities
            df = pd.read_csv(paths_dataframes[i])
            # Get predicted stage of embryo image based on index of
            # maximum of similarity values above threshold
            tp_pred = self.calc_speed_divergence_linear(df)
            # Store index of dataframe/original image and
            # predicted index of image in class variables
            var_index_pred.append(tp_pred)
            var_index_df.append(i)

        print(f"[DONE] {str_info} [NUM_FILES] {num_dataframes}"
              .ljust(self.format_ljust),
              end='\n')
