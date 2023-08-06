from pp.log import logger
from pp.util import *

#non-standard libraries
import pandas as pd
    
def _DATA_COL_ADD_CUSTOM(df, columns=None, eval_string='""', name='new_column'):
    '''Add a single new column with custom (lambda) content'''
    columns = colHelper(df, columns)
    name = toUniqueColName(df, name)
    df[name] = df[columns].apply(lambda row: eval(eval_string), axis=1, result_type='expand')
    logger.debug('pp.data > Added column: {}'.format(name))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    separator=FIELD_STRING,
    name=FIELD_STRING,
)
def DATA_COL_ADD_CONCATENATE(df, columns=None, separator='_', name='new_column'):
    '''Add a single new column with a 'fixed' value as content'''
    eval_string = '"{}".join(map(str, row.tolist()))'.format(separator)
    df = _DATA_COL_ADD_CUSTOM(df=df, columns=columns, eval_string=eval_string, name=name)
    return df

@registerService(
    column=OPTION_FIELD_SINGLE_COL_ANY,
    name=FIELD_STRING,
)
def DATA_COL_ADD_DUPLICATE(df, column=None, name='new_column'):
    '''Add a single new column by copying an existing column'''
    column = colHelper(df, column, max=1, forceReturnAsList=False)
    eval_string = 'row.{}'.format(column)
    df = _DATA_COL_ADD_CUSTOM(df=df, eval_string=eval_string, name=name)
    return df

@registerService(
    column=OPTION_FIELD_SINGLE_COL_ANY,
    pos=FIELD_INTEGER,
    name=FIELD_STRING,
)
def DATA_COL_ADD_EXTRACT_BEFORE(df, column=None, pos=None, name='new_column'):
    '''Add a single new column with text extracted from before char pos in existing column'''
    column = colHelper(df, column, max=1, forceReturnAsList=False)
    eval_string = 'str(row.{})[:{}]'.format(column, pos)
    df =  _DATA_COL_ADD_CUSTOM(df=df, eval_string=eval_string, name=name)
    return df

@registerService(
    column=OPTION_FIELD_SINGLE_COL_ANY,
    chars=FIELD_INTEGER,
    name=FIELD_STRING,
)
def DATA_COL_ADD_EXTRACT_FIRST(df, column=None, chars=None, name='new_column'):
    '''Add a single new column with first N chars extracted from column'''
    column = colHelper(df, column, max=1, forceReturnAsList=False)
    eval_string = 'str(row.{})[:{}]'.format(column, chars)
    df = _DATA_COL_ADD_CUSTOM(df=df, eval_string=eval_string, name=name)
    return df

@registerService(
    column=OPTION_FIELD_SINGLE_COL_ANY,
    pos=FIELD_INTEGER,
    name=FIELD_STRING,
)
def DATA_COL_ADD_EXTRACT_FROM(df, column=None, pos=None, name='new_column'):
    '''Add a single new column of text extracted from after char pos in existing column'''
    column = colHelper(df, column, max=1, forceReturnAsList=False)
    eval_string = 'str(row.{})[{}:]'.format(column, pos)
    df = _DATA_COL_ADD_CUSTOM(df=df, eval_string=eval_string, name=name)
    return df

@registerService(
    column=OPTION_FIELD_SINGLE_COL_ANY,
    pos=FIELD_INTEGER,
    name=FIELD_STRING,
)
def DATA_COL_ADD_EXTRACT_LAST(df, column=None, chars=None, name='new_column'):
    '''Add a single new column with last N chars extracted from column'''
    column = colHelper(df, column, max=1, forceReturnAsList=False)
    eval_string = 'str(row.{})[-{}:]'.format(column, chars)
    df = _DATA_COL_ADD_CUSTOM(df=df, eval_string=eval_string, name=name)
    return df

@registerService(
    value=FIELD_STRING,
    name=FIELD_STRING,
)
def DATA_COL_ADD_FIXED(df, value=None, name='new_column'):
    '''Add a single new column with a 'fixed' value as content'''
    if isinstance(value, str): value = '"{}"'.format(value) # wrap string with extra commas!
    eval_string = '{}'.format(value)
    df = _DATA_COL_ADD_CUSTOM(df=df, eval_string=eval_string, name=name)
    return df

