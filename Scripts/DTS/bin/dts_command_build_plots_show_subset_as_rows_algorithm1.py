#!/usr/local/opt/python@3.8/bin/python3
#!/usr/bin/python3

import sys

import os

from pathlib import Path

import uuid

import matplotlib

from matplotlib import pyplot

#from matplotlib.widgets import Button

import numpy as np

from dts_matplotlib import composition, draw, tools

from dts_commands import commandrun


# dts_command_build_plots_show_subset_as_rows_algorithm1.py 0 $PARAM_PLOT_N 20 0.0001 0.975 0.970 ${DTS_DIR_PROJECTS}/${PARAM_ORGANISM}/unified/MATs/TN_similarities*.mat
# os.getenv( '' )

#os.getenv( 'ALGO1_RESET')

files_subset_start = int(os.getenv( 'PARAM_PLOT_START')) # int( sys.argv[ 1 ] )

files_subset_width = int(os.getenv( 'PARAM_PLOT_N')) # int( sys.argv[ 2 ] )

algorithm1_param_neighborhood_size = int(os.getenv( 'ALGO1_NEIGHBORHOOD')) # int( sys.argv[ 3 ] ) # default = 20

algorithm1_param_threshold = float(os.getenv( 'ALGO1_THRESHOLD')) # float( sys.argv[ 4 ] ) # default = 20

algorithm1_param_lower = float(os.getenv( 'ALGO1_PARAM_LOWER')) # float( sys.argv[ 5 ] ) # 0.955

algorithm1_param_lower_global = float(os.getenv( 'ALGO1_PARAM_LOWER_GLOBAL')) # float( sys.argv[ 6 ] ) # 0.955

indices = np.arange(0, len(sys.argv)-1)

argv_last_fixed = 1

files_subset = []

for i in indices:
    
    if (i >= files_subset_start) and (i < files_subset_start+files_subset_width):
        
        files_subset.append( sys.argv[i+argv_last_fixed] )

heights = []

for x in files_subset:        
    heights.append(10)

commandsession = commandrun.Session( dirpath_root_ = "/tmp/commandrun/autoatlas_algorithm1_parameterized_plot_subset_as_rows.py/", session_uuid_ = uuid.uuid4() )

session_variable_boundaries_peaks_all = []




    
i=0

subplots_figure, subplots_axis_array = pyplot.subplots( len(files_subset), 6, figsize=(9*2,40), dpi=80, gridspec_kw = { 'height_ratios': heights }, sharex=False, sharey=False )

if len(files_subset)==1:
    subplots_axis_array=[subplots_axis_array]

subplots_figure.suptitle('Autoregressions: Algorithm1 (Local Maximum Finding): n=%02d files' % len(files_subset) )

#subplots_figure.tight_layout()

for index, filename in enumerate(files_subset):

    #subplots_figure, subplots_axis_array = pyplot.subplots( len(files_subset), 6, figsize=(9*2,30), dpi=80, gridspec_kw = { 'height_ratios': heights }, sharex=False, sharey=False )
    compositor = composition.SubfigurePerColumn(subplots_figure, subplots_axis_array)

    drawer = draw.MatrixRangeCompare(compositor)

    drawer.neighborhood_size=algorithm1_param_neighborhood_size

    drawer.threshold = algorithm1_param_threshold # 0.03 # 0.02 # 0.020*0.47

    drawer.parameter_lower = algorithm1_param_lower

    drawer.global_maxima_threshold = algorithm1_param_lower_global
    
    drawer.matrix_load_from_filename(filename)

    rownr=index
    
#    drawer.plot_matrix_lut_vrange_step1(rownr,  "jet")
    drawer.plot_matrix_lut_vrange_step1(rownr,  "viridis")

#    compositor.column_number_increase()
    drawer.plot_matrix_lut_vrange_step2(rownr,  "flag")

#    drawer.plot_matrix_lut_vrange_step3(rownr,  "jet")
    drawer.plot_matrix_lut_vrange_step3(rownr,  "viridis")

    drawer.matrix_local_maxima_find();

    drawer.plot_matrix_lut_vrange_step4(rownr,  "viridis")

#    drawer.plot_matrix_lut_vrange_step5(rownr,  "jet")
    drawer.plot_matrix_rowsum_tril_step5(rownr,  "jet")

    drawer.plot_matrix_lut_vrange_step6(rownr,  "jet")

    session_variable_boundaries_peaks_all.extend(drawer.boundaries_peaks);

#    pyplot.imsave(filename+'-saved.png', data_copy, cmap='gray', origin='lower')
pyplot.show()

#    pyplot.clf()

print( "Saving session files (commandsession.path=", commandsession.path, ")" )

print( " ...saving session file: session_variable_boundaries_peaks_all=\n", session_variable_boundaries_peaks_all )

np.save( str(Path( commandsession.path, 'session_variable_boundaries_peaks_all' )), session_variable_boundaries_peaks_all )



