import seaborn as sns, numpy as np, pandas as pd
from scipy.stats import poisson
import datetime as dt

import matplotlib.pyplot as plt, matplotlib.colors, matplotlib.dates as dates
import matplotlib.ticker as ticker

from src.Plot import Hazard, PlotHelper as PH
from src.BaseClasses import ConfigFile as CF, Helper as H

#region: Best/Avg Lines Sem 

def get_lineBest(linesSem):
    lineBest = {}   

    for line in linesSem:
        for x, y in sorted(line.items()):
            if x not in lineBest and not pd.isnull(y):   # If not such x-y exists, 
                lineBest[x] = y         # add it
            # Else if the new y-value is better (lower)
            elif not pd.isnull(y) and y < lineBest[x]:   
                lineBest[x] = y         # use the new value

    return lineBest

def get_lineAvg(linesSem):
    lineAvg, count = {}, {}

    for line in linesSem:
        for x, y in line.items():
            if x not in lineAvg and not pd.isnull(y):   # If not such x-y exists, 
                lineAvg[x] = y         # add it
                count[x]    = 1
            elif not pd.isnull(y):                   # Else 
                lineAvg[x] += y        # sum with old y 
                count[x]    += 1        # (and inc count)

    # Average out the y-val
    for x in lineAvg:
        lineAvg[x] = lineAvg[x] / count[x] 
    return lineAvg

def get_lineDiff(line1, line2):
    '''Returns line1 - line2'''
    lineDiff = {}
    for x in line1:
        if x in line2:
            if pd.isnull(line1[x]) or pd.isnull(line2[x]):
                lineDiff[x] = None    
            else:
                lineDiff[x] = line1[x] - line2[x]
        else:
            lineDiff[x] = None

    for x in line2:
        if x not in line1:
            lineDiff[x] = None

    return lineDiff
#endregion

#region: Access/Create Lines from plot 
def get_axLine(ax, indexL):
    '''Some plots have "dummy" null lines. Ignore them to get actual lines'''
    lines = ax.lines
    actLines = []
    for line in lines:
        for ypoint in line.get_xydata()[:,1]:
            if not pd.isnull(ypoint):
                actLines.append(line)
                break

    return actLines[indexL]

def get_dictXY(ax, params, indexAx, indexL):
    kmfs, points, maxX = H.fetchExists_list(params, ['kmfs', 'points', 'maxX'])
    nsplits = len(CF.semesters) - 1 + 2 # -1 to discount feedback sem, +2 to add repair/eg

    x1 = get_axLine(ax, indexL).get_xydata()[:,0]
    if kmfs is not None: # If survival plots passed, accurately predicting using kmf
        index = indexAx*nsplits + indexL
        x1 = range(0, maxX+1)
        y1 = [kmfs[index].predict(x) for x in x1]
    elif points is not None: # Elif points for each axes passed
        x1, y1 = points[indexAx][indexL]
    else:   # go old-fashion: Pick lines from axesOrig  
        y1 = get_axLine(ax, indexL).get_xydata()[:,1]           

    return {i:j for i, j in zip(x1, y1)}


def delta_axes(ax, params, indexAx):
    lineRepair = get_dictXY(ax, params, indexAx, 0)  # Repair is the first line
    lineEg = get_dictXY(ax, params, indexAx, 1)      # Example is the second

    # Lines of other sems
    numLines_hint = 2
    endRange = len(CF.semesters) - 1 + numLines_hint
    linesSem = [get_dictXY(ax, params, indexAx, i) for i in range(numLines_hint, endRange)] 

    lineBest = get_lineBest(linesSem)    
    lineAvg  = get_lineAvg(linesSem)

    bestR = get_lineDiff(lineRepair, lineBest)
    bestE = get_lineDiff(lineEg, lineBest)

    avgR = get_lineDiff(lineRepair, lineAvg)
    avgE = get_lineDiff(lineEg, lineAvg)

    return bestR, bestE, avgR, avgE

