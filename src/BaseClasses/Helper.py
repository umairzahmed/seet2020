import csv

def readCSV(fname):
    f = open(fname, 'rU')
    freader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    lines = list(freader)
    f.close()
    headers = [i.strip() for i in lines[0]]

    return headers, lines[1:]

def writeCSV(fname, headers, lines):    
    fwriter = csv.writer(open(fname, 'w'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)    
    fwriter.writerow(headers)
    fwriter.writerows(lines)

def fetchExists(dicti, key):
    if key in dicti:
        return dicti[key]
    return None

def fetchExists_list(dicti, listK):
    return [fetchExists(dicti, k) for k in listK]


def joinList(li, joinStr='\n', func=str):
    return joinStr.join([func(i) for i in li]) 

def joinLL(lists, joinStrWord=' ', joinStrLine='\n', func=str):
    listStrs = [joinList(li, joinStrWord, func) for li in lists]
    return joinList(listStrs, joinStrLine, func) 


def stringifyL(li):
    return [str(token) for token in li]

def stringifyLL(lists):
    return [stringifyL(li) for li in lists]

    
def div(a, b):
    '''Return a/b (float div). Returns None if denominator is 0'''    
    if a == None: return None
    if b == 0: return None
    return float(a) / b

