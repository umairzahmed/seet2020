import os
import matplotlib.pyplot as plt, matplotlib.colors
import pylab

def plot_params(font_size=10):
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': font_size})
    plt.rc('xtick', labelsize='x-small')
    plt.rc('ytick', labelsize='x-small')

def get_color(uniqGroup, indexT, indexS):
    colors = matplotlib.cm.get_cmap('tab10').colors # Blue, Orange, Green, Purple, ...

    blueD, blueL        = colors[0], colors[9]
    orange, green, red  = colors[1], colors[2], colors[3]
    purple, brown, pink = colors[4], colors[5], colors[6]
    grey, yellow        = colors[7], colors[8]
    
    sems = (blueD, purple, pink, blueL)

    if      uniqGroup.lower() == 'true repair':     return orange,  indexT+1, indexS
    elif    uniqGroup.lower() == 'true example':    return green,   indexT+1, indexS
    elif    uniqGroup.lower() == 'false repair':    return red,     indexT+1, indexS
    elif    uniqGroup.lower() == 'false example':   return brown,   indexT+1, indexS
    elif    'repair' in uniqGroup.lower():          return orange,  indexT+1, indexS
    elif    'example' in uniqGroup.lower():         return green,   indexT+1, indexS

    elif    uniqGroup.upper() == '2017-2018-II':    return yellow,    indexT, indexS+1
    elif    uniqGroup.upper() == '2017-2018-I':     return blueD,   indexT, indexS+1
    elif    uniqGroup.upper() == '17-18-II':        return brown,   indexT, indexS+1
    elif    uniqGroup.upper() == '17-18-I':         return blueD,   indexT, indexS+1
    elif    uniqGroup.upper() == '2016-2017-II':    return purple,  indexT, indexS+1
    elif    uniqGroup.upper() == '16-17-II':        return purple,  indexT, indexS+1

    elif    uniqGroup.lower() == 'feedback-tools':  return red,    indexT, indexS+1
    elif    uniqGroup.lower() == 'previous-sem':    return blueD,    indexT, indexS+1
    #elif    re.match('^\d', uniqGroup): # If the group name begins with number (then other sem data)
    else:   return sems[indexS], indexT, indexS+1

def get_palette(groups):
    indexT, indexS = 0, 0
    colors = []
    for group in groups:
        color, indexT, indexS = get_color(group, indexT, indexS)
        colors.append(color)
        
    return colors

def get_size(df, splitBy):
    splits = df[splitBy].unique()
    if len(splits) <= 1:
        return 1, 1
    elif len(splits) <= 2:
        return 1, 2
    elif len(splits) <= 4:
        return 2, 2
    elif len(splits) <= 6:
        return 2, 3
    else:
        return 3, 3

    
def savefig(fig, fpath, fname, title):
    #fig.suptitle(title)

    if fpath != None:
        if not os.path.exists(fpath):
            os.makedirs(fpath)

        # Replace - with _ for latex fnames
        fpathname = (fpath + fname +'.pdf').replace('-', '_')
        fig.savefig(fpathname, dpi=300, format='pdf')

def set_legend(fig, ncol, axesNum=0):
    '''Sets a common legend for multiple axes'''
    axes = fig.get_axes()

    # Add legend only to the first plot, and place at top (with ncol number of columns)
    handles, labels = axes[axesNum].get_legend_handles_labels()

    # Remove legend from other axes
    for index in range(len(axes)):
        if axes[index].legend(): # If axes has a legend to remove
            axes[index].legend().remove() 

    # Plant it at top, spread across multiple columns
    legend = fig.legend(handles, labels, loc='upper center', ncol=ncol+1, mode="expand", prop={'size': 'x-small'})
    

def ifNoneElse(val1, val2):
    '''If val1 is None, return val2, else val1'''
    if val1 == None: return val2
    return val1

def set_axLim(fig, minX=None, minY=None, maxX=None, maxY=None, axes=None):
    xLow, yLow = float('inf'), float('inf')
    xHigh, yHigh = float('-inf'), float('-inf')
    
    if axes is None: axes = fig.get_axes()
    for ax in axes:
        xl, xh = ax.get_xlim()
        yl, yh = ax.get_ylim()

        xLow = min(xLow, xl)
        yLow = min(yLow, yl)
        xHigh = max(xHigh, xh)
        yHigh = max(yHigh, yh)

    xLow = ifNoneElse(minX, xLow)
    yLow = ifNoneElse(minY, yLow)
    xHigh = ifNoneElse(maxX, xHigh)
    yHigh = ifNoneElse(maxY, yHigh)

    for ax in axes:
        ax.set_xlim([xLow, xHigh])
        ax.set_ylim([yLow, yHigh])

def suplabel(fig, axisName, label, label_prop=None,
             labelpad=5,
             ha='center',va='center'):
    ''' Add super ylabel or xlabel to the figure
    Similar to matplotlib.suptitle
    axisName       - string: "x" or "y"
    label      - string
    label_prop - keyword dictionary for Text
    labelpad   - padding from the axis (default: 5)
    ha         - horizontal alignment (default: "center")
    va         - vertical alignment (default: "center")
    '''
    #fig = pylab.gcf()
    if labelpad == None: labelpad=5
    xmin = []
    ymin = []
    for ax in fig.axes:
        xmin.append(ax.get_position().xmin)
        ymin.append(ax.get_position().ymin)
    xmin,ymin = min(xmin),min(ymin)
    dpi = fig.dpi
    if axisName.lower() == "y":
        rotation=90.
        x = xmin-float(labelpad)/dpi
        y = 0.5
    elif axisName.lower() == 'x':
        rotation = 0.
        x = 0.5
        y = ymin - float(labelpad)/dpi
    else:
        raise Exception("Unexpected axis: x or y")
    if label_prop is None: 
        label_prop = dict()
    pylab.text(x,y,label,rotation=rotation,
               transform=fig.transFigure,
               ha=ha,va=va,
               **label_prop)
