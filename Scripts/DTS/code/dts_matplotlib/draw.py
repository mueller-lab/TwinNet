import sys

import math

import re

from pathlib import Path

import scipy.io

import scipy.signal

import scipy.ndimage as ndimage

import scipy.ndimage.filters as filters

#import pandas as pd

from copy import copy, deepcopy

import numpy as np

import json

from json import JSONEncoder

from matplotlib import pyplot

np.set_printoptions(threshold=sys.maxsize)

def matrixdiagonals_tlbr(a):
    result = [a[::-1,:].diagonal(i) for i in range(-a.shape[0]+1,a.shape[1])]
    return result

def matrixdiagonals_trbl(a):
    result = []
    result.extend(a.diagonal(i) for i in range(a.shape[1]-1,-a.shape[0],-1))
    return result

def rowsum(a):
    rowsums = np.empty(0)
    for rowlist in a:
        rowlistsum = 0.0
        for element in rowlist:
            rowlistsum = rowlistsum + element
            rowsums=np.append(rowsums, rowlistsum)
    return rowsums
    
def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)

class LocalJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)
    
class MatrixRangeCompare:

    def __init__(self, compositor_, flag_titles_=False):
        self.compositor=compositor_

        self.parameter_lower = 0.955
        self.neighborhood_size = 10
        self.threshold = 0.020*0.47
        self.flag_titles = flag_titles_
#ZEBRAFISH:        self.global_maxima_threshold=
#MEDAKA:        self.global_maxima_threshold=self.parameter_lower-0.000025
#C. ELEGANS
        self.global_maxima_threshold=self.parameter_lower-0.025

        self.parameter_find_peaks_distance=15 #4
        self.parameter_find_peaks_prominence=10 #5        

    def matrix_load_from_filename(self, filename):

        print( "PLOTTING = ", filename )

        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html

        re_mat = re.compile( '\.mat' );
        re_npy = re.compile( '\.npy$' );
        re_csv = re.compile( '\.npy$' );
        
        #if re_mat.match( filename ):
        if 1:
            print( ".mat file detected: ", filename )
            
            mat = scipy.io.loadmat( filename ) # 'TN_similarities_0089--A003--PO01--E000.mat')
        
            mat_keys = sorted(mat.keys())
        
            print(mat_keys)
    
            self.data_original = mat['data']
            self.data = mat['data']

        #print( self.data )
        # else:
        #     if re_npy.match( '.npy' ):
        #         mat = np.load( Path(filename).with_suffix('.npy') ) # 'TN_similarities_0089--A003--PO01--E000.mat')
        #         self.data_original = mat
        #         self.data = mat
        #     else:
        #         if re_npy.match( '.csv' ):
        #             #Using pandas
        #             #mat = pd.read_csv( Path(filename).with_suffix('.npy'), sep=",", header=1, index_col=1 )
        #             mat = np.loadtxt( Path(filename).with_suffix('.npy'), delimiter=',', skiprows=1)
        #             mat = np.delete(mat, 0, axis = 1)
        #             self.data_original = mat
        #             self.data = mat
            
        print(self.data.shape)

        #    data = data[:150,:150]
        #ZEBRAFISH: self.data = self.data[:230,:230]
        #self.data = self.data[:256,:256]
        #MEDAKA:
        #self.data = self.data[:230,:230]
        #C. ELEGANS
#        self.data = self.data[:110,:110]
    
        #    print(data)

        #    print("Example pos [0][0]=", data[0][0])
    
        self.data_copy = deepcopy(self.data);
        
        self.data_copy2 = deepcopy(self.data);

        #self.data_copy = np.multiply(0.25, self.data_copy);

        #self.data_copy = np.add(0.75, self.data_copy);

    def init_data_clipped(self):

