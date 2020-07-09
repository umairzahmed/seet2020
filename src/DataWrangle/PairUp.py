import pandas as pd

#region: --- Collate Data ---

def pairUp_code(df, srcIndex, trgtIndex, numAttempt):
    dateTimeDiff = df.get_value(trgtIndex, 'compile_time') - df.get_value(srcIndex, 'compile_time')    
    timeTaken = dateTimeDiff.total_seconds()

    # Count the fix only if its time taken is <= maxTime allowed
    df.set_value(srcIndex, 'trgtRow', trgtIndex)
    df.set_value(srcIndex, 'numAttempt', numAttempt)
    df.set_value(srcIndex, 'timeTaken (sec)', timeTaken)

def pairUp(df):
    '''For each student, for each assignment:
Find the "source-target" pair: A compilation error code -> compiled code'''
    print('Pairing Src-Trgt ...')
    totalCount, currCount, perc = len(df['assignment_id'].unique()), 0, 0

    for aid in df['assignment_id'].unique():
        if float(currCount)/totalCount * 100 >= perc:
            perc = perc + 10
            print('\t{} / {} done'.format(currCount, totalCount))

        codes = df[df['assignment_id'] == aid]
        srcIndex, numAttempt = None, 0
        currCount += 1
        
        for index in codes.index:
            row = df.loc[index]
            
            # Start measure from the first errorneous code
            if row['compiled'] == 0 and srcIndex is None: 
                srcIndex, numAttempt = index, 1

            # Student got an error earlier, and is still trying to debug
            elif row['compiled'] == 0 and srcIndex is not None:
                numAttempt += 1

            # If there was an earlier error code, note the timeDiff
            elif row['compiled'] == 1 and srcIndex is not None: 
                pairUp_code(df, srcIndex, index, numAttempt)        
                srcIndex, numAttempt = None, 0      

    # Return a new DataFrame containing only those source having a target (0 -> 1 compilation transition)
    return df[~df['trgtRow'].isnull()] 
                    
#endregion
