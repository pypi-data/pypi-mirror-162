from pp.log import logger
from pp.util import *
from pp.data import *

#python standard libraries
import datetime

#non-standard libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

FIGURE_CONFIG_SHOW = {
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png', # one of png, svg, jpeg, webp
        'filename': 'custom_image',
        'height': None,
        'width': None,
        'scale': 5 # Multiply title/legend/axis/canvas sizes by this factor
    },
    'edits': {
        'axisTitleText': True,
        'legendPosition': True,
        'legendText': True,
        'titleText': True,
        'annotationPosition': True,
        'annotationText': True
    }
}

FIGURE_CONFIG_BASE =  {
    'dragmode': 'drawopenpath',
    'modebar_remove': ['resetScale', 'lasso2d'], #'select', 'zoom',
    'modebar_add': ['drawline', 'drawcircle',  'drawrect', 'eraseshape', 'pan2d'],
    'legend':{
        'traceorder':'reversed'
    },
    'title': {
            'x': 0
    }
}

VIZ_COLORS_PLOTLY = px.colors.qualitative.Plotly
VIZ_COLORS_D3 = px.colors.qualitative.D3
VIZ_COLORS_G10 = px.colors.qualitative.G10
VIZ_COLORS_T10 = px.colors.qualitative.T10
VIZ_COLORS_ALPHABET = px.colors.qualitative.Alphabet
VIZ_COLORS_DARK24 = px.colors.qualitative.Dark24
VIZ_COLORS_LIGHT24 = px.colors.qualitative.Light24
VIZ_COLORS_SET1 = px.colors.qualitative.Set1
VIZ_COLORS_PASTEL1 = px.colors.qualitative.Pastel1
VIZ_COLORS_DARK2 = px.colors.qualitative.Dark2
VIZ_COLORS_SET2 = px.colors.qualitative.Set2
VIZ_COLORS_PASTEL2 = px.colors.qualitative.Pastel2
VIZ_COLORS_SET3 = px.colors.qualitative.Set3
VIZ_COLORS_ANTIQUE = px.colors.qualitative.Antique
VIZ_COLORS_BOLD = px.colors.qualitative.Bold
VIZ_COLORS_PASTEL = px.colors.qualitative.Pastel
VIZ_COLORS_PRISM = px.colors.qualitative.Prism
VIZ_COLORS_SAFE = px.colors.qualitative.Safe
VIZ_COLORS_VIVID = px.colors.qualitative.Vivid
VIZ_COLORS_DEFAULT = VIZ_COLORS_ANTIQUE
    
def _fig(fig=None, settings=None, overwrite=True):
    '''Handles figure displaying for IPython'''
    if fig is not None and not isinstance(fig, list):
        d = {**FIGURE_CONFIG_BASE, **settings} if settings else FIGURE_CONFIG_BASE
        fig.update_layout(dict1=d, overwrite=overwrite)
        #self._append(DATATYPE_VIZ, fig)
        #self._preview(preview=PREVIEWER_CHART_CURRENT)
    elif fig is not None and isinstance(fig, list):
        d = {**FIGURE_CONFIG_BASE, **settings} if settings else FIGURE_CONFIG_BASE
        for f in fig:
            f.update_layout(dict1=d, overwrite=overwrite)
        #self._append(DATATYPE_VIZ, fig)
        #self._preview(preview=PREVIEWER_CHART_CURRENT) 