#        print( "self.data_copy=\n", self.data_copy )

        self.data_copy_clipped = np.clip(self.data_copy, self.parameter_lower, 1.0 )

        self.data_copy_clipped[ self.data_copy_clipped<=self.parameter_lower ] = 0

    def matrix_local_maxima_find(self):

        #See: https://stackoverflow.com/questions/9111711/get-coordinates-of-local-maxima-in-2d-array-above-certain-value

        self.init_data_clipped( )

#        print( "data_copy_clipped", self.data_copy_clipped )

        tmp = np.tril(self.data_copy_clipped,-1);

        self.data_copy_clipped_tril_rowsum = np.sum(tmp, axis=1).tolist()


        self.data_copy_clipped_max = filters.maximum_filter(self.data_copy_clipped, self.neighborhood_size)

        maxima = (self.data_copy_clipped == self.data_copy_clipped_max)

#        print( "maxima", maxima )

        self.data_copy_clipped_min = filters.minimum_filter(self.data_copy_clipped, self.neighborhood_size)

        diff = ((self.data_copy_clipped_max - self.data_copy_clipped_min) > self.threshold)

        maxima[diff == 0] = 0

        labeled, num_objects = ndimage.label(maxima)

        slices = ndimage.find_objects(labeled)

        self.local_maxima_x, self.local_maxima_y = [], []

        for dy,dx in slices:
            x_center = (dx.start + dx.stop - 1)/2
            self.local_maxima_x.append(x_center)
            y_center = (dy.start + dy.stop - 1)/2    
            self.local_maxima_y.append(y_center)

            #pyplot.savefig('/tmp/result.png', bbox_inches = 'tight')

        self.local_maxima_points = []

        for index, element in enumerate(self.local_maxima_x):

            delta_prev=-1

            if index > 0:
                delta_prev=self.local_maxima_x[index-1]-self.local_maxima_x[index]

            self.local_maxima_points.append( { "x" : self.local_maxima_x[index], "y" : self.local_maxima_y[index], "delta_prev" : delta_prev } )

#        print( "local maxima points: ", self.local_maxima_points )

        return self.local_maxima_points

    def matrix_clip_tril_calc_boundaries(self):

        ## AMP
        data_copy_clipped_tril=self.data_copy_clipped.copy()

        data_copy_clipped_tril=np.tril( data_copy_clipped_tril )
                
        self.data_copy_clipped_tril_rowsum = data_copy_clipped_tril.sum(axis=1)

        #data = self.data_copy_clipped_tril_rowsum 

        diagonals = matrixdiagonals_tlbr( self.data_copy_clipped )

        self.diagonals_sums = []

        bucket = 0.0
        
        i=0

        for d in diagonals:
            if (i%2)==0:
                self.diagonals_sums.append( d.sum()+bucket )
            else:
                bucket=d.sum()
            i = i + 1

#        print( "diagonals_sums len=", len(diagonals_sums), "=\n", diagonals_sums )




        self.diagonals_sums_amp = [math.sqrt(n)*8 for n in self.diagonals_sums]

        ## AMP_INVERT
        self.diagonals_sums_amp_inv = [100-n for n in self.diagonals_sums_amp]        

        ## AMP_INVERT/FINDPEAKS

        self.boundaries_peaks, _ = scipy.signal.find_peaks( np.flip(self.diagonals_sums_amp_inv), distance = self.parameter_find_peaks_distance, prominence = self.parameter_find_peaks_prominence )
#        peaks = scipy.signal.find_peaks_cwt( np.flip(diagonals_sums_amp_inv), np.arange(1,10) )

        print( "boundaries_peaks=\n", self.boundaries_peaks )

        self.boundaries_peaks_y = []

        for i, x in enumerate(self.boundaries_peaks):
            self.boundaries_peaks_y.append( 100 ) #diagonals_sums_amp_inv[i] )

        print( "boundaries_peaks_y=\n", self.boundaries_peaks_y )

        self.boundaries_peaks_listmodel=[]
        
