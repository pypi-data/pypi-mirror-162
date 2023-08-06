from pp.log import logger
from pp.util import *
from pp.constants import *

#non-standard libraries
import pandas as pd

#READER 
READERS = {}
READERTYPES = []
READER_SIMPLE_CSV_EXCEL = 'reader_simple_csv_excel'
READERTYPES.extend([
    READER_SIMPLE_CSV_EXCEL
])

#WRITER
WRITERS = {}
WRITERTYPES = []
WRITER_SIMPLE_CSV_EXCEL = 'writer_simple_csv_excel'
WRITERTYPES.extend([
    WRITER_SIMPLE_CSV_EXCEL
])

#PREVIEWER TYPES
PREVIEWERS = {}
PREVIEWERTYPES = []
PREVIEWER_SIMPLEDATA = 'previewer_simpledata'
PREVIEWERTYPES.extend([
    PREVIEWER_SIMPLEDATA
])

@registerService(
    src=FIELD_STRING,
)
def READ_CSV(src):
    read_df = _read(src=src, reader=READER_SIMPLE_CSV_EXCEL)
    logger.debug('pp.io > READ_CSV Read from: {}'.format(src))
    return read_df

@registerService()
def READ_DATA_ATTRITION():
    return READ_CSV(src=DATA_ATTRITION)

def WRITE_CSV(df, tar):
    _write(content=df, tar=tar, writer=WRITER_SIMPLE_CSV_EXCEL)
    return

def _read(src=None, reader=None):
    # call specified reader
    if reader and reader in READERS.keys():
        r = READERS[reader](src=src)

    #else, fallback to 1-by-1 check of readers supporting our src - use first 'OK' reader
    else:
        for r in READERS.values():
            if r.ok(src):
                r = r(src=src)
                break
        else:
            print('Reader not found')
            return

    #If success, instantiate Reader, read df, append to our data
    df = r.read()
    return df

def _write(content, tar=None, writer=None):
    #check config for *valid* section matching our src
    if writer and writer in WRITERS.keys():
        w = WRITERS[writer](tar=tar)

    #else, fallback to 1-by-1 check of readers supporting our src - use first 'OK' reader
    else:
        for w in WRITERS.values():
            if w.ok(tar):
                w = w(tar=tar)
                break
        else:
            print('Writer not found')
            return

    w.write(content)
    return

def _preview(content, previewer=None):
    #check config for *valid* section matching our src
    if previewer and previewer in PREVIEWERS.keys():
        p = PREVIEWERS[previewer]()

    #else, fallback to 1-by-1 check of readers supporting our src - use first 'OK' reader
    else:
        for p in PREVIEWERS.values():
            if p.ok():
                p = p()
                break
        else:
            print('Previewer not found')
            return

    p.preview(content)
    return

#READERS, WRITERS & PREVIEWERS
    
def register(cls):
    '''Register Reader, Writer & Previewer objects'''
    t = cls.type()
    if t is None or (t not in READERTYPES and t not in WRITERTYPES and t not in PREVIEWERTYPES):
        raise ValueError('Not valid Reader, Writer or Previewer')
    if t in READERTYPES:
        READERS[t] = cls
    elif t in WRITERTYPES:
        WRITERS[t] = cls
    else:
        PREVIEWERS[t] = cls
    logger.debug('pp.io > register: Registered Reader/Writer/Previewer: {}'.format(cls))
    return cls
    
class BaseReader():
    def __init__(self, src=None):
        self._src = src
        
    @classmethod
    def type(cls):
        '''Returns key used to regsiter Reader type'''
        return None #don't register BaseReader
    
    @classmethod
    def ok(cls, src):
        '''Check if this Reader can handle specified source'''
        return False #don't register BaseReader
        
    def read(self):
        '''Returns dataframe from specified source'''
        #check cfg, read, return df
        return

@register 
class SimpleCsvExcelReader(BaseReader):
    def __init__(self, src=None):
        super().__init__(src=src)
        
    @classmethod
    def type(cls):
        '''Returns key used to regsiter Reader type'''
        return READER_SIMPLE_CSV_EXCEL
        
    @classmethod
    def ok(cls, src):
        '''Returns key used to regsiter Reader type'''
        if isinstance(src, str) and (src[-4:]=='.csv' or src[-5:]=='.xlsx'):
            return True
        return False #don't register BaseReader
        
    def read(self):
        '''Returns dataframe based on config'''
        s = self._src
        if isinstance(s, str) and (s[-4:]=='.csv'):
            return pd.read_csv(s)
        elif isinstance(s, str) and (s[-5:]=='.xlsx'):
            return pd.read_excel(s)
        else:
            if not hasattr(s, 'read'):
                raise TypeError("Invalid reader source")
            else:
                s.seek(0)
                return pd.read_csv(s)
            
