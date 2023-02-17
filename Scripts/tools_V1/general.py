import os
from datetime import datetime
import json
import numpy as np
import warnings

import scipy.io


class SNNToolset:
    """
    This class is part of the toolset for usage of siamese network (SNN) on evaluation purposes,
    SNN Version 5, scripts version 1.

    This class is the newer version of snn_utils_inference_20220427/SNNUtilsGeneral.
    This part of the toolset contains commonly used functions.
    """
    @staticmethod
    def fn_out(string, **kwargs):
        """Convenience function to print text with standardized format."""
        info_string = f'{string}'
        if 'ef' in kwargs:
            if kwargs['ef'] == '\n-':
                print(info_string, end='\n')
                print('-' * len(info_string), end='\n')
        else:
            print(info_string, end=kwargs['ef'])

    @staticmethod
    def fn_dirs_make(path_dir):
        """Create a directory path if it does not exist."""
        if not os.path.isdir(path_dir):
            try:
                os.makedirs(path_dir)
            except OSError as ose:
                print(ose)
        return path_dir

    @staticmethod
    def fn_filename(suffix):
        return f'{path_dst}/{datetime.today().strftime("%Y-%m-%d")}{suffix}'

    @staticmethod
    def fn_json_load(path_json):
        """Load json file."""
        with open(path_json, 'rb') as JsonFile:
            content = json.load(JsonFile)
        return content

    def fn_json_write(self, content, path_dst):
        if path_dst.endswith('.json'):
            pass
        else:
            path_dst = self.fn_filename('.json')
            warnings.warn(f'Filename not specified. Saving file as {path_dst}.')
        with open(path_dst, 'w') as file_json:
            json.dump(content, file_json, indent=4)
        file_json.close()

    def fn_mat_write(self, content, path_dst):
        if path_dst.endswith('.mat'):
            pass
        else:
            path_dst = self.fn_filename('.mat')
            warnings.warn(f'Filename not specified. Saving file as {path_dst}.')
        assert type(content) == dict
        scipy.io.savemat(path_dst, content)

    def fn_npy_write(self, content, path_dst):
        if path_dst.endswith('.npy'):
            pass
        else:
            path_dst = self.fn_filename('.npy')
            warnings.warn(f'Filename not specified. Saving file as {path_dst}.')
        with open(path_dst, 'wb') as file_npy:
            np.save(file_npy, content)

    @staticmethod
    def fn_validate_length_equal(inputs, fn_name):
        for i in range(len(inputs)):
            assert len(inputs[i]) == len(inputs[i + 1]),\
                f"{fn_name}: File lengths do not match." \
                f"{len(inputs[i])} vs {len(inputs[i + 1])}."