#        for element in np.flip(self.boundaries_peaks):
#            self.boundaries_peaks_listmodel.append( { "pos" : 230 - int(element) } );

        for element in self.boundaries_peaks:
            self.boundaries_peaks_listmodel.append( { "pos" : int(element) } );


    def matrix_local_maxima_serialize_json(self, filename_):

        jsonObject = { "filename_source" : filename_, "local_maxima_points": self.local_maxima_points, "row_sum_tril" : self.data_copy_clipped_tril_rowsum, "boundaries_peaks" : self.boundaries_peaks_listmodel }

            
#        jsonObjectAsString = json.dumps(jsonObject, cls=LocalJsonEncoder)  # or use dump() to write array into file

#        print("matrix_local_maxima_serialize(array_): filename=", filename_, " ..: ")

        with open(filename_, "w") as filehandle:

            json.dump([jsonObject], filehandle, cls=LocalJsonEncoder)

            print("Done writing to file:", filename_)

#        print(jsonObjectAsString)
    
    def cell_get(self, rownr):
        return self.compositor.subplots_axis_array_pointer_for_column(rownr)

    def plot_matrix_lut_vrange_step1(self, rownr, lutname):

        #ZEBRAFISH: vmin=0.0
        vmin=-1.0
        vmax=1.0
        
#        img = self.cell_get(rownr).imshow(self.data, interpolation='nearest', vmin=vmin, vmax=vmax, cmap=pyplot.get_cmap(lutname), origin='lower')
        img = self.cell_get(rownr).imshow(self.data_original, cmap=pyplot.get_cmap(lutname), origin='lower')
            
        if self.flag_titles:
            self.cell_get(rownr).set_title('lut="%s"' % ( lutname ), fontsize=6)

        self.cell_get(rownr).set_xlabel('time [hpf]')

        self.cell_get(rownr).set_ylabel('time [hpf]')

        self.compositor.subplots_figure.colorbar(img, fraction=0.046, pad=0.04) # Similar to subplots_figure.colorbar(im, cax = cax)

        self.compositor.column_number_increase()


    def plot_matrix_lut_vrange_step2(self, rownr, lutname):
        
        # cm = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict2, 1024)

        vmin=0.0
        vmax=1.0

        img = self.cell_get(rownr).imshow(self.data_copy, cmap=pyplot.get_cmap( lutname ), origin='lower')
            
        if self.flag_titles:
            self.cell_get(rownr).set_title('lut="%s"' % ( lutname ), fontsize=6)

        self.cell_get(rownr).set_xlabel('time [hpf]')

        self.cell_get(rownr).set_ylabel('time [hpf]')

        self.compositor.subplots_figure.colorbar(img, fraction=0.046, pad=0.04) # Similar to subplots_figure.colorbar(im, cax = cax)

        self.compositor.column_number_increase()


    def plot_matrix_lut_vrange_step3(self, rownr, lutname):
    
        vmin=self.parameter_lower
        vmax=1.0

        img = self.cell_get(rownr).imshow( self.data_copy, interpolation='nearest', vmin=vmin, vmax=vmax, cmap=pyplot.get_cmap(lutname), origin='lower')
            
        if self.flag_titles:
            self.cell_get(rownr).set_title('lut="%s"' % ( lutname ), fontsize=6)

        self.cell_get(rownr).set_xlabel('time [hpf]')

        self.cell_get(rownr).set_ylabel('time [hpf]')

        self.compositor.subplots_figure.colorbar(img, fraction=0.046, pad=0.04) # Similar to subplots_figure.colorbar(im, cax = cax)

        self.compositor.column_number_increase()
    

    def plot_matrix_lut_vrange_step4(self, rownr, lutname):

        self.init_data_clipped()

        vmin=self.parameter_lower

        vmax=1.0

