import pathlib
from . import main_window_tasks, prediction_tasks, glob_tasks


class MainWindowProcedures:
    def __init__(self):
        self.MWT_INSTANCE = main_window_tasks.MainWindowTasks()
        self.PT_INSTANCE = prediction_tasks.PredictionTasks()
        self.GT_INSTANCE = glob_tasks.GlobTasks()

    def procedure_dataset_stats_print(self, dirs_src_experiments):
        """
        Print information on datasets inside the experiment folder.
        """
        for dir_src_experiment in dirs_src_experiments:
            n_dataset = pathlib.PurePath(dir_src_experiment).parent.stem

            subdirs = self.GT_INSTANCE.glob_dir_root(dir_src_experiment)
            pattern_glob_imgs = f"{subdirs[0]}/images/*.*".replace("\\", "/")
            n_subdir = pathlib.PurePath(subdirs[0]).stem

            files = self.GT_INSTANCE.glob_variable(pattern_glob_imgs)
            filetype = pathlib.PurePath(files[0]).suffix

            print(f"[INFO][DATASET PATH] {dir_src_experiment}",
                  f"[INFO][DATASET NAME] {n_dataset}",
                  f"[INFO][NUM FILES] {n_subdir}: {len(files)}",
                  f"[INFO][FILETYPE] {filetype}",
                  sep='\n')

    def procedure_model_load(self, path_model_segmentation):
        """
        Procedure to load the segmentation model.
        """
        try:
            model_segmentation = self.PT_INSTANCE.load_model(
                path_model_segmentation
            )
            return model_segmentation
        except Exception as e:
            print('DEBUG -- main_window_procedures/procedure_model_load -- \n', e)

    def procedure_inference_single(self,
                                   dir_src_experiment,
                                   model_segmentation,
                                   dir_dst):
        """
        Loop through subdirs in root dir and run model prediction on images.
        """
        try:
            glob_dir_root = self.GT_INSTANCE.glob_dir_root(dir_src_experiment)
            try:
                for path_subdir in glob_dir_root:
                    self.MWT_INSTANCE.do_inference(path_subdir,
                                                   model_segmentation,
                                                   dir_dst)
            except Exception as e:
                print('DEBUG -- main_window_procedures/'
                      'procedure_inference_single (Error 1) -- \n',
                      e)
        except Exception as e:
            print('DEBUG -- main_window_procedures/'
                  'procedure_inference_single (Error 2) -- \n',
                  e)

    def procedure_inference_multiple(self,
                                     dirs_src_experiments,
                                     model_segmentation,
                                     dir_dst):
        """
        Loop through experiment directories and run segmentation
        model prediction on images in subdirs.
        """
        try:

            try:
                for dir_src_experiment in dirs_src_experiments:
                    path = pathlib.PurePath(dir_src_experiment)
                    self.procedure_inference_single(dir_src_experiment,
                                                    model_segmentation,
                                                    dir_dst)

            except Exception as e:
                print('DEBUG -- main_window_procedures/'
                      'procedure_inference_multiple (Error 1) -- \n',
                      e)
        except Exception as e:
            print('DEBUG -- main_window_procedures/'
                  'procedure_inference_multiple (Error 2) -- \n',
                  e)