@registerService(
    start=FIELD_INTEGER,
    name=FIELD_STRING,
)
def DATA_COL_ADD_INDEX(df, start=1, name='new_column'):
    '''Add a single new column with a index/serial number as content'''
    name = toUniqueColName(df, name)
    df[name] = range(start, df.shape[0] + start)
    logger.debug('pp.data > Added column: {}'.format(name))
    return df

@registerService(
    name=FIELD_STRING,
)
def DATA_COL_ADD_INDEX_FROM_0(df, name='new_column'):
    '''Convenience method for DATA_COL_ADD_INDEX'''
    df = DATA_COL_ADD_INDEX(df=df, start=0, name=name)
    return df

@registerService(
    name=FIELD_STRING,
)
def DATA_COL_ADD_INDEX_FROM_1(df, name='new_column'):
    '''Convenience method for DATA_COL_ADD_INDEX'''
    df = DATA_COL_ADD_INDEX(df=df, start=1, name=name)
    return df

# Handle explicit and non-explicit dataframe

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_DELETE(df, columns=None):
    '''Delete specified column/s'''
    max = 1 if columns is None else None
    columns = colHelper(df, columns, max=max)
    df = df.drop(columns, axis = 1)
    logger.debug('pp.data > Deleted {} columns: {}'.format(len(columns), columns[:5]))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_DELETE_EXCEPT(df, columns=None):
    '''Deleted all column/s except specified'''
    max = 1 if columns is None else None
    columns = colHelper(df, columns, max=max)
    cols = removeElementsFromList(df.columns.values.tolist(), columns)
    df = DATA_COL_DELETE(df, cols)
    df = DATA_COL_REORDER_MOVE_TO_FRONT(df, columns)
    return df

@registerService(
    criteria=FIELD_STRING,
)
def DATA_COL_FILTER(df, criteria=None):
    '''Filter rows with specified filter criteria'''
    df.query(criteria, inplace = True)
    df.reset_index(drop=True, inplace=True)
    logger.debug('pp.data > Filtered columns by: {}'.format(criteria))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_FILTER_MISSING(df, columns=None):
    '''Filter rows with specified filter criteria'''
    columns = colHelper(df, columns, colsOnNone=True)
    df.dropna(inplace=True, subset=columns)
    logger.debug('pp.data > Filtered rows with missing data in these columns: {}'.format(columns))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    prefix=FIELD_STRING,
)
def DATA_COL_FORMAT_ADD_PREFIX(df, columns=None, prefix='pre_'):
    '''Format specified column/s values by adding prefix'''
    eval_string = 'str("{}") + str(cell)'.format(prefix)
    df =  _DATA_COL_FORMAT_CUSTOM(columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    suffix=FIELD_STRING,
)
def DATA_COL_FORMAT_ADD_SUFFIX(df, columns=None, suffix='_suf'):
    '''Format specified single column values by adding suffix'''
    eval_string = 'str(cell) + str("{}")'.format(suffix)
    df = _DATA_COL_FORMAT_CUSTOM(columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    eval_string=FIELD_STRING,
)
def DATA_COL_FORMAT(df, columns=None, eval_string=None):
    '''Format specified column/s values to uppercase'''
    eval_string = 'cell{}'.format(eval_string)
    df = _DATA_COL_FORMAT_CUSTOM(columns=columns, eval_string=eval_string)
    return df

def _DATA_COL_FORMAT_CUSTOM(df, columns=None, eval_string=None):
    '''Format specified column/s values to uppercase'''
    max = 1 if columns is None else None
    columns = colHelper(df, columns, max=max)
    df[columns] = pd.DataFrame(df[columns]).applymap(lambda cell: eval(eval_string))
    logger.debug('pp.data > Formatted columns: {}'.format(columns))
    return df