#        self.data_copy_clipped[self.data_copy_clipped>=self.parameter_lower] = 1
        
        tmp2 = self.data_copy_clipped.copy()

        tmp2 = np.tril( tmp2, -1 );

        img = self.cell_get(rownr).imshow( tmp2, interpolation='nearest', vmin=vmin, vmax=vmax, cmap=pyplot.get_cmap( lutname ), origin='lower' )
            
        if self.flag_titles:
            self.cell_get(rownr).set_title('lut="%s", clip: %.2f-%.2f' % ( lutname, self.parameter_lower, 1.0 ), fontsize=6)

        self.cell_get(rownr).set_xlabel('time [hpf]')

        self.cell_get(rownr).set_ylabel('time [hpf]')

        self.compositor.subplots_figure.colorbar(img, fraction=0.046, pad=0.04) # Similar to subplots_figure.colorbar(im, cax = cax)

        self.cell_get(rownr).autoscale(False)

        img = self.cell_get(rownr).plot( self.local_maxima_x, self.local_maxima_y, 'ro', markersize=2 )


        global_maxima_points_coord_planes = np.nonzero( self.data_copy_clipped>(self.global_maxima_threshold) )

        #print( "global_maxima_points_coords=\n", global_maxima_points_coord_planes )

        img = self.cell_get(rownr).plot( global_maxima_points_coord_planes[0], global_maxima_points_coord_planes[1], 'wo', markersize=0.5 )
        

        self.compositor.column_number_increase()

    def plot_matrix_lut_vrange_step5(self, rownr, lutname):

        self.init_data_clipped()

        vmin=self.parameter_lower
        
        vmax=1.0

        img = self.cell_get(rownr).imshow( self.data_copy_clipped, interpolation='nearest', vmin=vmin, vmax=vmax, cmap=pyplot.get_cmap(lutname), origin='lower')

        if self.flag_titles:
            self.cell_get(rownr).set_title('lut="%s", clip: %.2f-%.2f' % ( lutname, self.parameter_lower, 1.0 ), fontsize=6)

        self.compositor.subplots_figure.colorbar(img, fraction=0.046, pad=0.04) # Similar to subplots_figure.colorbar(im, cax = cax)
            
        self.cell_get(rownr).autoscale(False)

        img = self.cell_get(rownr).plot( self.local_maxima_x, self.local_maxima_y, 'ro', markersize=3 )

        self.cell_get(rownr).set_title('Local maxima: neigh_s='+("%02d" % self.neighborhood_size)+", threshold="+("%.02f" % self.threshold), fontsize=6)

        self.cell_get(rownr).set_xlabel('time [hpf]')

        self.cell_get(rownr).set_ylabel('time [hpf]')

        self.compositor.column_number_increase()

    def plot_matrix_rowsum_tril_step5(self, rownr, lutname):

        param_plot_alpha=0.6

        self.init_data_clipped()

        self.matrix_clip_tril_calc_boundaries()
#        print( "self.data_copy_clipped shape=", self.data_copy_clipped.shape, "min=", np.min(self.data_copy_clipped), "max=", np.max(self.data_copy_clipped) )

        # test = np.array( [
        #     [0,0,0,8,8,8],
        #     [0,0,2,2,2,0],
        #     [0,0,3,3,3,0],
        #     [0,2,2,2,0,0],
        #     [1,1,1,0,0,0],
        #     [1,1,2,0,0,0]
        # ], int )
        
#        print( "data_copy_clipped=\n", self.data_copy_clipped )

        #np.save( "data_copy_clipped", self.data_copy_clipped )

# MUE: Interesting trick        
#        tmp2=np.rot90( np.tril(np.rot90(tmp)), 3)

