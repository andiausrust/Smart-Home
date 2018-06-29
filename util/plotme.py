import bokeh
import bokeh.models   as bmod
import bokeh.plotting as bplt
from bokeh.io import export_png, export_svgs

#import networkx as nx

import pandas as pd
from bokeh.models.formatters import PrintfTickFormatter
from pandas import DataFrame

from util.config import SHELL
from util.config import Config

##           width=1200,height=300,
## hover =  bmodels.HoverTool()
#tooltips=[
#            ("index", "$index")
#            ("(x,y)", "($x, $y)"),
#            ("desc", "@desc"),
#            ("bla", "bla <br> morebla <br> evenmore")
#        ]
#hover = bmodels.HoverTool(tooltips=tooltips)
#left.add_tools(hover)

COLORS = ['red',       'green',      'darkblue',  'gold',
          'turquoise', 'darkorchid', 'olive',     'lightgreen']

class Plotme:
    @staticmethod
    def plot3(model, name, searchfor: str):
        m1 = model[0]
        m2 = model[1]

        if len(model)>2:
            m3 = model[2]
        else:
            m3 = None

        dfp1 = m1.result_df(searchfor)
        dfp2 = m2.result_df(searchfor)
        source1 = bmod.ColumnDataSource(dfp1)
        source2 = bmod.ColumnDataSource(dfp2)

        if m3:
            dfp3 = m3.result_df(searchfor)
            source3 = bmod.ColumnDataSource(dfp3)

        #print(dfp1.values.max())
        #print(dfp2.values.max())
        #print(dfp3.values.max())
        if m3:
            yrange =[0.0, max(dfp1.values.max(), dfp2.values.max(), dfp3.values.max()) ]
        else:
            yrange =[0.0, max(dfp1.values.max(), dfp2.values.max()) ]

        TOOLS = 'pan,box_zoom, box_select,reset'   # wheel_zoom,
#                                                                                                                                                                      545         500
        left =   bplt.figure(title=name[0], x_axis_label='time', y_axis_label='', y_range=yrange, x_axis_type="datetime", toolbar_location="above", tools=TOOLS, width=545, height=500)
        for i,col in enumerate(sorted(list(dfp1.columns))):
            left.line    (x="index", y=col,      source=source1, legend=" "+col,     line_width=2, line_color=COLORS[i],    alpha=0.6)

        middle = bplt.figure(title=name[1], x_axis_label='time', y_axis_label='', y_range=yrange, x_axis_type="datetime", toolbar_location="above", tools=TOOLS, width=545, height=500)
        for i,col in enumerate(sorted(list(dfp2.columns))):
            middle.line  (x="index", y=col,      source=source2, legend=" "+col,     line_width=2, line_color=COLORS[i],    alpha=0.6)

#        left.legend.location = "center_right"
        left.legend.background_fill_alpha = 0.4
#        middle.legend.location = "center_right"
        middle.legend.background_fill_alpha = 0.4

        if m3:
            right =  bplt.figure(title=name[2], x_axis_label='time', y_axis_label='', y_range=yrange, x_axis_type="datetime", toolbar_location="above", tools=TOOLS, width=545, height=600)
            for i,col in enumerate(sorted(list(dfp3.columns))):
                right.line   (x="index", y=col,      source=source3, legend=" "+col,     line_width=2, line_color=COLORS[i],    alpha=0.6)

#            right.legend.location = "top_left"
            right.legend.background_fill_alpha = 0.4

        if m3:
            p = bokeh.layouts.gridplot([[left,middle,right]])
        else:
            p = bokeh.layouts.gridplot([[left,middle]])

        bokeh.plotting.show(p)


#        if Config.detect_environment() is not SHELL:
#            return bokeh.plotting.show(p)
#        else:
#            print("prepared plot")
#        return p

#    @staticmethod
#    def plot_to_png(model, title, searchfor: str, filename):
#        plot = Plotme.plot3(model, title, searchfor)
#        print("exporting plot...", filename)
#        export_svgs(plot, filename=filename)
