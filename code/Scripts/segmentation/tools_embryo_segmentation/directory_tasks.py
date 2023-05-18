import os
import pathlib


class DirectoryTasks:
    """Tools to manage directory structure."""

    def __init__(self):
        self.title = 'DirectoryTasks'

    @staticmethod
    def dir_create(dir_path):
        """
        Convenience function to create a directory
        under the specified dir_path.
        """
        try:
            os.makedirs(dir_path)
        except OSError as ose:
            print(ose, dir_path)
            pass

        return dir_path

    @staticmethod
    def paths_subdir_get(dir_path, dir_dst):
        """
        Convenience function to return filepaths of directories of subdir.
        Assumes structure of directory containing images to be
        'Dir_selected_for_segmentation/*(dataset)/TIFFs/*(position)/images'.
        Prepares path to save annotations to a new directory with
        following structure:
        "Dir_selected_for_annotations/*(dataset)/TIFFs/*(position)/annotations/"
        """
        p_src = pathlib.PurePath(dir_path)
        n_position = p_src.stem
        n_tiffs = p_src.parent.stem
        n_dataset = p_src.parent.parent.stem
        path_subdir_images = f"{dir_path}/images/".replace("\\", "/")
        path_subdir_annotations = f"{dir_dst}/annotations/{n_dataset}/" \
                                  f"{n_tiffs}/{n_position}/" \
                                  f"annotations/"\
            .replace("\\", "/").replace("//", "/")

        return path_subdir_images, path_subdir_annotations
