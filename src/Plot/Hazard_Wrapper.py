from src.Plot import Hazard

#region: Manipulate DFs
def getDF_labs(df):
    df_labs = df[df['event']=='labs'] 
    return df_labs

def getDF_errSet(df_labs):
    sorted_errSet = df_labs.groupby('errSet').count().sort_values('code_id', 0) # Sorting on any works, since count inc all
    top9 = sorted_errSet.iloc[-9:]
    df_err9 = df_labs[df_labs['errSet'].isin(top9.index)]

    return df_err9

def getDF_filterErrs(df_labs, errSets):    
    df_errs = df_labs[df_labs['errSet'].isin(errSets)]

    return df_errs

def getDF_assignment(df):
    df_as = df.groupby('assignment_id').count().sort_values('code_id', 0)
    df_as['event'] = df[df['assignment_id'] == '17-18-II41689']['event_name'].unique()[0]

    return df_as

def getDF_dict(df, errSets=[]):
    dfs = {}

    dfs['all'] = df[(df['event']=='labs') | ((df['event']=='exam'))] 
    dfs['labs_1-6'] = getDF_labs(dfs['all'])
    dfs['top9-errs labs_1-6'] = getDF_errSet(dfs['labs_1-6'])
    dfs['chosen-errs labs_1-6'] = getDF_filterErrs(dfs['labs_1-6'], errSets)
    
    return dfs

    #endregion


#region: Indiv plots
def plot_indiv(dfs, key, Tname, groupBy, splitBy, params):
    print('key={}, TName={}, groupBy={}, splitBy={}'.format(key, Tname, groupBy, splitBy))
    #params['fpath'] = params['fpath'] + Tname + '/'
    title = key

    params['title'] = title
    return Hazard.plot_survival(dfs[key], Tname, groupBy=groupBy, splitBy=splitBy, params=params)
    #Hazard.plot_hazard  (dfs[key], Tname, groupBy=groupBy, splitBy=splitBy, title=title, 
    #                        xlim=xlim, ylim=ylim, fpath=fpath)
#endregion

#region: Main plot
def plot_all(df, path_hazard):
    print('Plotting ...')

    dfs = getDF_dict(df)
    
    for maxX in [10]:
        params = {'xlim':maxX, 'fpath':path_hazard}
        plot_indiv(dfs, key='all',  Tname='numAttempt', groupBy='tool', splitBy='event', params=params)
        plot_indiv(dfs, key='labs_1-6', Tname='numAttempt', groupBy='tool', splitBy='labs',  params=params)
        plot_indiv(dfs, key='top9-errs labs_1-6', Tname='numAttempt', groupBy='tool', splitBy='errSet', params=params)

    for maxX in [300]:
        params = {'xlim':maxX, 'fpath':path_hazard}
        plot_indiv(dfs, key='all', Tname='timeTaken (sec)',  groupBy='tool', splitBy='event', params=params)
        plot_indiv(dfs, key='labs_1-6', Tname='timeTaken (sec)', groupBy='tool', splitBy='labs',  params=params)
        plot_indiv(dfs, key='top9-errs labs_1-6', Tname='timeTaken (sec)', groupBy='tool', splitBy='errSet',   params=params)
        
    #endregion