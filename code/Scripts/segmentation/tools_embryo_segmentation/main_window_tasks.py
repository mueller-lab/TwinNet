import PIL
import os
import glob
from . import directory_tasks, segmentation_tasks


class MainWindowTasks:
    def __init__(self):
        self.title = 'MainWindowTasks'
        self.DT_INSTANCE = directory_tasks.DirectoryTasks()
        self.ST_INSTANCE = segmentation_tasks.SegmentationTasks()

    @staticmethod
    def fn_dirs_glob(dir_src):
        """
        Function to select directory and update
        specified variable with the respective directory.
        """
        try:
            dir_glob = glob.glob(f"{dir_src}/*/")
            return dir_glob

        except Exception as e:
            print('DEBUG -- main_window_tasks/fn_dirs_glob -- \n', e)

    @staticmethod
    def do_params_dir_get(main_window, dir_glob):
        try:
            if len(dir_glob) > 0:
                main_window.dir_root_glob.set(dir_glob)
                num_subdirs = len(dir_glob)
                main_window.num_subdirs.set(num_subdirs)
            else:
                pass

        except Exception as e:
            print('DEBUG -- main_window_tasks/do_num_subdirs_get -- \n', e)

    @staticmethod
    def do_params_subdir_get(main_window, dir_glob):
        """
        Get the filetype in and number of files of the first subdirectory.
        """
        try:
            if len(dir_glob) > 0:
                subdir_glob = glob.glob(dir_glob[0] + '/images/*.*')
                num_files = len(subdir_glob)
                if num_files > 0:
                    img = PIL.Image.open(subdir_glob[0])
                    main_window.file_format.set(img.format)
                    img.close()

                    main_window.num_files.set(num_files)
                else:
                    pass
            else:
                pass

        except Exception as e:
            print('DEBUG -- main_window_tasks/do_filetype_get -- \n', e)

    def do_inference(self, path_subdir, model_segmentation, dir_dst):
        """Run model inference on images in subdirectory.

        This method does the following steps:
        1. From the subdirectory path get paths for
        images/annotations subdirs in subdir
        2. Create a directory for annotations if not existing yet
        3. Run loop and perform inference on images
        """
        try:
            # 1. Get subdir paths
            path_subdir_images, path_subdir_annotations = \
                self.DT_INSTANCE.paths_subdir_get(path_subdir, dir_dst)
            # 2. Create annotations dir
            path_subdir_annotations = \
                self.DT_INSTANCE.dir_create(path_subdir_annotations)
        except Exception as e:
            print('DEBUG -- main-window_tasks/do_inference (Error 1) -- \n',
                  e)

        # 3. Inference
        try:
            self.ST_INSTANCE.task_inference(path_subdir_images,
                                            path_subdir_annotations,
                                            model_segmentation)
        except Exception as e:
            print('DEBUG -- main-window_tasks/do_inference (Error 2) -- \n',
                  e)