#horizontal
#        img = self.cell_get(rownr).barh( np.flip( np.arange(0, len(self.data_copy_clipped_tril_rowsum )) ), self.data_copy_clipped_tril_rowsum , height=1.0, align='center', color='blue', alpha=param_plot_alpha )

        img = self.cell_get(rownr).barh( np.flip( np.arange(0, len(self.diagonals_sums)) ), self.diagonals_sums_amp, height=1.0, align='center', color='green', alpha=param_plot_alpha )



        img = self.cell_get(rownr).barh( np.flip( np.arange(0, len(self.diagonals_sums)) ), self.diagonals_sums_amp_inv, height=1.0, align='center', color='red', alpha=0.8 )




        img = self.cell_get(rownr).barh( self.boundaries_peaks, self.boundaries_peaks_y, height=2.0, align='center', color='black', alpha=0.3 )






        if self.flag_titles:
            self.cell_get(rownr).set_title('lut="%s", clip: %.2f-%.2f' % ( lutname, self.parameter_lower, 1.0 ), fontsize=6)

#        self.compositor.subplots_figure.colorbar(img, fraction=0.046, pad=0.04) # Similar to subplots_figure.colorbar(im, cax = cax)
            
        self.cell_get(rownr).autoscale(False)

#        img = self.cell_get(rownr).plot( self.local_maxima_x, self.local_maxima_y, 'ro', markersize=3 )

#        self.cell_get(rownr).set_title('Rowsum tril')

        self.cell_get(rownr).set_xlabel('rowsum [cosine sums]')

        self.cell_get(rownr).set_ylabel('pos [npos]')

#        self.cell_get(rownr).set_xlim( [0, np.max(self.data_copy_clipped_tril_rowsum )] )
        self.cell_get(rownr).set_xlim( [0, 100] )
#        self.cell_get(rownr).set_xscale('log')
        self.cell_get(rownr).set_ylim( [0, self.data_copy_clipped_tril_rowsum.size] )
        
        self.cell_get(rownr).invert_yaxis()

        
#        self.cell_get(rownr).legend( [ "horizontal", "amp", "amp_inverted", "boundaries" ] )
        
        self.compositor.column_number_increase()

    def plot_matrix_lut_vrange_step6(self, rownr, lutname):

        self.init_data_clipped() 

        data = self.data_copy_clipped

        print( "create histogram, plot at column=", self.compositor.colnr )
        
#        bins, edges = np.histogram(self.data_original, 50)
        bins, edges = np.histogram(data, 80*80)

        left,right = edges[:-1],edges[1:]
        
        X = np.array([left,right]).T.flatten()
        
        Y = np.array([bins,bins]).T.flatten()

        #print( "create histogram, plot X=", X )

        #print( "create histogram, plot Y=", Y )

        img = self.cell_get(rownr).plot(X,Y)

        ## PLOT THRESHOLD VALUES AS VERTICALS

        X_WHERE = X[X>=self.global_maxima_threshold];

        print( "X_WHERE[0]=", X_WHERE[0] )

        img = self.cell_get(rownr).vlines( [ X_WHERE[0] ], ymin=0, ymax=500, color="green" )

        if self.flag_titles:
            self.cell_get(rownr).set_title('Histogram')
        
        self.cell_get(rownr).set_xlabel('histogram')
    
        self.cell_get(rownr).set_ylabel('count')

        #ZEBRAFISH
#        self.cell_get(rownr).set_xlim( [self.parameter_lower, 1.0] )

        #MEDAKA
        self.cell_get(rownr).set_xlim( [self.parameter_lower-0.03, 1.0] )

        #C. ELEGANS
        self.cell_get(rownr).set_xlim( [self.parameter_lower-0.003, 1.0] )

        #ZEBRAFISH
        #self.cell_get(rownr).set_ylim( [0, 500] )

        #MEDAKA
        self.cell_get(rownr).set_ylim( [0, 500*2] )

        #C. ELEGANS
        self.cell_get(rownr).set_ylim( [0, 500*1] )

        self.cell_get(rownr).legend( [ "similarities", "cutoff-cosmax" ] )

        self.compositor.column_number_increase()
