
import os, sys

if  not ('__file__' in locals() or '__file__' in globals()):
    __file__='.'
full_path = os.path.realpath(__file__)
currPath, configFilename = os.path.split(full_path)

#region: Paths

path_base = currPath + '/../../'
path_DF   = path_base + "data/"
path_results = path_base + 'plots/'

fname_feedback  = path_DF     + 'feedback.csv'
fname_pair = path_DF + 'pairs.csv'
fname_occur = path_DF + 'occurs.csv'
fname_errorIDs = path_DF + 'error_IDs.csv'

path_slopeCSV   = path_results + 'sheets_slope/'
path_slopePlot  = path_results + 'plots_slope/'
path_hazard     = path_results + 'plots_hazard/'
path_numErrs    = path_results + 'plots_numErrs/'
path_rateNumErr = path_results + 'plots_rate/'
path_compErrs   = path_results + 'plots_compErrs/'

#endregion

#region: Analyze settings

semesters       = [6, 7, 8]  # Which all its dumps to consider

rate_winSize = 10 # minutes [60, 10, 1]
rate_winSkip = 5  # minutes [30, 5, 1]

filter_errors = ['ALL', ['1;', '2;', '4;', '5;', '7;', '8;'], ['15;'], ['9;'], ['10;'], ['3;']]

#endregion
