import argparse
import sys
sys.path.append("./")
from tools_embryo_segmentation import glob_tasks
from tools_embryo_segmentation import main_window_procedures


class ToolEmbryoSegmentation:
    """
    Segment images containing multiple zebrafish embryos and store
    segment information as .json files.

    Requires following input data structure:
    Dir_to_select/*/TIFFs/*/images/

    Saves .json files to following directory:
    Dir_to_select/*/TIFFs/*/annotations/
    """
    def __init__(self, dir_src, dir_model, dir_dst):
        self.dir_src = dir_src
        self.dir_dst = dir_dst
        self.path_model_segmentation = dir_model

        self.GT_INSTANCE = glob_tasks.GlobTasks()
        self.MWP_INSTANCE = main_window_procedures.MainWindowProcedures()

    def __call__(self):
        """
        Load
        """
        # Load paths to image data
        dirs_src_experiments = self.GT_INSTANCE.glob_dir_experiments(
            self.dir_src
        )

        # Check if dirs contain images and get info about dirs
        self.MWP_INSTANCE.procedure_dataset_stats_print(dirs_src_experiments)
        # Load segmentation model
        model_segmentation = self.MWP_INSTANCE.procedure_model_load(
            self.path_model_segmentation
        )

        # Start segmentation
        self.MWP_INSTANCE.procedure_inference_multiple(dirs_src_experiments,
                                                       model_segmentation,
                                                       self.dir_dst)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir",
                        help="Path to directory containing test "
                             "data. Use following directory structure: "
                             "Dir_to_select/*/TIFFs/*/images.",
                        required=True)
    parser.add_argument("-m", "--model_dir",
                        help="Path to directory containing saved "
                             "tensorflow model for image segmentation.",
                        required=True)
    parser.add_argument("-o", "--output_dir",
                        help="Path to directory to save "
                             "segmentation results to.",
                        required=True)
    args = parser.parse_args()

    tool_embryo_segmentation = ToolEmbryoSegmentation(args.input_dir,
                                                      args.model_dir,
                                                      args.output_dir)
    tool_embryo_segmentation()
