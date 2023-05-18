import argparse
import cv2
import json
import glob
import os
import pathlib
import time
from multiprocessing import Pool


class ToolsSegmentationImages:

    def __init__(self, dir_dst):
        self.dir_dst = dir_dst

    def __call__(self, path_image, path_json, preds):
        """
        Save images based on automatized segmentation.
        """
        p_img = pathlib.PurePath(path_image)
        p_ann = pathlib.PurePath(path_json)

        n_position = p_ann.parent.parent.stem
        n_tiffs = p_ann.parent.parent.parent.stem
        n_dataset = p_ann.parent.parent.parent.parent.stem

        p_position_dst = f"{self.dir_dst}/{n_dataset}/{n_tiffs}/{n_position}"\
            .replace("\\", "/").replace("//", "/")

        name_stem_image = p_img.stem
        image = self.load_tiff(path_image)
        size_padding = 200
        image_padded = cv2.copyMakeBorder(image,
                                          size_padding,  # top border
                                          size_padding,  # bottom border
                                          size_padding,  # left border
                                          size_padding,  # right border
                                          cv2.BORDER_CONSTANT)

        for i in preds:
            embryo_id = str('E' + str(i).zfill(3))
            centerx = preds[i][0][0] + 0.5 * int(preds[i][0][2])
            centery = preds[i][0][1] + 0.5 * int(preds[i][0][3])
            xmin = int(centerx - 192 + size_padding)
            xmax = int(centerx + 192 + size_padding)
            ymin = int(centery - 192 + size_padding)
            ymax = int(centery + 192 + size_padding)

            name_image_embryo = name_stem_image + embryo_id + '.tif'
            path_embryo = os.path.join(p_position_dst, 'embryos', embryo_id)
            path_save_embryo = os.path.join(path_embryo, name_image_embryo)

            if os.path.isdir(path_embryo):
                pass
            else:
                self.dir_make(path_embryo)

            image_frame = image_padded[ymin:ymax, xmin:xmax]
            cv2.imwrite(path_save_embryo, image_frame)

    @staticmethod
    def load_tiff(path_tiff):
        image = cv2.imread(path_tiff, cv2.IMREAD_UNCHANGED)
        return image

    @staticmethod
    def dir_make(path_dir):
        try:
            os.makedirs(path_dir)
        except OSError:
            pass


class ToolSegmentationPaths:

    def __init__(self, dir_src, dir_dst):
        self.dir_src = dir_src
        self.tools_segmentation_images = ToolsSegmentationImages(dir_dst)

    def __call__(self):
        """
        Load image paths of images which have been segmented
        using the segmentation tool for zebrafish embryos.

        Store segments separately, sorted by embryos.
        """
        list_filepaths = self.get_list_filepaths(self.dir_src)
        start_time = time.time()
        pool = Pool()
        _ = pool.map(self.read_json, list_filepaths)

        pool.close()
        pool.join()

        duration = time.time() - start_time
        print('\n')
        print(f"[INFO][DONE] {len(list_filepaths)} images",
              f"[INFO][DURATION] {duration:.2f} s.",
              sep="\n")

    @staticmethod
    def get_list_filepaths(dir_src):
        """
        Get list of filepaths of files in a directory.
        """
        filepaths = sorted(glob.glob(
            f"{dir_src}/*/TIFFs/*/annotations/*.json"
            .replace("\\", "/")
            .replace("//", "/")
        ))
        return filepaths

    def read_json(self, path_json):
        """Get info on segmentation."""
        with open(path_json) as f:
            file = json.load(f)
            path_image = file['images'][0]['path']
            preds = {}
            for i in file['annotations']:
                preds[i['id']] = [i['bbox'], i['score']]
        
            self.tools_segmentation_images(path_image,
                                           path_json,
                                           preds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir",
                        help="Path to directory containing test "
                             "image annotations. Use following directory structure: "
                             "Dir_to_select/*/TIFFs/*/annotations/")
    parser.add_argument("-o", "--output_dir",
                        help="Path to directory to save "
                             "image segments to.")
    args = parser.parse_args()

    tool_segmentation_paths = ToolSegmentationPaths(
        args.input_dir,
        args.output_dir
    )
    tool_segmentation_paths()
