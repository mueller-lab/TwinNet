#!/usr/bin/python3
#!/usr/local/opt/python@3.8/bin/python3

import sys

import os.path

from pathlib import Path

import uuid

import matplotlib

from matplotlib import pyplot

#from matplotlib.widgets import Button

import numpy as np

from dts_matplotlib import composition, draw, tools

from dts_commands import commandrun


heights = []


#dirpath_out = 'data/mat-algorithm1_local_maxima/neighs_20--threshold_0.01/'
dirpath_out = os.getenv( 'PARAM_DIR_OUTPUT') # 'data/mat-algorithm1_local_maxima/tmp/'



files_subset_start = int(os.getenv( 'PARAM_PLOT_START')) # int( sys.argv[ 1 ] )

files_subset_width = int(os.getenv( 'PARAM_PLOT_N')) # int( sys.argv[ 2 ] )

algorithm1_param_neighborhood_size = int(os.getenv( 'ALGO1_NEIGHBORHOOD')) # int( sys.argv[ 3 ] ) # default = 20

algorithm1_param_threshold = float(os.getenv( 'ALGO1_THRESHOLD')) # float( sys.argv[ 4 ] ) # default = 20

algorithm1_param_lower = float(os.getenv( 'ALGO1_PARAM_LOWER')) # float( sys.argv[ 5 ] ) # 0.955

algorithm1_param_lower_global = float(os.getenv( 'ALGO1_PARAM_LOWER_GLOBAL')) # float( sys.argv[ 6 ] ) # 0.955





argv_last_fixed = 1

indices = np.arange(0, len(sys.argv)-argv_last_fixed)

files_subset = []

for i in indices:
    
    if files_subset_width == -1:
        print( "i+5=", i+argv_last_fixed, ", argv=", len(sys.argv) )
        files_subset.append( sys.argv[i+argv_last_fixed] )
    else:
        if (i >= files_subset_start) and (i < files_subset_start+files_subset_width):
            files_subset.append( sys.argv[i+argv_last_fixed] )


commandsession = commandrun.Session( dirpath_root_ = "/tmp/commandrun/autoatlas_algorithm1_parameterized_write_to_disk.py/", session_uuid_ = uuid.uuid4() )

session_variable_boundaries_peaks_all = []


print( "files_subset=", files_subset )

for index, filename in enumerate(files_subset):

    print( "ARGV filename=", filename )

    scale = 1.5
    
    subplots_figure, subplots_axis_array = pyplot.subplots( 1, 6, figsize=(9*2*scale, 3.5*scale), dpi=80, gridspec_kw = { 'height_ratios': [ 10 ] }, sharex=False, sharey=False )

#    if len(files_subset)==1:
#        subplots_axis_array=[subplots_axis_array]

    subplots_figure.suptitle('Autoregressions: Algorithm1 (Local Maximum Finding): "%s"' % filename )

    subplots_figure.tight_layout()

    compositor = composition.SubfigureSingleColumn(subplots_figure, subplots_axis_array)

    drawer = draw.MatrixRangeCompare(compositor, True)

    drawer.neighborhood_size=algorithm1_param_neighborhood_size

    drawer.threshold = algorithm1_param_threshold # 0.03 # 0.02 # 0.020*0.47

    drawer.parameter_lower = algorithm1_param_lower

    drawer.global_maxima_threshold = algorithm1_param_lower_global

    drawer.matrix_load_from_filename(filename)

    filename_basename = os.path.basename( filename )
    
    rownr=0
    
#    drawer.plot_matrix_lut_vrange_step1(rownr,  "jet")
    drawer.plot_matrix_lut_vrange_step1(rownr,  "viridis")

    drawer.plot_matrix_lut_vrange_step2(rownr,  "flag")

#    drawer.plot_matrix_lut_vrange_step3(rownr,  "jet")
    drawer.plot_matrix_lut_vrange_step3(rownr,  "viridis")

    drawer.matrix_local_maxima_find();

    drawer.plot_matrix_lut_vrange_step4(rownr,  "jet")

#    drawer.plot_matrix_lut_vrange_step5(rownr,  "jet")
#    drawer.matrix_clip_tril_calc_boundaries()

    drawer.plot_matrix_rowsum_tril_step5(rownr,  "jet")

    drawer.plot_matrix_lut_vrange_step6(rownr,  "jet")

    drawer.matrix_local_maxima_serialize_json(dirpath_out+filename_basename+"-local_maxima.json");
    
    session_variable_boundaries_peaks_all.extend(drawer.boundaries_peaks);

    filename_output1 = dirpath_out+filename_basename+'-algorithm1_local_maxima.png'

    #pyplot.imsave(filename_output2, data_copy, cmap='gray', origin='lower')
    pyplot.savefig(filename_output1, dpi=300)
    #pyplot.show()

    filename_output2 = dirpath_out+filename_basename+'-algorithm1_local_maxima.svg'

    #pyplot.imsave(filename_output2, data_copy, cmap='gray', origin='lower')
    pyplot.savefig(filename_output2, dpi=300)

    pyplot.clf()


print( "Saving session files (commandsession.path=", commandsession.path, ")" )

print( " ...saving session file: session_variable_boundaries_peaks_all=\n", session_variable_boundaries_peaks_all )

np.save( str(Path( commandsession.path, 'session_variable_boundaries_peaks_all' )), session_variable_boundaries_peaks_all )