def _DATA_COL_FORMAT_CUSTOM_BATCH(df, columns=None, eval_string=None):
    '''Add a new column with custom (lambda) content'''
    max = 1 if columns is None else None
    columns = colHelper(df, columns, max=max)
    df[columns] = pd.DataFrame(df[columns]).apply(lambda row: eval(eval_string), axis=1)
    logger.debug('pp.data > Formatted columns: {}'.format(columns))
    return df

@registerService()
def DATA_COL_FORMAT_FILL_DOWN(df):
    '''Fill blank cells with values from last non-blank cell above'''
    eval_string = 'row.fillna(method="ffill")'.format(str(before), str(after))
    df = _DATA_COL_FORMAT_CUSTOM_BATCH(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService()
def DATA_COL_FORMAT_FILL_UP(df):
    '''Fill blank cells with values from last non-blank cell below'''
    eval_string = 'row.fillna(method="bfill")'.format(str(before), str(after))
    df = _DATA_COL_FORMAT_CUSTOM_BATCH(df=df, columns=columns, eval_string=eval_string)
    return df

# DATA_REPLACE
@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    before=FIELD_STRING,
    after=FIELD_STRING,
)
def DATA_COL_FORMAT_REPLACE(df, columns=None, before='', after=''):
    '''Round numerical column values to specified decimal'''
    eval_string = 'cell.replace("{}","{}")'.format(str(before), str(after))
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

# DATA_REPLACE
@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    after=FIELD_STRING,
)
def DATA_COL_FORMAT_REPLACE_MISSING(df, columns=None, after=''):
    '''Replace null (NaN) values to specified string'''
    eval_string = '"{}" if pd.isna(cell) else cell'.format(str(after))
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    decimals=FIELD_INTEGER,
)
def DATA_COL_FORMAT_ROUND(df, columns=None, decimals=0):
    '''Round numerical column values to specified decimal'''
    eval_string = 'round(cell,{})'.format(decimals)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    chars=FIELD_INTEGER,
)
def DATA_COL_FORMAT_STRIP(df, columns=None, chars=None):
    '''Format specified column/s values by stripping invisible characters'''
    eval_string = 'str(cell).strip()' if not chars else 'str(cell).strip("{}")'.format(chars)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    chars=FIELD_STRING,
)
def DATA_COL_FORMAT_STRIP_LEFT(df, columns=None, chars=None):
    '''Convenience method for DATA_COL_FORMAT_STRIP'''
    eval_string = 'str(cell).lstrip()' if not chars else 'str(cell).lstrip("{}")'.format(chars)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    chars=FIELD_INTEGER,
)
def DATA_COL_FORMAT_STRIP_RIGHT(df, columns=None, chars=None):
    '''Convenience method for DATA_COL_FORMAT_STRIP'''
    eval_string = 'str(cell).rstrip()' if not chars else 'str(cell).rstrip("{}")'.format(chars)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_FORMAT_TO_LOWERCASE(df, columns=None):
    '''Format specified column/s values to lowercase'''
    eval_string = 'str(cell).lower()'
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_FORMAT_TO_TITLECASE(df, columns=None):
    '''Format specified column/s values to titlecase'''
    eval_string = 'str(cell).title()'
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_FORMAT_TO_UPPERCASE(df, columns=None):
    '''Format specified column/s values to uppercase'''
    eval_string = 'str(cell).upper()'
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    typ=FIELD_STRING,
)
def DATA_COL_FORMAT_TYPE(df, columns=None, typ='str'):
    '''Format specified columns as specfied type'''
    max = 1 if columns is None else None
    columns = colHelper(df, columns, max=max)
    typ = [typ] if isinstance(typ, str) else typ
    convert_dict = {c:t for c,t in zip(columns, typ)}
    df = df.astype(convert_dict)
    logger.debug('pp.data > Changed column type to {} for these columns: {}'.format(typ, columns))
    return df

def DATA_COL_RENAME(df, columns):
    '''Rename specfied column/s'''
    # we handle dict for all or subset, OR list for all
    if isinstance(columns, dict):
        df.rename(columns = columns, inplace = True)
    else:
        df.columns = columns
    logger.debug('pp.data > Renamed columns: {}'.format(columns))
    return df

