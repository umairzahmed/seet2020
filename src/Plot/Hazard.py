from lifelines import KaplanMeierFitter, NelsonAalenFitter
from lifelines.datasets import load_waltons

import os, re
from collections import Counter

import matplotlib.pyplot as plt, matplotlib.colors
from src.BaseClasses import Helper as H
from src.Plot import PlotHelper as PH


#region: Survival/Hazard Wrapper
def get_TE(df, TName='T', EName='E'):
    if EName == None: return df[TName], None
    return df[TName], df[EName]

def plot_survival(df, TName, EName=None, groupBy=None, splitBy=None, params={}):
    print('\tSurvival')
    ylabel, kmf = 'Survival_Probability', KaplanMeierFitter()
    params['ylabel'] = ylabel
    return plot_any(df, fitter=kmf, TName=TName, EName=EName, 
                groupBy=groupBy, splitBy=splitBy, params=params)

def plot_hazard(df, TName, EName=None, groupBy=None, splitBy=None, params={}):
    print('\tHazard')
    ylabel, naf = 'Hazard_Rate', NelsonAalenFitter()
    params['ylabel'] = ylabel
    return plot_any(df, fitter=naf, TName=TName, EName=EName, groupBy=groupBy, splitBy=splitBy, params=params)

def plot_any(df, fitter, TName, EName=None, groupBy=None, splitBy=None, params={}):
    params['xlabel'] = TName
    params['title'] = '{} on={} lim={} across={}'.format(
            params['ylabel'].split('_')[0], params['title'], params['xlim'], splitBy)

    if groupBy == None or splitBy == None:  
        return plotOverall(df, fitter, TName, EName, params)
    else:
        return plotGroup(df, fitter, TName, EName, groupBy, splitBy, params)

    #endregion

#region: Plots Helper
def get_groups(df, TName, EName, splitBy, groupBy, uniqSplit):
    if uniqSplit is None:
        df_curr = df[df[splitBy].isnull()]
    else:
        df_curr = df[df[splitBy] == uniqSplit]

    T, E = get_TE(df_curr, TName, EName)
    groups = df_curr[groupBy]

    return T, E, groups

def get_pltLimits(ax, maxX, maxY, xlim, ylim):
    if xlim == None: # If set by user, use it. Else define it
        maxX = max(maxX, ax.get_xlim()[1])
    else:
        maxX = xlim
    
    if ylim == None:
        maxY = max(maxY, ax.get_ylim()[1])
    else:
        maxY = ylim
    
    return maxX, maxY


def set_fit(fitter, T, E, groups, uniqGroup):
    ix = (groups == uniqGroup)   

    if E != None: 
        fitter.fit(T[ix], E[ix], label=uniqGroup, c='')
    else:
        fitter.fit(T[ix], label=uniqGroup)

    newKMF = KaplanMeierFitter()
    newKMF.fit(T[ix], label=uniqGroup)
    #display(newKMF)
    return newKMF

def set_pltLimits(fig, maxX, maxY, title):
    for ax in fig.get_axes():
        ax.set_xlim([0, maxX])
        ax.set_ylim([0, maxY])
        

    return title

def set_axAttr(ax, subtitle, xlabel, ylabel):
    ax.grid(which='major')    
    ax.set_title(subtitle, fontsize=8)

    #if indexPlot != 1: # Set labels only for 1st axis
    #    xlabel, ylabel = '', ''
        #ax.get_yaxis().set_ticks([])

    ax.set_xlabel('')
    ax.set_ylabel('')  


    #endregion

#region: Plots Implementation

def plotOverall(df, fitter, TName, EName, title=None, xlabel=None, ylabel=None, 
                xlim=None, ylim=None, fpath=None, height=None):
    T, E = get_TE(df, TName, EName)
    fitter.fit(T, E)

    ax = fitter.plot()
    set_axAttr(ax, title, xlabel, ylabel) 
    return ax

def plotGroup(df, fitter, TName, EName=None, groupBy=None, splitBy=None, params={}):
    xlim, ylim, title = H.fetchExists_list(params, ['xlim', 'ylim', 'title'])
    fpath, fname, xlabel, ylabel = H.fetchExists_list(params, ['fpath', 'fname', 'xlabel', 'ylabel'])
    height, width = H.fetchExists_list(params, ['height', 'width'])
    top, left, bot = H.fetchExists_list(params, ['top', 'left', 'bot'])
    xlabelpad, ylabelpad = H.fetchExists_list(params, ['xlabelpad', 'ylabelpad'])
    wspace, hspace, revSortSplit = H.fetchExists_list(params, ['wspace', 'hspace', 'revSortSplit'])
    splitKeys, replaceSplit = H.fetchExists_list(params, ['splitKeys', 'replaceSplit'])

    nrows, ncols, height_ratios = H.fetchExists_list(params, ['nrows', 'ncols', 'height_ratios'])    
    indexp, maxX, maxY = 0, 0, 0
    fig = plt.figure(figsize=(width, height))
    gs = plt.GridSpec(nrows, ncols, height_ratios=height_ratios, wspace=wspace, hspace=hspace)

    newKMFs = []
    if revSortSplit is None: revSortSplit = False
    if splitKeys is None: splitKeys = sorted(df[splitBy].unique(), reverse=revSortSplit)
    print('\t\t{}'.format(splitKeys))

    for indexSplit in range(len(splitKeys)): 
        uniqSplit = splitKeys[indexSplit]

        fitter = KaplanMeierFitter() # Init a new KMF for each new split/axes
        T, E, groups = get_groups(df, TName, EName, splitBy, groupBy, uniqSplit)
        ax = fig.add_subplot(gs[indexp])
        indexp += 1
        
        uniqGroups = sorted(groups.unique(), reverse=True) # Reverse sort, so that the "example" and "repair" group are always top

        indexT, indexS = 0, 0 # Index Tool, and Index Sem
        for index in range(len(uniqGroups)): # Sort so that colour coding (of labels) remains same
            uniqGroup = uniqGroups[index]
            newKMF = set_fit(fitter, T, E, groups, uniqGroup)
            newKMFs.append(newKMF) # Return these independent kmfs for Delta plots
            
            c, indexT, indexS = PH.get_color(uniqGroup, indexT, indexS)
            newKMF.plot(ax=ax, color=c, linewidth=1, ci_show=False) 

        axTitle = uniqSplit
        if replaceSplit is not None: axTitle = replaceSplit[indexSplit]
        set_axAttr(ax, axTitle, xlabel, ylabel)
        maxX, maxY = get_pltLimits(ax, maxX, maxY, xlim, ylim)
    
    title = set_pltLimits(fig, maxX, maxY, title)
    
    fig.tight_layout()  
    
    #PH.suplabel(fig, 'x', xlabel, labelpad=xlabelpad)
    #PH.suplabel(fig, 'y', ylabel, labelpad=ylabelpad)

    PH.set_legend(fig, ncol=len(df[groupBy].unique()))
        
    fig.subplots_adjust(left=left, top=top, bottom=bot)    # For the distance between legend and titles
    PH.savefig(fig, fpath, fname, title)
          
    return fig, gs, newKMFs
    #endregion
   
