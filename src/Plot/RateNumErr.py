from src.BaseClasses import ConfigFile as CF, Helper as H

import seaborn as sns, numpy as np, pandas as pd
from scipy.stats import poisson
import datetime as dt
import matplotlib.pyplot as plt, matplotlib.colors, matplotlib.dates as dates
import matplotlib.ticker as ticker

from src.Plot import Hazard, NumErrs, PlotHelper as PH
from src.DataWrangle import ClusterErrs

ALL_ERRS = ClusterErrs.readPrev_AllErrors()

#region: Pre-set Ops
def get_dfFail(df_occur):
    print('Fetching df_fail and df_pass ...')
        
    # Keep only labs
    df_labs = df_occur[df_occur['event'] == 'labs']    
    df_labs.is_copy = False
    
    # Keep only True repair/example
    df_labs = df_labs[~((df_labs['tool'] == 'False repair') | (df_labs['tool'] == 'False example'))]
    df_labs.is_copy = False

    # Comment below line to split plot into "example/repair", or uncomment to merge into single sem
    # df_sem  = NumErrs.get_dfSem(df_labs)    

    df_labs['compile_time'] = [dt.datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in df_labs['compile_time']]
    df_labs['time_hms'] = [i.time() for i in df_labs['compile_time']]

    df_pass = df_labs[df_labs['compiled'] == 1]
    df_fail = df_labs[df_labs['compiled'] == 0]

    return df_fail, df_pass

def time2num(t):
    '''Given a timeStamp, convert it to a 'number'. Ignores the date'''
    h, m, s = t.hour, t.minute, t.second
    seconds = m*60 + s
    return round(h + seconds / 3600.0, 1) # One hour has 3600 seconds

def add_date(timeObj, index_lab):
    tempDate = dt.datetime.strptime('2000', '%Y')
    dateObj = dt.datetime.combine(tempDate, timeObj) + dt.timedelta(days=index_lab)
    return dateObj

def add_time(timeObj, minutes):
    tempDate = dt.datetime.strptime('2000', '%Y')
    timeObj = dt.datetime.combine(tempDate, timeObj) + dt.timedelta(seconds=minutes*60)
    return timeObj.time()

def get_numAssign(df_passFail, lab, tool):
    '''Return the number of assignments for a given lab and tool'''
    df_labTool = NumErrs.get_dfLabTool(df_passFail, lab, tool)
    return len(df_labTool['assignment_id'].unique())

def get_maxLOC(df_passFail, lab, tool):
    df_labTool = NumErrs.get_dfLabTool(df_passFail, lab, tool)        
    return sum(df_labTool.groupby('assignment_id')['LOC'].max()) # 'Group by Max'

def get_count(df_range, yType):
    count = float(len(df_range))
    if yType == 'numErrors':
        return count
    elif yType == 'timeTaken':
        return H.div(sum(df_range['timeTaken (sec)']), count)
    elif yType == 'numAttempt':
        return H.div(sum(df_range['numAttempt']), count)

def get_dfNumErr(df_filter, df_passFail, yType):
    df_numErr = pd.DataFrame()
    cols = ['labs', 'tool', 'winStart', 'winEnd', yType, yType + '_assignment', 
                yType +'_LOC-sumAll', yType+'_LOC-sumWindow', yType +'_LOC-sumMaxAssign']
    labs = df_filter['labs'].unique()
    winSize, winSkip = CF.rate_winSize, CF.rate_winSkip

    for index_lab in range(len(labs)):
        lab = labs[index_lab]
        df_lab = df_filter[df_filter['labs'] == lab]

        # Hard code the start time to 14:00
        labStart, labEnd = dt.time(14, 0), dt.time(17, 15)
        
        for tool in df_lab['tool'].unique():
            df_tool     = df_lab[df_lab['tool'] == tool]
            num_assign  = get_numAssign(df_passFail, lab, tool)
            loc_sumAll  = sum(df_tool['LOC'])
            loc_maxAssign = get_maxLOC(df_passFail, lab, tool)
            
            winStart, winEnd = labStart, add_time(labStart, winSize)            
            while winStart < labEnd:
                df_range    = df_tool[(df_tool['time_hms']>=winStart) & (df_tool['time_hms']<winEnd)]
                count       = get_count(df_range, yType)
                loc_sumWin  = sum(df_range['LOC'])

                normalizers = [num_assign, loc_sumAll, loc_sumWin, loc_maxAssign]
                li  = [lab, tool, add_date(winStart, index_lab), add_date(winEnd, index_lab), count]
                li += map(H.div, [count]*4, [num_assign, loc_sumAll, loc_sumWin, loc_maxAssign])

                df_new      = pd.DataFrame([li], columns=cols)
                df_numErr   = pd.concat([df_numErr, df_new], ignore_index=True)

                winStart = add_time(winStart, winSkip)
                winEnd   = add_time(winStart, winSize)
        
    return df_numErr

#endregion

#region: Main Plotting Function - freq VS num_errors
def plot_snsCount(df_plot, ax, tool, indexT, indexS):
    if len(df_plot) > 0:
        x = df_plot['num_errors']
        mean = x.mean()
        k = np.arange(x.max() + 1)
        color, indexT, indexS = PH.get_color(tool, indexT, indexS)

        sns.countplot(x, order=k, color=color, alpha=0.5)
        ax.plot(k, poisson.pmf(k, mean)*len(x), 'ro', markersize=9)

    return indexT, indexS


