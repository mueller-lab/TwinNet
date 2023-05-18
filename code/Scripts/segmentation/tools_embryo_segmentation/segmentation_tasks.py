import datetime
from . import segmentation_utils, image_tasks


class SegmentationTasks:
    """Segmentation procedures"""

    def __init__(self):
        self.title = 'SegmentationTasks'
        self.SU_INSTANCE = segmentation_utils.SegmentationUtils()
        self.IT_INSTANCE = image_tasks.ImageTasks()

    def task_inference(self,
                       path_subdir_images,
                       path_subdir_annotations,
                       model_segmentation):
        """Run inference on images in directory and store annotations."""
        string_start = 'START: Sequence segmentation and storage as JSON.'
        string_done = 'DONE: Saved predictions as JSONs.'
        try:
            start_time = datetime.datetime.now()
            print('\n')
            print(path_subdir_images)
            print('=' * (len(string_start) + 10))
            print('=', string_start, '=', sep=' '*4)
            print('=' * (len(string_start) + 10))

            self.SU_INSTANCE.utils_inference(path_subdir_images,
                                             path_subdir_annotations,
                                             model_segmentation)

            duration = datetime.datetime.now() - start_time
            string_duration = 'Duration: ' + str(duration)
            print('=' * (len(string_done) + 10))
            print('=', string_done, '=', sep=' ' * 4)
            print('=', string_duration, ' ' *
                  (len(string_done) - len(string_duration) - 4),
                  '=', sep=' ' * 4)
            print('=' * (len(string_done) + 10))

        except Exception as e:
            print("DEBUG -- segmentation_tasks/task_inference -- \n", e)
