import pandas as pd
from pathlib import Path
from pp.log import logger

from inspect import signature
#from types import MappingProxyType
from collections import OrderedDict

#SERVICES DIRECTORY 
SERVICES = {}

#SERVICE KEYS
# type, number of selections possible
OPTION_FIELD_SINGLE_COL_ANY = (None, 1)
OPTION_FIELD_MULTI_COL_ANY = (None, None)
OPTION_FIELD_SINGLE_COL_NUMBER = ('number', 1)
OPTION_FIELD_MULTI_COL_NUMBER = ('number', None)
OPTION_FIELD_SINGLE_COL_STRING = ('object', 1)
OPTION_FIELD_MULTI_COL_STRING = ('object', None)
OPTION_FIELD_SINGLE_BOOLEAN = ('boolean', 1)
OPTION_FIELD_SINGLE_COLORSWATCH = ('colorswatch', 1)
OPTION_FIELDS = []
OPTION_FIELDS.extend([
    OPTION_FIELD_SINGLE_COL_ANY,
    OPTION_FIELD_MULTI_COL_ANY,
    OPTION_FIELD_SINGLE_COL_NUMBER,
    OPTION_FIELD_MULTI_COL_NUMBER,
    OPTION_FIELD_SINGLE_COL_STRING,
    OPTION_FIELD_MULTI_COL_STRING,
    OPTION_FIELD_SINGLE_BOOLEAN,
    OPTION_FIELD_SINGLE_COLORSWATCH,
])
FIELD_STRING = 'string'
FIELD_INTEGER = 'int'
FIELD_NUMBER = 'number'
FIELD_FLOAT = 'float'

class Service(object):
    def __init__(self, fn, d):
        self.name = fn.__name__
        self.fn = fn
        self._d = d

    def options(self, df):
        #TODO: orderedDict 
        return {k: (colHelper(df, type=v[0], colsOnNone=True) if v in OPTION_FIELDS else None) for k, v in self._d.items()}

def registerService(**d):
    def inner(fn):
        def service_group(service_name):
            gr = extractGroup(service_name)
            if gr not in SERVICES.keys():
                SERVICES[gr] = {}
            return SERVICES[gr]
        service_group(fn.__name__)[fn.__name__] = Service(fn, d)
        logger.debug('pp.util > registerService: Registered Service: {}'.format(fn.__name__))
        return fn
    return inner

# ## UTILITIES ###
def service_helper(groups=None, return_type='group_service_callable'):
    if isinstance(groups, str):
        groups = [groups]
    elif isinstance(groups, list):
        groups = groups
    else:
        groups = None
    if groups is None:
        filtered_services = SERVICES
    else:
        filtered_services = {g: SERVICES[g] for g in groups if g in SERVICES.keys()}
        
    if return_type=='group_service_callable':
        return filtered_services
    elif return_type=='group_service_names':
        return {k: list(v.keys()) for k, v in filtered_services.items()}
    elif return_type=='service_callable':
        return {k: v for dic in filtered_services.values() for k, v in dic.items()}
    return "SERVICE NOT FOUND"

        
def extractGroup(service):
    if not isinstance(service, str):
        return None
    return service.split('_', 1)[0].lower()

def removeElementsFromList(l1, l2):
    '''Remove from list1 any elements also in list2'''
    # if not list type ie string then covert
    if not isinstance(l1, list):
        list1 = []
        list1.append(l1)
        l1 = list1
    if not isinstance(l2, list):
        list2 = []
        list2.append(l2)
        l2 = list2
    return [i for i in l1 if i not in l2]

def commonElementsInList(l1, l2):
    if l1 is None or l2 is None: return None
    if not isinstance(l1, list): l1 = [l1]
    if not isinstance(l2, list): l2 = [l2]
    return [i for i in l1 if i in l2]

def colHelper(df, columns=None, max=None, type=None, colsOnNone=True, forceReturnAsList=True):

    if isinstance(columns, tuple):
        columns = list(columns)

    # pre-process: translate to column names
    if isinstance(columns, slice) or isinstance(columns, int):
        columns = df.columns.values.tolist()[columns]
    elif isinstance(columns, list) and all(isinstance(c, int) for c in columns):
        columns = df.columns[columns].values.tolist()

    # process: limit possible columns by type (number, object, datetime)
    df1 = df.select_dtypes(include=type) if type is not None else df

    #process: fit to limited column scope
    if colsOnNone == True and columns is None: columns = df1.columns.values.tolist()
    elif columns is None: return None
    else: columns = commonElementsInList(columns, df1.columns.values.tolist())           

    # apply 'max' check    
    if isinstance(columns, list) and max != None:
        if max == 1: columns = columns[0]
        else: columns = columns[:max]

    # if string format to list for return
    if forceReturnAsList and not isinstance(columns, list): 
        columns = [columns]

    return columns

def colValues(df, col):
    cv = df[col].unique()
    return cv

def toMultiIndex(df):
    if isinstance(df.columns, pd.MultiIndex): 
        arrays = [range(0, len(df.columns)), df.columns.get_level_values(0), df.dtypes]
        mi = pd.MultiIndex.from_arrays(arrays, names=('Num', 'Name', 'Type'))
    else:
        arrays = [range(0, len(df.columns)), df.columns, df.dtypes]
        mi = pd.MultiIndex.from_arrays(arrays, names=('Num', 'Name', 'Type'))
    df.columns = mi
    return df

def toSingleIndex(df):
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = df.columns.get_level_values(1)
    return df

def rowHelper(df, max = None, head = True):
    if max is None: return df
    else: 
        if head is True: return df.head(max)
        else: return df.tail(max)

def toUniqueColName(df, name):
    n = 1
    name = str(name)
    while name in df.columns.values.tolist():
        name = name + '_' + str(n)
    return name

def pathHelper(path, filename):
    import os
    if path == None:
        home = str(pathlib.Path.home())
        path = os.path.join(home, 'report')
    else:
        path = os.path.join(path, 'report')
    os.makedirs(path, exist_ok = True)
    path = os.path.join(path, filename)
    return path