def adjust_limits(fig, params):
    minX, maxX = H.fetchExists_list(params, ['minX', 'maxX'])
    minY, maxY = H.fetchExists_list(params, ['minY', 'maxY'])
    PH.set_axLim(fig, minX=minX, maxX=maxX, minY=minY, maxY=maxY)  

def set_xaxis(ax):
    #ax.xaxis.set_minor_locator(dates.HourLocator())
    #ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(ticker.FixedLocator([14, 15, 16, 17]))
    ax.xaxis.grid(True, which="minor")
    ax.xaxis.grid()

    ax.yaxis.grid(True, which="minor")
    ax.yaxis.grid()    
    
    # 
    
    #ax.xaxis.set_minor_locator(ticker.FixedLocator(np.linspace(0, 1, 11)[1:-1]))
    #ax.xaxis.set_major_formatter(dates.DateFormatter('\n%d'))
            
    #ax.tick_params(axis='x', rotation=45)  


def plot_bar(dict_dfNumErr, params, isPlotErrs=False):
    axes = []
    indexPlot = 0

    y, height, width = H.fetchExists_list(params, ['yType', 'height', 'width'])
    wspace, hspace = H.fetchExists_list(params, ['wspace', 'hspace'])
    nrows, ncols, height_ratios = H.fetchExists_list(params, ['nrows', 'ncols', 'height_ratios'])  

    fig = plt.figure(figsize=(width, height))
    gs = plt.GridSpec(nrows, ncols, height_ratios=height_ratios, wspace=wspace, hspace=hspace)
    points = []

    if isPlotErrs:
        # Pre-pend ALL first in sorting
        errSets = ['ALL'] + sorted([i for i in dict_dfNumErr.keys() if i != 'ALL']) 
    else:
        errSets = ['ALL']

    sns.set_context(rc = {'lines.linewidth': 0.5}) # Thinner lines


    for errSet in errSets: 
        df_numErr = dict_dfNumErr[errSet]  
        df_numErr['winStart_num'] = map(time2num, df_numErr['winStart'])
        df_numErr['winEnd_num'] = map(time2num, df_numErr['winEnd'])

        labs = df_numErr['labs'] .unique()

        for lab in sorted(labs):
            df = df_numErr[df_numErr['labs'] == lab]                  
            df_plot = df.sort_values(['winStart_num', 'tool'], ascending=[True,False])

            ax = fig.add_subplot(gs[indexPlot])     
            pointsAx = []

            for tool in df_plot['tool'].unique():
                pointsX = df_plot[df_plot['tool'] == tool]['winStart_num']
                pointsY = df_plot[df_plot['tool'] == tool][y]
                pointsAx.append((pointsX, pointsY))

                color = PH.get_palette([tool])[0]
                ax.plot(pointsX, pointsY, 'o-', markersize=2, color=color, linewidth=1, label=tool)

            #sns.factorplot(data=df_plot, ax=ax, kind="point", x="winStart_num", y=y,
            #    hue="tool", palette=PH.get_palette(df_plot['tool'].unique()))
            
            set_xaxis(ax)
            if isPlotErrs: ax.set_title(str(errSet))      
            if y == 'numErrors_LOC-sumAll':    # Cut short the (irrevant) highs for LOC div
                ax.set_ylim([ax.get_ylim()[0], ax.get_ylim()[1]/2.0])

            points.append(pointsAx)
            indexPlot += 1
    
    PH.set_legend(fig, ncol=len(dict_dfNumErr['ALL']['tool'].unique()))
    PH.set_axLim(fig)
    adjust_limits(fig, params)

    fpath, fname = H.fetchExists_list(params, ['fpath', 'fname'])
    PH.savefig(fig, fpath, fname, '')

    return fig, gs, points

#endregion
def get_errExp(errSet):
    if errSet == 'ALL': return errSet
    retList = []

    for errAct in errSet.split(';'):
        errAct = errAct.strip()
        if errAct != '':
            for errExp in ALL_ERRS:
                if str(ALL_ERRS[errExp].getIndex()) == errAct:
                    retList.append(errAct +': '+ errExp +'; ')
                    break
                    
    return H.joinList(retList, ' ')

def get_dict_dfNumErr(df_fail, df_pass, yType):
    print('Computing df_numErr(s) ...')
    dict_dfNumErr = {}
    topK = df_fail.groupby('errSet').size().reset_index(name='num_errSet').sort_values('num_errSet')[-10:]['errSet']

    for filter_errs in ['ALL'] + list(topK):
        if filter_errs == 'ALL':    
            df_filter = df_fail
        else: 
            df_filter = df_fail[df_fail['errSet'] == filter_errs]
        
        df_numErr = get_dfNumErr(df_filter, pd.concat([df_fail, df_pass]), yType)
        dict_dfNumErr[get_errExp(filter_errs)] = df_numErr

    return dict_dfNumErr


def plot(df_occur):
    df_fail, df_pass = get_dfFail(df_occur)    

    for yType in ['numErrors', 'timeTaken', 'numAttempt']:
        dict_dfNumErr = get_dict_dfNumErr(df_fail, df_pass, yType)

        for y in [yType, yType + '_assignment', 
                yType +'_LOC-sumAll', yType+'_LOC-sumWindow', yType +'_LOC-sumMaxAssign']:
            path = CF.path_rateNumErr + yType + '/'
            title = 'y={} winSize={} winSkip={}'.format(y, CF.rate_winSize, CF.rate_winSkip)
            fname = 'rate ' + title     

            params = {'yType':y, 'fpath':path, 'fname':fname, 'title':title}
            plot_bar(dict_dfNumErr, params, isPlotErrs=True)
