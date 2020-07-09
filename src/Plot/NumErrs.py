import seaborn as sns
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.colors

from src.Plot import Hazard, PlotHelper as PH

#region: Pre-set Ops
def get_dfLabs(df_occur):
    df_labs = df_occur[df_occur['event'] == 'labs']
    df_labs.is_copy = False

    def remove_success(tool):
        t = tool.lower()
        if 'repair' in t or 'example' in t: return tool.split()[1] # remove True/False
        return tool

    df_labs['tool'] = [remove_success(t) for t in df_labs['tool']]
    return df_labs

def get_dfLabTool(df_numErr, lab, tool):
    df_labTool = df_numErr[(df_numErr.labs == lab) & (df_numErr.tool == tool)]
    return df_labTool

def get_labsTools(df_numErr):
    labs  = sorted(df_numErr['labs'].unique())
    tools = sorted(df_numErr['tool'].unique())[::-1]

    return labs, tools

def get_dfFail(df_fail):
    df_group = df_fail.groupby(['tool', 'labs', 'assignment_id'])
    df_numErr = df_group.size().reset_index(name='num_errors')

    return df_numErr

def get_dfPass(df_pass, df_fail):
    '''Add all unique assignment (not having single compilation failure) as num_error=0 '''       
        # Get the failing assignments
    assignFail      = df_fail['assignment_id'].unique()
        # Pick the first successful compilation assignment-id "row"
    df_passFirst    = df_pass.groupby(['assignment_id']).first() 
        # Fetch assign having only success - by filtering out assign which exists in failure 
    df_passOnly     = df_passFirst[~df_passFirst.index.isin(assignFail)]
        
        # Filter out only the required columns, and set the number of errors to be zero
    df_group    = df_passOnly.groupby(['tool', 'labs', 'assignment_id'])
    df_numErr   = df_group.size().reset_index(name='num_errors') 
    df_numErr['num_errors'] = 0
    
    return df_numErr

def get_dfNumErr(df_occur):
    print('Creating NumErr dataFrame ...')

    df_labs = get_dfLabs(df_occur)
    df_pass = df_labs[df_labs['compiled'] == 1]
    df_fail = df_labs[df_labs['compiled'] == 0]

    df_numErr_f = get_dfFail(df_fail)
    df_numErr_p = get_dfPass(df_pass, df_fail)

    df_numErr = df_numErr_f.append(df_numErr_p, ignore_index=True)
    return df_numErr

def get_dfSem(df_numErr):
    print('\nSemester merging')
    def check_sem8(tool):
        tool = tool.lower()
        return 'repair' in tool or 'example' in tool

    df_numErr['tool'] = ['2017-2018-II' if check_sem8(t) else t for t in df_numErr['tool']]
    return df_numErr

#endregion

#region: Plotting Ops
def set_axLim(axes):
    xmax = 12 # hard-coded
    ymax = max([ax.get_ylim()[1] for ax in axes])
    ymax = 600 # hard-code

    for ax in axes:    
        ax.set_xlim([-1, xmax])
        ax.set_ylim([0, ymax])
    
  
def plot_snsCount(df_plot, ax, tool, indexT, indexS):
    if len(df_plot) > 0:
        x = df_plot['num_errors']
        mean = x.mean()
        k = np.arange(x.max() + 1)
        color, indexT, indexS = PH.get_color(tool, indexT, indexS)

        sns.countplot(x, order=k, color=color)

    return indexT, indexS

def set_rowLabel(fig, labs):
    # Add a "row" label (common label for entire row)
    axes = [ax for ax in fig.get_axes() if ax.is_first_col()]
    for ax, lab in zip(axes, labs):
        ax.annotate(lab, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - 5, 0),
                xycoords=ax.yaxis.label, textcoords='offset points',
                size='large', ha='right', va='center')

def setLim_save(fig, fname):
    # Adjust the fig    
    title = '\'Count\' of student assignments/submissions, having exactly \'num_errors\' #compilation-errors (ignore success)'  

    # Save and close the fig
    PH.savefig(fig, CF.path_numErrs, fname, title)
    

#endregion

#region: Main Plotting Function - freq VS num_errors
def plot_count(df_numErr, fname):
    print('Plotting numErrs absolute ...')
    labs, tools = get_labsTools(df_numErr)
    indexPlot = 1
    fig = plt.figure(figsize=(25,30))
    
    for lab in labs:        
        indexT, indexS = 0, 0 # Index Tool, and Index Sem
        axes = []

        for tool in tools:
            ax = fig.add_subplot(len(labs), len(tools), indexPlot)
            df_plot = get_dfLabTool(df_numErr, lab, tool)
            
            indexT, indexS = plot_snsCount(df_plot, ax, tool, indexT, indexS)
            ax.set_title(str(tool) +' #'+ str(len(df_plot)))

            axes.append(ax)
            indexPlot += 1   
        
        set_axLim(axes)

    set_rowLabel(fig, labs)
    setLim_save(fig, fname)

def plot_perc(df_numErr_sem, fname):
    print('\nPlotting numErrs percentage ...')
    df_percErr = (df_numErr_sem.groupby(['labs', 'tool']))['num_errors'].value_counts(
            normalize=True).rename('percentage').mul(100).reset_index().sort_values(['tool', 'labs'], ascending=[False, True])

    labs, tools = get_labsTools(df_percErr)
    axes = []
    indexPlot = 1

    fig = plt.figure(figsize=(25,35))
    plt.rcParams.update({'font.size': 18})

    for lab in labs:
        ax = fig.add_subplot(len(labs), 1, indexPlot)
        df_plot = df_percErr[(df_percErr.labs == lab)]
        sns.factorplot(data=df_plot, ax=ax, kind="bar", x="num_errors", y="percentage",
            hue="tool", palette=PH.get_palette(df_plot['tool'].unique()))
        
        ax.set_title(str(lab))
        ax.set_xlim([-1, 12]); ax.set_ylim([0, 100]); 
        indexPlot += 1
    
    setLim_save(fig, fname)

def plot(df_occur):
    df_numErr = get_dfNumErr(df_occur)
    plot_count(df_numErr, 'tool-split')

    df_numErr_sem = get_dfSem(df_numErr)
    plot_count(df_numErr_sem, 'semester-split')

    plot_perc(df_numErr_sem, 'percentage')
