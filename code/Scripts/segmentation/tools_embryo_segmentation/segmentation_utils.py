import os
import json
import pathlib
from datetime import datetime
import time
from . import glob_tasks, prediction_tasks, object_tracker, image_tasks


class SegmentationUtils:
    """Segmentation procedures."""

    def __init__(self):
        self.title = 'SegmentationTasks'
        self.GT_INSTANCE = glob_tasks.GlobTasks()
        self.PT_INSTANCE = prediction_tasks.PredictionTasks()
        self.OT_INSTANCE = object_tracker.ObjectTracker()
        self.IT_INSTANCE = image_tasks.ImageTasks()

    @staticmethod
    def utils_template_json():
        """Create a dictionary to store model predictions in JSON format."""
        info = {"year": "2023",
                "version": "",
                "description": "High throughput image segmentation.",
                "contributor": "",
                "url": "",
                "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        categories = [{"id": 1,
                       "name": "complete",
                       "supercategory": "embryo"}]

        json_dict = {"info": info,
                     "categories": categories}

        return json_dict

    @staticmethod
    def utils_image_parameters(path,
                               embryo_id,
                               bbox, score,
                               histogram,
                               bins,
                               image_min,
                               image_max):
        """
        Convenience function to get image parameters required for
        saving JSON file.
        """
        filename = os.path.basename(path)
        image_id = int(time.time() * 10e3)
        images = [{"id": image_id,
                   "file_name": filename,
                   "height": 2048,
                   "width": 2048,
                   "date_captured": 0,
                   "path": path,
                   }]

        ymin, xmin, ymax, xmax = bbox
        width = xmax - xmin
        height = ymax - ymin
        annotation = {'id': embryo_id,
                      'image_id': image_id,
                      'category_id': 1,
                      'bbox': [int(xmin),
                               int(ymin),
                               int(width),
                               int(height)],
                      'segmentation': [],
                      'area': int(width * height),
                      'iscrowd': 0,
                      'score': score,
                      'metadata': dict(histogram=histogram,
                                       bins=bins,
                                       image_min=image_min,
                                       image_max=image_max)}

        return filename, images, annotation

    def utils_save_json(self,
                        path_subdir_annotations,
                        name_image,
                        info_image,
                        predictions):
        """
        Save model predictions as json files for each image.

        This function stores the model prediction, which comes in format
        [class, score, [box coordinates]] with further information
        (image path, classes, image id, image id in sequence, embryo id)
        as dictionary. This dictionary is saved as json file with the same
        filename as the image.
        """
        # 1. Create dictionary with prediction
        prediction_dict = self.utils_template_json()
        prediction_dict['images'] = info_image
        prediction_dict['annotations'] = predictions

        # 2. Create save name
        path_json_save = os.path.join(
            path_subdir_annotations,
            pathlib.PurePath(name_image).stem + '.json'
        )

        # 3. Save JSON file
        try:
            with open(path_json_save, 'w') as JSON_file:
                json.dump(prediction_dict,
                          JSON_file,
                          indent=4,
                          separators=(',', ': '))
        except Exception as e:
            print(e)

        return path_json_save

    def utils_inference(self,
                        path_subdir_images,
                        path_subdir_annotations,
                        model_segmentation):
        """
        Run model inference on all images in the directory
        and save annotations as JSON files.
        """
        try:
            # 1. Get paths of images in directory
            paths_imgs_segment = self.GT_INSTANCE.glob_paths_files_tif(
                path_subdir_images
            )

            num_imgs = len(paths_imgs_segment)

            # 2. Loop through images
            try:
                for i in range(len(paths_imgs_segment)):
                    print(f"Segmented images: "
                          f"{str(i + 1).zfill(len(str(num_imgs)))}/"
                          f"{num_imgs}",
                          end='\r')
                    if i == 0:
                        # Load image to tensor and run inference on tensor
                        try:
                            model_pred, image_tensor = \
                                self.PT_INSTANCE.inference(
                                    model_segmentation,
                                    paths_imgs_segment[i]
                                )
                            bboxes_old = self.PT_INSTANCE.boxes_threshold(
                                model_pred,
                                0.5,
                                2048
                                )
                            self.OT_INSTANCE.object_tracking_initialize(
                                bboxes_old
                                )
                        except Exception as e:
                            print('DEBUG --segmentation_utils/'
                                  'utils_inference (Error 1) -- \n',
                                  e)

                        # Loop through predictions and append dictionaries
                        # for each embryo to annotations list
                        params_annotations = []
                        for embryo_id in bboxes_old:
                            histogram,\
                                bins,\
                                image_min,\
                                image_max = self.IT_INSTANCE.bbox_histogram(
                                    image_tensor,
                                    bboxes_old[embryo_id][2]
                                )

                            name_file,\
                                params_image,\
                                params_annotation = \
                                self.utils_image_parameters(
                                    paths_imgs_segment[i],
                                    embryo_id,
                                    bboxes_old[embryo_id][2],
                                    float(bboxes_old[embryo_id][1]),
                                    histogram,
                                    bins,
                                    image_min,
                                    image_max
                                )
                            params_annotations.append(params_annotation)

                        # Save a JSON file with segmentation
                        # information to path_subdir_annotations
                        self.utils_save_json(
                            path_subdir_annotations,
                            name_file,
                            params_image,
                            params_annotations
                        )

                    else:
                        # Load image to tensor and run inference on tensor
                        try:
                            model_pred,\
                                image_tensor = self.PT_INSTANCE.inference(
                                    model_segmentation,
                                    paths_imgs_segment[i]
                                    )
                            bboxes_new = self.PT_INSTANCE.boxes_threshold(
                                model_pred,
                                0.5,
                                2048)

                            bboxes_traced = self.OT_INSTANCE.object_track(
                                bboxes_old,
                                bboxes_new
                            )
                        except Exception as e:
                            print('DEBUG --segmentation_utils/'
                                  'utils_inference (Error 2) -- \n',
                                  e)
                        # Loop through predictions and append dictionaries
                        # for each embryo to annotations list
                        params_annotations = []
                        for embryo_id in bboxes_traced:
                            histogram, \
                                bins, \
                                image_min, \
                                image_max = self.IT_INSTANCE.bbox_histogram(
                                    image_tensor,
                                    bboxes_traced[embryo_id][2]
                                )

                            name_file, \
                                params_image, \
                                params_annotation = \
                                self.utils_image_parameters(
                                    paths_imgs_segment[i],
                                    embryo_id,
                                    bboxes_traced[embryo_id][2],
                                    float(bboxes_traced[embryo_id][1]),
                                    histogram,
                                    bins,
                                    image_min,
                                    image_max
                                )
                            params_annotations.append(params_annotation)

                        # Create and save a JSON file with segmentation
                        # information to path_subdir_annotations
                        self.utils_save_json(
                            path_subdir_annotations,
                            name_file, params_image,
                            params_annotations
                        )
                        bboxes_old = bboxes_traced

            except Exception as e:
                print('DEBUG --segmentation_utils/'
                      'utils_inference (Error 3) -- \n',
                      e)

        except Exception as e:
            print('DEBUG --segmentation_utils/'
                  'utils_inference (Error 4) -- \n',
                  e)
