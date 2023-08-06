from pp.log import logger
from pp.util import *
from pp.constants import *

#non-standard libraries
import pandas as pd
import plotly.express as px

@registerService(
    x=FIELD_FLOAT, 
    line_width=FIELD_INTEGER, 
    line_dash=FIELD_STRING, 
    line_color=FIELD_STRING, 
    annotation_text=FIELD_STRING, 
    annotation_position=FIELD_STRING
)
def DRAW_VLINE(viz, x=None, line_width=None, line_dash=None, line_color=None, annotation_text=None, annotation_position=None):
    viz.add_vline(
        x=x, line_width=line_width, line_dash=line_dash, line_color=line_color, 
        annotation_text=annotation_text, annotation_position=annotation_position,
        annotation_font_color=line_color,
    )
    logger.debug('pp.draw > DRAW_VLINE')
    return viz

@registerService(
    x=FIELD_FLOAT, 
    line_width=FIELD_INTEGER, 
    line_dash=FIELD_STRING, 
    line_color=FIELD_STRING, 
    annotation_text=FIELD_STRING, 
    annotation_position=FIELD_STRING
)
def DRAW_HLINE(viz, y=None, line_width=None, line_dash=None, line_color=None, annotation_text=None, annotation_position=None):
    viz.add_hline(y=y, line_width=line_width, line_dash=line_dash, line_color=line_color,
                  annotation_text=annotation_text, annotation_position=annotation_position,
                  annotation_font_color=line_color)
    logger.debug('pp.draw > DRAW_HLINE')
    return viz

@registerService(
    y0=FIELD_FLOAT, 
    y1=FIELD_FLOAT, 
    line_width=FIELD_INTEGER, 
    fillcolor=FIELD_STRING, 
    opacity=FIELD_FLOAT, 
    line_color=FIELD_STRING, 
    annotation_text=FIELD_STRING, 
    annotation_position=FIELD_STRING
)
def DRAW_HRECT(viz, y0=None, y1=None, line_width=None, fillcolor=None, opacity=None, line_color=None, annotation_text=None, annotation_position=None):
    viz.add_hrect(y0=y0, y1=y1, line_width=line_width, fillcolor=fillcolor, opacity=opacity, 
                  annotation_text=annotation_text, annotation_position=annotation_position,
                  annotation_font_color=fillcolor)
    logger.debug('pp.draw > DRAW_HRECT')
    return viz

@registerService(
    x0=FIELD_FLOAT, 
    x1=FIELD_FLOAT, 
    fillcolor=FIELD_STRING, 
    opacity=FIELD_FLOAT, 
    annotation_text=FIELD_STRING, 
    annotation_position=FIELD_STRING
)
def DRAW_VRECT(viz, x0=None, x1=None, fillcolor=None, opacity=None, annotation_text=None, annotation_position=None):
    viz.add_vrect(x0=x0, x1=x1, line_width=0, fillcolor=fillcolor, opacity=opacity, 
                  annotation_text=annotation_text, annotation_position=annotation_position,
                  annotation_font_color=fillcolor)
    logger.debug('pp.draw > DRAW_VRECT')
    return viz
