import os
from datetime import datetime
import json
import numpy as np
import pandas as pd
import scipy.io
import warnings


class TNToolsGeneral:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    for evaluation purposes. This part of the toolset contains
    commonly used methods.
    """
    @staticmethod
    def fn_csv_read(path_csv):
        """
        Read csv and return as pandas DataFrame.
        """
        df = pd.read_csv(path_csv, index_col=0).reset_index(drop=True)
        return df

    @staticmethod
    def fn_csv_write(df, path_csv):
        """
        Write dataframe to csv file.
        """
        df.to_csv(path_csv, columns=df.columns, header=True)

    @staticmethod
    def fn_dirs_make(path_dir):
        """
        Create a directory path if it does not exist.
        """
        if not os.path.isdir(path_dir):
            try:
                os.makedirs(path_dir)
            except OSError as ose:
                print(ose)
        return path_dir

    @staticmethod
    def fn_filename(path_dst, suffix):
        """
        Create a standardized filename with date information
        for a given destination directory and suffix.
        """
        return f'{path_dst}/{datetime.today().strftime("%Y-%m-%d")}{suffix}'

    @staticmethod
    def fn_json_load(path_json):
        """
        Load JSON file.
        """
        with open(path_json, 'rb') as JsonFile:
            content = json.load(JsonFile)
        return content

    def fn_json_write(self, content, path_dst):
        """
        Write JSON file. If a filename without '.json' suffix is given,
        this method creates a standardized filename based on the date.
        """
        if path_dst.endswith(".json"):
            pass
        else:
            path_dst = self.fn_filename(path_dst, ".json")
            warnings.warn(f"Filename not specified. "
                          f"Saving file as {path_dst}.")
        with open(path_dst, "w") as file_json:
            json.dump(content, file_json, indent=4)
        file_json.close()

    def fn_mat_write(self, content, path_dst):
        """
        Write .mat file. If a filename without '.mat' suffix is given,
        this method creates a standardized filename based on the date.
        """
        if path_dst.endswith(".mat"):
            pass
        else:
            path_dst = self.fn_filename(path_dst, ".mat")
            warnings.warn(f"Filename not specified. "
                          f"Saving file as {path_dst}.")
        assert type(content) == dict
        scipy.io.savemat(path_dst, content)

    def fn_npy_write(self, content, path_dst):
        """
        Write .npy file. If a filename without '.npy' suffix is given,
        this method creates a standardized filename based on the date.
        """
        if path_dst.endswith(".npy"):
            pass
        else:
            path_dst = self.fn_filename(path_dst, ".npy")
            warnings.warn(f"Filename not specified. "
                          f"Saving file as {path_dst}.")
        with open(path_dst, "wb") as file_npy:
            np.save(file_npy, content)

    @staticmethod
    def fn_out(string, **kwargs):
        """
        Convenience function to print text with standardized format.
        """
        info_string = f'{string}'
        if 'ef' in kwargs and kwargs['ef'] == '\n\n':
            print(info_string, end='\n')
            print('-' * len(info_string))
        else:
            print(info_string, end=kwargs.get('ef', ''))

    @staticmethod
    def fn_subdir_make(dir_dst, n_dir):
        """
        Create a subdirectory within a
        directory and return subdirectory path.

        Parameters
        ----------
        dir_dst: str
            Path to directory in which subdirectory
            should be created.
        n_dir: str
            Name of subdirectory to be created in
            dir_dst.

        Returns
        -------
        dir_dst_n: str
            Path to new subdirectory in dir_dst.
        """
        dir_dst_n = str(os.path.join(
            dir_dst, n_dir
        )).replace("\\", "/")
        try:
            if not os.path.isdir(dir_dst_n):
                os.makedirs(dir_dst_n)
        except OSError as ose:
            print(ose)
        return dir_dst_n

    @staticmethod
    def fn_validate_length_equal(inputs, fn_name):
        """
        Validate that two inputs contain the same number of items.
        """
        for i in range(len(inputs)):
            assert len(inputs[i]) == len(inputs[i + 1]),\
                f"{fn_name}: File lengths do not match." \
                f"{len(inputs[i])} vs {len(inputs[i + 1])}."