class BaseWriter():
    def __init__(self, tar=None):
        self._tar = tar
        
    @classmethod
    def type(cls):
        '''Returns key used to regsiter type'''
        return None #don't register Base
        
    @classmethod
    def ok(cls, tar):
        '''Returns key used to register type'''
        return False #don't register Base
        
    def write(self, content):
        '''Writes based on config'''
        #check cfg, write, return
        return

@register 
class SimpleCsvExcelWriter(BaseWriter):
    def __init__(self, tar=None):
        super().__init__(tar=tar)
        
    @classmethod
    def type(cls):
        '''Returns key used to regsiter Reader type'''
        return WRITER_SIMPLE_CSV_EXCEL
        
    @classmethod
    def ok(cls, tar):
        '''Returns key used to register type'''
        if isinstance(tar, str) and (tar[-4:]=='.csv' or tar[-5:]=='.xlsx'):
            return True
        return False #don't register BaseReader
        
    def write(self, content):
        '''Writes dataframe based on config'''
        t = self._tar
        if isinstance(t, str) and (t[-4:]=='.csv'):
            return df.to_csv(t, index=False)
        elif isinstance(t, str) and (t[-5:]=='.xlsx'):
            return df.to_excel(t, index=False)
        else:
            raise TypeError("Invalid writer target")
        
class BasePreviewer():
    @classmethod
    def type(cls):
        '''Returns key used to regsiter Reader type'''
        return None #don't register Base
    
    @classmethod    
    def preview(self, content):
        '''Returns dataframe based on config'''
        return

@register 
class SimpleDATAPreviewer(BasePreviewer):
    @classmethod
    def type(cls):
        '''Returns key used to regsiter type'''
        return PREVIEWER_SIMPLEDATA
    
    @classmethod
    def preview(self, content):
        '''Returns dataframe based on config'''
        df = content[DATATYPE_DATAFRAME]['active']
        if isinstance(df.columns, pd.MultiIndex): 
            arrays = [range(0, len(df.columns)), df.columns.get_level_values(0), df.dtypes]
            mi = pd.MultiIndex.from_arrays(arrays, names=('Num', 'Name', 'Type'))
        else:
            arrays = [range(0, len(df.columns)), df.columns, df.dtypes]
            mi = pd.MultiIndex.from_arrays(arrays, names=('Num', 'Name', 'Type'))
        df.columns = mi
        return display(df)
    
'''
@registerPreviewer 
class PreviewerChartCurrent(BasePreviewer):
    @classmethod
    def type(cls):
        return PREVIEWER_CHART_CURRENT
    
    @classmethod
    def preview(self, data):
        viz = data[DATATYPE_VIZ]['active']
        
        #if viz contains multiple plots eg. HIST_LIST 
        if isinstance(viz, list):
            return tuple([v.show(config=FIGURE_CONFIG_SHOW) for v in viz]), PREVIEWERS[PREVIEWER_SIMPLEDATA].preview(data)
            
        return viz.show(config=FIGURE_CONFIG_SHOW), PREVIEWERS[PREVIEWER_SIMPLEDATA].preview(data)

@registerWriter 
class SimpleVizWriter(BaseWriter):
    def __init__(self, cfg=None, tar=None):
        super().__init__(cfg=cfg, tar=tar)
        
    @classmethod
    def type(cls):
        return WRITER_SIMPLE_VIZ
        
    @classmethod
    def ok(cls, tar):
        if isinstance(tar, str) and tar[-5:]=='.html':
            return True
        return False
        
    def write(self, data):
        vizs = data[DATATYPE_VIZ]['stack']
        write_type = 'w'
        def wr(path, vizs):
            #handle mixed lists (individual viz & list of viz)
            vizs1 = []
            for v in vizs:
                vizs1.extend(v) if isinstance(v, list) else vizs1.extend([v]) 
            with open(path, write_type) as f:
                f.write("Report generated: " + str(datetime.datetime.today()))
                for v in vizs1:
                    f.write(v.to_html(full_html=False, include_plotlyjs='cdn', default_height=360, default_width='95%', config=FIGURE_CONFIG_SHOW))
        if self._cfg:
            c = self._cfg
            if 'html' in c.keys():
                wr(c['html'], vizs)
                return
            else:
                pass
        t = self._tar
        if isinstance(t, str) and tar[-5:]=='.html':
            wr(tar, vizs)
            return 
        else:
            raise TypeError("Invalid writer target")
            
'''