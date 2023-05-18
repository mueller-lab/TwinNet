import sys

from pathlib import Path

#import pandas as pd
import numpy as np

class ConvertToNumpy:

    def __init__(self, filename):
        self.filename
    
    def load(self):

        re_csv = re.compile( '\.csv$' );
        
        if re_npy.match( '.csv' ):
            mat = np.loadtxt( Path(filename).with_suffix('.npy'), delimiter=',', skiprows=1)
            mat = np.delete(mat, 0, axis = 1)
            return mat

class ConvertToPandas:

    def __init__(self, filename):
        self.filename
    
    def load(self):

        re_csv = re.compile( '\.csv$' );
        
        if re_npy.match( '.csv' ):
            #Using pandas
            mat = pd.read_csv( Path(filename).with_suffix('.npy'), sep=",", header=1, index_col=1 )
            return mat