def DATA_COL_REORDER(df, columns):
    '''Reorder column titles in specified order. Convenience method for DATA_COL_MOVE_TO_FRONT'''
    # if not all columns are specified, we order to front and add others to end
    df = DATA_COL_REORDER_MOVE_TO_FRONT(df, columns)
    return df

@registerService()
def DATA_COL_REORDER_ASCENDING(df):
    '''Reorder column titles in ascending order'''
    #df.columns = sorted(df.columns.values.tolist())
    df = df[sorted(df.columns.values.tolist())]
    logger.debug('pp.data > Reordered columns: {}'.format(df.columns.values.tolist()))
    return df

@registerService()
def DATA_COL_REORDER_DESCENDING(df):
    '''Reorder column titles in descending order'''
    #df.columns = sorted(df.columns.values.tolist(), reverse = True)
    df = df[sorted(df.columns.values.tolist(), reverse=True)]
    logger.debug('pp.data > Reordered columns: {}'.format(df.columns.values.tolist()))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_REORDER_MOVE_TO_BACK(df, columns=None):
    '''Move specified column/s to back'''
    max = 1 if columns is None else None
    colsToMove = colHelper(df, columns, max=max)
    otherCols = removeElementsFromList(df.columns.values.tolist(), colsToMove)
    df = df[otherCols + colsToMove]
    logger.debug('pp.data > Reordered columns: {}'.format(df.columns.values.tolist()))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_COL_REORDER_MOVE_TO_FRONT(df, columns=None):
    '''Move specified column/s to front'''
    max = 1 if columns is None else None
    colsToMove = colHelper(df, columns, max=max)
    otherCols = removeElementsFromList(df.columns.values.tolist(), colsToMove)
    df = df[colsToMove + otherCols]
    logger.debug('pp.data > Reordered columns: {}'.format(df.columns.values.tolist()))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
    ascending=OPTION_FIELD_SINGLE_BOOLEAN,
)
def DATA_COL_SORT(df, columns=None, ascending=True):
    '''Sort specified column/s in specified asc/desc order'''
    columns = colHelper(df, columns, colsOnNone=True)
    ascending = [ascending for _ in columns]
    df.sort_values(by=columns, ascending=ascending, inplace=True, na_position ='last')
    df.reset_index(inplace=True, drop=True)
    logger.debug('pp.data > Sorted columns: {}'.format(df.columns.values.tolist()))
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_ADD(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell+{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_SUBTRACT(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell-{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_MULTIPLY(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell*{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_DIVIDE(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell/{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_EXPONENT(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell**{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_ROOT(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell**(1./{}.)'.format(num) if 0<=num else '-(-cell)**(1./{}.)'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_FLOORDIV(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell//{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_NUMBER,
    num=FIELD_NUMBER,
)
def DATA_COL_TRANSFORM_MODULUS(df, columns=None, num=0):
    '''Format specified column/s values to uppercase'''
    columns = colHelper(df, columns, type='number')
    eval_string = 'cell%{}'.format(num)
    df = _DATA_COL_FORMAT_CUSTOM(df=df, columns=columns, eval_string=eval_string)
    return df

# DATAFRAME 'ROW' ACTIONS

def DATA_ROW_ADD(df, rows=None):
    '''Add row at specified index'''
    if rows is None: rows = rowHelper(df, max=1)
    if isinstance(rows, tuple):
        rows = list(rows)
    if isinstance(rows, list):
        df.loc[-1] = rows
        df.index = df.index + 1
        df.sort_index(inplace=True)
    #else:
    #    self._df = pd.concat([rows, self._df], ignore_index = True)
    logger.debug('pp.data > Added {} row/s'.format(len(rows)))
    return df

def DATA_ROW_DELETE(df, rows=None):
    rows = list(rows) if isinstance(rows, tuple) else rows
    df.drop(df.index[rows], inplace=True)
    df.reset_index(drop=True, inplace=True)
    logger.debug('pp.data > Deleted {} row/s'.format(len(rows)))
    return df

@registerService(
    numRows=FIELD_INTEGER,
)
def DATA_ROW_KEEP_BOTTOM(df, numRows=1):
    '''Delete all rows except specified bottom N rows'''
    df = df.tail(numRows+1)
    df.reset_index(drop=True, inplace=True)
    logger.debug('pp.data > Kept {} row/s'.format(numRows))
    return df

@registerService()
def DATA_ROW_KEEP_TOP(df, numRows=1):
    '''Delete all rows except specified top N rows'''
    df = df.head(numRows+1)
    df.reset_index(drop=True, inplace=True)
    logger.debug('pp.data > Kept {} row/s'.format(numRows))
    return df

@registerService()
def DATA_ROW_REVERSE_ORDER(df):
    '''Reorder all rows in reverse order'''
    df = df[::-1].reset_index(drop = True)
    logger.debug('pp.data > Reversed row/s')
    return df

@registerService(
    row=FIELD_INTEGER,
)
def DATA_ROW_TO_COLHEADER(df, row=0):
    '''Promote row at specified index to column headers'''
    # make new header, fill in blank values with ColN
    newHeader = df.iloc[row].squeeze()
    newHeader = newHeader.values.tolist()
    for i in newHeader:
        if i == None: i = 'Col'
    df = DATA_COL_RENAME(df, newHeader)
    df = DATA_ROW_DELETE(df, [*range(row+1)])
    return df

@registerService()
def DATA_ROW_FROM_COLHEADER(df):
    '''Demote column headers to make 1st row of table'''
    df = DATA_ROW_ADD(df, list(df.columns.values))
    newHeader = ['Col' + str(x) for x in range(len(df.columns))]
    df = DATA_COL_RENAME(df, newHeader)
    return df

# DATAFRAME ACTIONS
def DATA_APPEND(df, otherdf):
    '''Append a table to bottom of current table'''
    df = df.append(otherdf, ignore_index=True)
    logger.debug('pp.data > Appended dataframe')
    return df

@registerService(
    groupby=OPTION_FIELD_MULTI_COL_ANY,
    aggregates=FIELD_STRING,
)
def DATA_GROUP(df, groupby=None, aggregates=None):
    '''Group table contents by specified columns with optional aggregation (sum/max/min etc)'''
    max = 1 if groupby is None else None
    groupby = colHelper(df, groupby, max=max)
    if aggregates is None:
        df = DATA_COL_ADD_FIXED(df, 1, 'count')
        c = df.columns[-1]
        df = df.groupby(groupby, as_index=False, dropna=False).agg({c:'count'})
        #self._df = self._df.groupby(groupby, as_index=False, dropna=False).first()
    else:
        df = df.groupby(groupby, as_index=False, dropna=False).agg(aggregates)
        #self._df.columns = ['_'.join(col).rstrip('_') for col in self._df.columns.values]
    logger.debug('pp.data > Grouped dataframe')
    return df

def DATA_MERGE(df, otherdf, on, how = 'left'):
    df = pd.merge(df, otherdf, on=on, how=how)
    logger.debug('pp.data > Merged dataframe')
    return df

@registerService()
def DATA_TRANSPOSE(df):
    df = df.transpose()
    logger.debug('pp.data > Transposed dataframe')
    return df

@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_UNPIVOT(df, columns=None):
    columns = colHelper(df, columns)
    df = pd.melt(df, id_vars=columns)
    logger.debug('pp.data > Unpivot dataframe')
    return df

@registerService(
    indexCols=OPTION_FIELD_MULTI_COL_ANY,
    cols=OPTION_FIELD_MULTI_COL_ANY,
    vals=OPTION_FIELD_MULTI_COL_ANY,
)
def DATA_PIVOT(df, indexCols, cols, vals):
    #indexCols = list(set(df.columns) - set(cols) - set(vals))
    df = df.pivot(index = indexCols, columns = cols, values = vals).reset_index().rename_axis(mapper = None,axis = 1)
    logger.debug('pp.data > Pivotted dataframe')
    return df