# VIZUALIZATION ACTIONS

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    y=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
)
def VIZ_AREA(df, x=None, y=None, color=None, facet_col=None, facet_row=None, markers=True, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a line plot with shaded area'''
    # catch missing x/y combination to prevent default to 'wide'
    if all(not param for param in (x, y)):
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, y, color, facet_col, facet_row = (
        colHelper(df=df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, y, color, facet_col, facet_row])
    fig = px.area(data_frame=df, x=x, y=y, color=color, facet_col=facet_col, facet_row=facet_row, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_AREA end')
    return fig

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    y=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
)
def VIZ_BAR(df, x=None, y=None, color=None, facet_col=None, facet_row=None, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a bar plot'''
    # catch missing x/y combination to prevent default to 'wide'
    if all(not param for param in (x, y)):
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, y, color, facet_col, facet_row = (
        colHelper(df=df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, y, color, facet_col, facet_row])
    fig = px.histogram(data_frame=df, x=x, y=y, color=color, facet_col=facet_col, facet_row=facet_row, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_BAR end')
    return fig

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    y=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
)
def VIZ_BOX(df, x=None, y=None, color=None, facet_col=None, facet_row=None, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a box plot'''
    # catch missing x/y combination to prevent default to 'wide'
    if all(not param for param in (x, y)):
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, y, color, facet_col, facet_row = (
        colHelper(df=df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, y, color, facet_col, facet_row])
    fig = px.box(data_frame=df, x=x, y=y, color=color, facet_col=facet_col, facet_row=facet_row, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_BOX end')
    return fig

@registerService()
def VIZ_DATASTATS(df):
    '''Show basic summary statistics of table contents'''
    df = df.describe(include='all').T
    df.insert(0, 'Feature', df.index)
    df = DATA_COL_ADD_INDEX_FROM_0(df=df, name='No')
    df = DATA_COL_REORDER_MOVE_TO_FRONT(df=df, columns='No')
    fig = VIZ_TABLE(df=df)
    logger.debug('pp.viz > VIZ_DATASTATS end')
    return fig

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
)
def VIZ_HIST(df, x=None, color=None, facet_col=None, facet_row=None, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a histogram'''
    # catch missing x/y combination to prevent default to 'wide'
    if not x:
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, color, facet_col, facet_row = (
        colHelper(df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, color, facet_col, facet_row])
    fig = px.histogram(data_frame=df, x=x, color=color, facet_col=facet_col, facet_row=facet_row, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_HIST end')
    return fig

'''
@registerService(
    color=OPTION_FIELD_SINGLE_COL_ANY, 
)
'''
def VIZ_HIST_LIST(df, color=None, swatch=VIZ_COLORS_ANTIQUE):
    '''Draw a histogram for all fields in current dataframe'''
    color = colHelper(df=df, columns=color, max=1, colsOnNone=False, forceReturnAsList=False)
    v = [px.histogram(data_frame=df, x=c, color=color, color_discrete_sequence=swatch) for c in df.columns]
    _fig(v)
    logger.debug('pp.viz > VIZ_HIST_LIST end')
    return v

'''
@registerService(
    path=OPTION_FIELD_MULTI_COL_ANY,
    values=OPTION_FIELD_SINGLE_COL_ANY,
)
'''
def VIZ_ICICLE(df, path, values, root='All data', swatch=VIZ_COLORS_DEFAULT):
    '''Draw a treemap plot'''
    path = [px.Constant("All data")] + colHelper(df=df, columns=path)
    values = colHelper(df=df, columns=values, max=1, type='number', forceReturnAsList=False)
    # make leaf dict (isna), update

    #p = self._colHelper(path)
    #d = self._df[p].groupby(p, as_index=False, dropna=False).first()
    #d = d[d.isna().any(axis=1)].to_dict(orient='records')
    #print(d)

    #d = df.groupby('Dia').apply(lambda a: dict(a.groupby('macap').apply(lambda x: dict(zip(x['transmission'], x['bytes'])))))
    #d = d.to_dict()

    # treemap, icicle, sunburst break on NaN. Replace with 'None' for this call
    df1 = df.where(pd.notnull, None)
    try:
        fig = px.icicle(data_frame=df1, path=path, values=values, color_discrete_sequence=swatch)
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        _fig(fig)
    except ValueError:
        fig = VIZ_ICICLE(df1, path[1:-1], values, root=path[0])
    logger.debug('pp.viz > VIZ_ICICLE end')
    return fig

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    y=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
)
def VIZ_LINE(df, x=None, y=None, color=None, facet_col=None, facet_row=None, markers=True, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a line plot'''
    # catch missing x/y combination to prevent default to 'wide'
    if all(not param for param in (x, y)):
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, y, color, facet_col, facet_row = (
        colHelper(df=df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, y, color, facet_col, facet_row])
    fig = px.line(data_frame=df, x=x, y=y, color=color, facet_col=facet_col, facet_row=facet_row, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_LINE end')
    return fig

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    y=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
    size=OPTION_FIELD_SINGLE_COL_NUMBER,
)
def VIZ_SCATTER(df, x=None, y=None, color=None, facet_col=None, facet_row=None, size=None, swatch=VIZ_COLORS_ANTIQUE):
    '''Draw a scatter plot'''
    # catch missing x/y combination to prevent default to 'wide'
    if all(not param for param in (x, y)):
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, y, color, facet_col, facet_row = (
        colHelper(df=df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, y, color, facet_col, facet_row])
    fig = px.scatter(data_frame=df, x=x, y=y, color=color, facet_col=facet_col, facet_row=facet_row, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_SCATTER end')
    return fig

'''
@registerService(
    dimension=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
)
'''
def VIZ_SCATTERMATRIX(df, dimensions=None, color=None, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a scatter matrix plot'''
    dimensions, color = (
        colHelper(df=df, columns=i, max=j, colsOnNone=False, forceReturnAsList=False) for i, j in [(dimensions, None), (color, 1)])
    fig = px.scatter_matrix(data_frame=df, dimensions=dimensions, color=color, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_SCATTERMATRIX end')
    return fig

'''
@registerService(
    path=OPTION_FIELD_MULTI_COL_ANY,
    values=OPTION_FIELD_SINGLE_COL_ANY,
)
'''
def VIZ_SUNBURST(df, path, values, root='All data', swatch=VIZ_COLORS_DEFAULT):
    '''Draw a treemap plot'''
    path = [px.Constant("All data")] + colHelper(df=df, columns=path)
    values = colHelper(df=df, columns=values, max=1, type='number', forceReturnAsList=False)
    # treemap, icicle, sunburst break on NaN. Replace with 'None' for this call
    df1 = df.where(pd.notnull, None)
    try:
        fig = px.sunburst(data_frame=df1, path=path, values=values, color_discrete_sequence=swatch)
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        _fig(fig)
    except ValueError:
        fig = VIZ_SUNBURST(df1, path[1:-1], values, root=path[0])
    logger.debug('pp.viz > VIZ_SUNBURST end')
    return fig

'''
@registerService(
    columns=OPTION_FIELD_MULTI_COL_ANY, 
)
'''
def VIZ_TABLE(df, columns=None, **kwargs):
    '''Draw a table'''
    columns = colHelper(df=df, columns=columns)
    cell_values = df[columns].to_numpy().T
    fig = go.Figure(data=[go.Table(
        header=dict(values=columns,
                   align='left',
                   font_size=12,
                   height=30),
        cells=dict(values=cell_values,
                  align='left',
                   font_size=12,
                   height=30))
    ])
    _fig(fig)
    logger.debug('pp.viz > VIZ_TABLE end')
    return fig

'''
@registerService(
    path=OPTION_FIELD_MULTI_COL_ANY,
    values=OPTION_FIELD_SINGLE_COL_ANY,
)
'''
def VIZ_TREEMAP(df, path, values, root='All data', swatch=VIZ_COLORS_DEFAULT):
    '''Draw a treemap plot'''
    path = [px.Constant("All data")] + colHelper(df=df, columns=path)
    values = colHelper(df=df, columns=values, max=1, type='number', forceReturnAsList=False)
    # treemap, icicle, sunburst break on NaN. Replace with 'None' for this call
    df1 = df.where(pd.notnull, None)
    try:
        fig = px.treemap(data_frame=df1, path=path, values=values, color_discrete_sequence=swatch)
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        _fig(fig)
    except ValueError:
        fig = VIZ_TREEMAP(df1, path[1:-1], values, root=path[0])
    logger.debug('pp.viz > VIZ_TREEMAP end')
    return fig

@registerService(
    x=OPTION_FIELD_SINGLE_COL_ANY,
    y=OPTION_FIELD_SINGLE_COL_ANY,
    color=OPTION_FIELD_SINGLE_COL_ANY, 
    facet_col=OPTION_FIELD_SINGLE_COL_ANY,
    facet_row=OPTION_FIELD_SINGLE_COL_ANY,
)
def VIZ_VIOLIN(df, x=None, y=None, color=None, facet_col=None, facet_row=None, swatch=VIZ_COLORS_DEFAULT):
    '''Draw a violin plot'''
    # catch missing x/y combination to prevent default to 'wide'
    if all(not param for param in (x, y)):
        x = colHelper(df=df, columns=x, max=1, colsOnNone=True, forceReturnAsList=False)
    x, y, color, facet_col, facet_row = (
        colHelper(df=df, columns=i, max=1, colsOnNone=False, forceReturnAsList=False) for i in [x, y, color, facet_col, facet_row])
    fig = px.violin(data_frame=df, x=x, y=y, color=color, facet_col=facet_col, facet_row=facet_row, box=True, color_discrete_sequence=swatch)
    _fig(fig)
    logger.debug('pp.viz > VIZ_VIOLIN end')
    return fig

fig_defaults = {
    'data': [
        {
            'alignmentgroup': 'True', 
            'bingroup': 'x', 
            'hovertemplate': 
            'Attrition=Yes<br>Age=%{x}<br>count=%{y}<extra></extra>', 
            'legendgroup': 'Yes', 
            'marker': {
                'color': 'rgb(133, 92, 117)', 
                'pattern': {
                    'shape': ''
                }
            }, 
            'name': 'Yes', 
            'offsetgroup': 'Yes', 
            'orientation': 'v', 
            'showlegend': True, 
            'x': [], 
            'xaxis': 'x', 
            'yaxis': 'y', 
            'type': 'histogram'
        },
        {
            'alignmentgroup': 'True', 
            'bingroup': 'x', 
            'hovertemplate': 'Attrition=No<br>Age=%{x}<br>count=%{y}<extra></extra>', 
            'legendgroup': 'No', 
            'marker': {
                'color': 'rgb(217, 175, 107)', 
                'pattern': {
                    'shape': ''
                }
            }, 
            'name': 'No', 
            'offsetgroup': 'No', 
            'orientation': 'v', 
            'showlegend': True, 
            'x': [], 
            'xaxis': 'x', 
            'yaxis': 'y', 
            'type': 'histogram'
        }
    ], 
    'layout': {
        'template': {
            'data': {
                'bar': [{
                    'error_x': {
                        'color': '#2a3f5f'
                    }, 
                    'error_y': {
                        'color': '#2a3f5f'
                    }, 'marker': {
                        'line': {
                            'color': '#E5ECF6', 'width': 0.5
                        }, 
                        'pattern': {
                            'fillmode': 'overlay', 
                            'size': 10, 
                            'solidity': 0.2
                        }
                    }, 
                    'type': 'bar'
                }], 
                'barpolar': [{
                    'marker': {
                        'line': {
                            'color': '#E5ECF6', 'width': 0.5
                        }, 
                        'pattern': {
                            'fillmode': 'overlay', 
                            'size': 10, 
                            'solidity': 0.2
                        }
                    }, 
                    'type': 'barpolar'
                }], 
                'carpet': [{
                    'aaxis': {
                        'endlinecolor': '#2a3f5f', 
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'minorgridcolor': 'white', 
                        'startlinecolor': '#2a3f5f'
                    }, 
                    'baxis': {
                        'endlinecolor': '#2a3f5f', 
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'minorgridcolor': 'white', 
                        'startlinecolor': '#2a3f5f'
                    }, 
                    'type': 'carpet'
                }], 
                'choropleth': [{
                    'colorbar': {
                        'outlinewidth': 0, 
                        'ticks': ''
                    }, 
                    'type': 'choropleth'
                }], 
                'contour': [{
                    'colorbar': {
                        'outlinewidth': 0, 
                        'ticks': ''
                    }, 
                    'colorscale': [], 
                    'type': 'histogram2dcontour'
                }], 
                'mesh3d': [{
                    'colorbar': {
                        'outlinewidth': 0, 
                        'ticks': ''
                    }, 
                    'type': 'mesh3d'
                }], 
                'parcoords': [{
                    'line': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'parcoords'
                }], 
                'pie': [{
                    'automargin': True, 'type': 'pie'
                }], 
                'scatter': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scatter'
                }], 
                'scatter3d': [{
                    'line': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scatter3d'
                }], 
                'scattercarpet': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scattercarpet'
                }], 
                'scattergeo': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scattergeo'
                }], 
                'scattergl': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scattergl'
                }], 
                'scattermapbox': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scattermapbox'
                }], 
                'scatterpolar': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scatterpolar'
                }], 
                'scatterpolargl': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scatterpolargl'
                }], 
                'scatterternary': [{
                    'marker': {
                        'colorbar': {
                            'outlinewidth': 0, 
                            'ticks': ''
                        }}, 
                    'type': 'scatterternary'
                }], 
                'surface': [{
                    'colorbar': {
                        'outlinewidth': 0, 
                        'ticks': ''
                    }, 
                    'colorscale': [], 
                    'type': 'surface'
                }], 
                'table': [{
                    'cells': {
                        'fill': {
                            'color': '#EBF0F8'
                        }, 
                        'line': {
                            'color': 'white'
                        }}, 
                    'header': {
                        'fill': {
                            'color': '#C8D4E3'
                        }, 
                        'line': {
                            'color': 'white'
                        }}, 
                    'type': 'table'
                }]
            }, 
            'layout': {
                'annotationdefaults': {
                    'arrowcolor': '#2a3f5f', 
                    'arrowhead': 0, 
                    'arrowwidth': 1
                }, 
                'autotypenumbers': 'strict', 
                'coloraxis': {
                    'colorbar': {
                        'outlinewidth': 0, 
                        'ticks': ''
                    }
                }, 
                'colorscale': {
                    'diverging': []
                }, 
                'colorway': [], 
                'font': {
                    'color': '#2a3f5f'
                }, 
                'geo': {
                    'bgcolor': 'white', 
                    'lakecolor': 'white', 
                    'landcolor': '#E5ECF6', 
                    'showlakes': True, 
                    'showland': True, 
                    'subunitcolor': 'white'
                }, 
                'hoverlabel': {
                    'align': 'left'
                }, 
                'hovermode': 'closest', 
                'mapbox': {
                    'style': 'light'
                }, 
                'paper_bgcolor': 'white', 
                'plot_bgcolor': '#E5ECF6', 
                'polar': {
                    'angularaxis': {
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'ticks': ''
                    }, 
                    'bgcolor': '#E5ECF6', 
                    'radialaxis': {
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'ticks': ''
                    }
                }, 
                'scene': {
                    'xaxis': {
                        'backgroundcolor': '#E5ECF6', 
                        'gridcolor': 'white', 
                        'gridwidth': 2, 
                        'linecolor': 'white', 
                        'showbackground': True, 
                        'ticks': '', 
                        'zerolinecolor': 'white'
                    }, 
                    'yaxis': {
                        'backgroundcolor': '#E5ECF6', 
                        'gridcolor': 'white', 
                        'gridwidth': 2, 
                        'linecolor': 'white', 
                        'showbackground': True, 
                        'ticks': '', 
                        'zerolinecolor': 'white'
                    }, 
                    'zaxis': {
                        'backgroundcolor': '#E5ECF6', 
                        'gridcolor': 'white', 
                        'gridwidth': 2, 
                        'linecolor': 'white', 
                        'showbackground': True, 
                        'ticks': '', 
                        'zerolinecolor': 'white'
                    }
                }, 
                'shapedefaults': {
                    'line': {
                        'color': '#2a3f5f'
                    }
                }, 
                'ternary': {
                    'aaxis': {
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'ticks': ''
                    }, 
                    'baxis': {
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'ticks': ''
                    }, 
                    'bgcolor': '#E5ECF6', 
                    'caxis': {
                        'gridcolor': 'white', 
                        'linecolor': 'white', 
                        'ticks': ''
                    }
                }, 
                'title': {
                    'x': 0.05
                }, 
                'xaxis': {
                    'automargin': True, 
                    'gridcolor': 'white', 
                    'linecolor': 'white', 
                    'ticks': '', 
                    'title': {
                        'standoff': 15
                    }, 
                    'zerolinecolor': 'white', 
                    'zerolinewidth': 2
                }, 
                'yaxis': {
                    'automargin': True, 
                    'gridcolor': 'white', 
                    'linecolor': 'white', 
                    'ticks': '', 
                    'title': {
                        'standoff': 15
                    }, 
                    'zerolinecolor': 'white', 
                    'zerolinewidth': 2
                }
            }
        },
        'xaxis': {
            'anchor': 'y', 
            'domain': [0.0, 1.0], 
            'title': {
                'text': 'Age'
            }
        }, 
        'yaxis': {
            'anchor': 'x', 
            'domain': [0.0, 1.0], 
            'title': {
                'text': 'count'
            }
        }, 
        'legend': {
            'traceorder': 'reversed'
        }, 
        'margin': {
            't': 60
        }, 
        'barmode': 'relative', 
        'modebar': {
            'remove': ['resetScale', 'lasso2d'], 
            'add': ['drawline', 'drawcircle', 'drawrect', 'eraseshape', 'pan2d']
        }, 
        'dragmode': 'drawopenpath'
    }
}
