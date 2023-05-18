import glob


class GlobTasks:
    """List paths of different image subsets from all images in a directory."""
    
    def __init__(self):
        self.title = 'SortTasks'

    @staticmethod
    def glob_dir_experiments(dir_experiments):
        """
        Get paths of experiment subdirs containing folder
        'TIFFs' within dir_experiments.
        """
        glob_experiments = [
            p.replace("\\", "/")
            for p
            in list(sorted(glob.glob(dir_experiments + '/*/TIFFs')))
        ]

        return glob_experiments

    @staticmethod
    def glob_dir_root(dir_root):
        """Get paths of subdirectories within dir_root."""
        glob_subdirs = sorted(glob.glob(dir_root + '/*/'))

        return glob_subdirs
    
    @staticmethod
    def glob_paths_files_tif(dir_images):
        """Get paths of all '.tif' files in a directory."""
        glob_tif = sorted(glob.glob(dir_images + '/*.tif'))
        
        return glob_tif
    
    @staticmethod
    def glob_paths_all(dir_images):
        """Get paths of all files in a directory."""
        glob_all = sorted(glob.glob(dir_images + '/*.*'))
        
        return glob_all

    @staticmethod
    def glob_variable(path):
        """
        Get paths of all files located in a directory based on custom
        glob pattern.
        """
        glob_variable = sorted(glob.glob(path))

        return glob_variable