def plot_diff(axOrig, ax, lineR, lineE, ylab, params):
    xlab, ylab = axOrig.get_xlabel(), ylab
    cr, ce = PH.get_palette(['True repair'])[0], PH.get_palette(['True example'])[0]
    minX, maxX, markersize = H.fetchExists_list(params, ['minX', 'maxX', 'markersize'])
    if markersize is None: markersize = 1
    
    def get_xy(lines):
        xs, ys = [], []
        for x,y in sorted(lines.items()):
            if maxX == None or x<=maxX:
                xs.append(x); ys.append(y)
        return xs, ys

    xR, yR = get_xy(lineR)
    xE, yE = get_xy(lineE)
    
    ax.plot(xR, yR, 'o-', markersize=markersize, c=cr, linewidth=1)
    ax.plot(xE, yE, 'o-', markersize=markersize, c=ce, linewidth=1)
    ax.axhline(y=0, c='k', linewidth=1, linestyle='--') # horizontal line

    #if H.fetchExists(params, 'freq'):
    #    ax.set_xticks(ax.get_xticks()[::params['freq']])           
    #    ax.set_xticklabels(ax.get_xticks())
    if H.fetchExists(params, 'showTitle'):
        ax.set_title(axOrig.get_title())
    if H.fetchExists(params, 'showXlabel'):
        ax.set_xlabel(params['xlabel'], fontsize=8)    

    #plot_fillArea(ax)   
    ax.xaxis.grid()
    ax.yaxis.grid()
#endregion

#region: adjust figs

def adjust_limits(fig, axes, params):
    minX, maxX = H.fetchExists_list(params, ['minX', 'maxX'])
    minY, maxY = H.fetchExists_list(params, ['minY', 'maxY'])
    PH.set_axLim(fig, axes=axes, minX=minX, maxX=maxX, minY=minY, maxY=maxY)    
    

def adjust_labels(fig, params):
    axes = fig.get_axes()
    xlabels, ylabels, titles = H.fetchExists_list(params, ['xlabels', 'ylabels', 'titles'])    
    xlabels, ylabels, ylabelpos = H.fetchExists_list(params, ['xlabels', 'ylabels', 'ylabelpos'])   

    for index in range(len(axes)):
        ax = axes[index]
        if titles is not None:
            ax.set_title(titles[index], fontsize=8)

        if xlabels is not None:
            ax.set_xlabel(xlabels[index], fontsize=8)
        
        if ylabels is not None:
            if ylabelpos is None: ylabelpos = 'right'
            ax.set_ylabel(ylabels[index], fontsize=8)            
            ax.yaxis.set_label_position(ylabelpos)

def adjust_suplabels(fig, params):
    xsuplabel, ysuplabel = H.fetchExists_list(params, ['xsuplabel', 'ysuplabel']) 
    xsuppad, ysuppad = H.fetchExists_list(params, ['xsuppad', 'ysuppad']) 
    if xsuppad is None: xsuppad = 0.2
    if ysuppad is None: ysuppad = 0.2      

    # For the distance between legend and titles 
    if xsuplabel is not None:
        fig.text(0.5, xsuppad, xsuplabel, va='center', ha='center')
    if ysuplabel is not None:        
        fig.text(ysuppad, 0.5, ysuplabel, va='center', ha='center', rotation=90)

    left, right, top, bot       = H.fetchExists_list(params, ['left', 'right', 'top', 'bottom']) 
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bot)   
        

def adjust_ticks(fig, params):
    axes = fig.get_axes()
    showXTicks, showYTicks, xticks = H.fetchExists_list(params, ['showXTicks', 'showYTicks', 'xticks'])

    for index in range(len(axes)):
        ax = axes[index]
        if xticks is not None:
            ax.xaxis.set_major_locator(ticker.FixedLocator(xticks))            

        if showXTicks is not None:
            if index+1 not in showXTicks:
                ax.set_xticklabels([])            
        
        if showYTicks is not None:
            if index+1 not in showYTicks:
                ax.set_yticklabels([])

def adjust_figs(fig, axes, params):
    adjust_suplabels(fig, params)
    adjust_limits(fig, axes, params)
    adjust_ticks(fig, params)
    adjust_labels(fig, params)
    

#endregion

#region: Main Delta plots Implementation
def delta(fig, gs, params):
    nPlots = 1 # 2 if adding best as well

    axesOrig = fig.get_axes()
    newFig, ncols = H.fetchExists_list(params, ['newFig', 'ncols'])

    ylabBest, ylabAvg = r'$\delta$ Best', r'$\delta$ Average'    
    axes = [fig.add_subplot(gs[ncols + index]) for index in range(ncols*nPlots)]

    # For each one of the axes/subfig, plot its delta
    for index in range(ncols):
        axOrig = axesOrig[index]
        axAvg = axes[index]
        #axBest  = axes[ncols+index]
        
        bestR, bestE, avgR, avgE = delta_axes(axOrig, params, index)                
        #plot_diff(axOrig, axBest, bestR, bestE, ylabBest, params)
        plot_diff(axOrig, axAvg,  avgR,  avgE, ylabAvg, params)   

    adjust_figs(fig, axes, params)    
    fpath, fname = H.fetchExists_list(params, ['fpath', 'fname'])
    PH.savefig(fig, fpath, fname, fname)

    return fig
#endregion
