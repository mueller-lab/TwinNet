import glob
import json
import numpy as np
import os
import pathlib

from .tngeneral import TNToolsGeneral
from .tnarroweval import TNToolsArrowEval


class TNToolsArrow:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used with tools in 'tnarroweval.py' and
    'tnarrowplot.py' to utilize TN predicted developmental stages for
    detection of deviation from normal development.
    """
    def __init__(self, size_img=224, size_img_min=300):
        self.param_img_size = size_img
        self.param_img_size_min = size_img_min
        self.tools_general = TNToolsGeneral()
        self.tools_arrow_eval = TNToolsArrowEval(size_img,
                                                 size_img_min)

    def embeddings_save(self, embeddings, dir_dst, **kwargs):
        """
        Save embeddings to .npy files.

        Parameters
        ----------
        embeddings: dict
            Dictionary with structure of key: image index
            and value: embedding.
        dir_dst: str
            Path to directory where embeddings should
            be saved.
        kwargs: Variable keyword arguments
            See below.

        Keyword arguments
        -----------------
        str_sign: str
            Signature phrase to add to the names of .npy files
            when saving embeddings.
        """
        str_sign = kwargs.get("str_sign", "")

        try:
            os.makedirs(dir_dst)
        except OSError:
            pass

        for k, v in embeddings.items():
            p_dst_embedding = f"{dir_dst}/embeddings_{str_sign}" \
                              f"_{str(k).zfill(5)}.npy"
            self.tools_general.fn_npy_write(v, p_dst_embedding)

    @staticmethod
    def embeddings_load(dir_src):
        """
        Load embeddings from .npy files.

        Parameters
        ----------
        dir_src: str
            Path to directory where embeddings are saved.

        Returns
        -------
        embeddings: dict
            Dictionary with structure of key: image index
            and value:embedding.
        """
        ps_embeddings = list(sorted(glob.glob(f"{dir_src}/*.npy")))
        embeddings = {
            int(pathlib.PurePath(p).stem[-5:]): np.load(p)
            for p
            in ps_embeddings
        }
        return embeddings

    def embeddings_test_save(self, embeddings_test, paths_test_dst_embeddings):
        """
        Save embeddings of test embryos to directory with
        similar structure as in 'embeddings_test', which
        corresponds to the following structure:
        embeddings_test = {
            category_embryo: {
                path_dir_embryo: {
                    {k_tp: embedding, ...}
                ...}
            ...}
        ...}
        """
        # Loop through categories normal, disintegrating, patterning defects
        for k_cat, v_cat in embeddings_test.items():
            # Loop through embryo paths
            for k_emb, v_emb in v_cat.items():
                # Prepare embryo directory path for access of directory names
                p = pathlib.PurePath(k_emb)
                # Prepare directory path for embryo embeddings
                dir_dst_embryo = f"{paths_test_dst_embeddings}/" \
                                 f"{k_cat}/{k_emb}/"
                # Save embeddings sorted by timepoints
                self.embeddings_save(v_emb, dir_dst_embryo)

    @staticmethod
    def embeddings_test_load(paths_test_dst_embeddings):
        """
        Load embeddings of test embryos from directory to
        dictionary with similar structure as in dst
        directory, which has the following structure:
        embeddings_test/
            category_embryo/
                path_dir_embryo/
                    embeddings__00XYZ
        """
        # Glob for embedding directories containing .npy files
        paths_embeddings = list(sorted(
            glob.glob(f"{paths_test_dst_embeddings}/*/*/")
        ))
        # Prepare dictionary to store embeddings
        embeddings = dict()
        # Loop through paths to embedding directories
        for path_embeddings in paths_embeddings:
            # Prepare embryo directory path for access of directory names
            p = pathlib.PurePath(path_embeddings)
            p_cat = p.parent.stem
            p_emb = p.stem
            if p_cat not in embeddings:
                embeddings[p_cat] = dict()

            # Glob for embedding .npy files
            embeddings[p_cat][p_emb] = {
                int(pathlib.PurePath(p).stem[-5:]): np.load(p)
                for p
                in list(sorted(glob.glob(f"{path_embeddings}/*.npy")))
            }
        return embeddings

    @staticmethod
    def paths_embryos_from_json_fn(path_json_dataset,
                                   dir_src):
        """
        Load the content of a .json file containing paths to
        embryo directories.

        Parameters
        ----------
        path_json_dataset: str
            Path to json file containing paths to embryo directories
            sorted to the categories 'paths_normal', 'paths_disintegrating',
            'paths_patterning_defects'
        dir_src: str
            Path to directory where test
            dataset is stored.

        Returns
        -------
        file_json_dataset: dict
            Dictionary of lists with paths to dataset files.
        """

        with open(path_json_dataset, 'r') as json_file:
            file_json_dataset = json.load(json_file)

        dirs_normal = file_json_dataset['paths_normal']
        dirs_disintegrating = file_json_dataset['paths_disintegrating']
        dirs_patterning_defects = file_json_dataset['paths_patterning_defects']

        dirs_normal = [f"{dir_src}{p[1:]}"
                       .replace("\\", "/")
                       .replace("//", "/")
                       for p in dirs_normal]
        dirs_disintegrating = [f"{dir_src}{p[1:]}"
                               .replace("\\", "/")
                               .replace("//", "/")
                               for p in dirs_disintegrating]
        dirs_patterning_defects = [f"{dir_src}{p[1:]}"
                                   .replace("\\", "/")
                                   .replace("//", "/")
                                   for p in dirs_patterning_defects]

        string_info = '[INFO] Working on {} normal, ' \
                      '{} disintegrating, ' \
                      '{} patterning defective embryo directories.'\
                      .format(len(dirs_normal),
                              len(dirs_disintegrating),
                              len(dirs_patterning_defects))
        dirs_embryos = {'paths_normal': dirs_normal,
                        'paths_disintegrating': dirs_disintegrating,
                        'paths_patterning_defects': dirs_patterning_defects}
        print(string_info, end='\n')
        print('-' * len(string_info), end='\n')

        return dirs_embryos

    def similarities_calc(self,
                          embeddings_1,
                          embeddings_2,
                          embeddings_3,
                          embeddings_test,
                          dir_dst,
                          **kwargs):
        """
        Calculate similarities.
        """
        # Get the number of image indices to include
        limit_indices = kwargs.get("limit_indices", None)
        # Loop through test embedding categories
        # (normal, disintegrating, patterning defects)
        for k_cat, v_cat in embeddings_test.items():
            # Loop through embryo directories
            for k_emb, v_emb in v_cat.items():
                # Print info
                print(f'[INFO][{k_cat}][{k_emb}]', end='\n')
                # Prepare dst directory for similarity .csv files
                dir_dst_emb = self.tools_general.fn_subdir_make(
                    dir_dst, f"{k_cat}/{k_emb}/"
                )

                # Set limit of frame count to include in analysis
                if limit_indices is not None:
                    keys_embeddings = [
                        k for k in v_emb.keys()
                        if int(k) <= limit_indices
                    ]
                else:
                    keys_embeddings = list(v_emb.keys())

                for i in keys_embeddings:
                    print(f'[INFO] {i}/{len(keys_embeddings)}',
                          end='\r')
                    path_dst_emb_df = os.path.join(
                        dir_dst_emb,
                        f"{k_emb}_df_similarities_{str(i).zfill(5)}.csv"
                    )

                    # Calculate similarities
                    df = self.tools_arrow_eval.\
                        similarities_calc_to_df_embeddings_both(
                            embeddings_1, embeddings_2, embeddings_3, v_emb[i]
                        )
                    df.to_csv(path_dst_emb_df)
