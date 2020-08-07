# importing required python packages
import os
import pandas as pd
import numpy as np
from datetime import datetime
import random
import plotly.graph_objects as go
#import plotly
import dash
print('Your current dash board version is:' + dash.__version__)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

#importing data frame
df_analyse=pd.read_csv('C:/Users/dhame/ds_covid-19/data/processed/SIR_fitted.csv',sep=';')
df_analyse.sort_values('Date',ascending=True).head()
df_analyse = df_analyse.reset_index(drop = True)
df_data = df_analyse[35:] #Need to be careful here because it difffers from each country!!

# for showing same color for each countries both curve, and color will be random at when you update the color list
color_list = []
for i in range(200):
    var = '#%02x%02x%02x'%(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    color_list.append(var)

# creating dashboard app containig plotting for whole dataset
fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''

    #  Data Science Project @ TU_KL on COVID-19 Dataset-Part 2
    ## Real and simulated number of infected people

    * The default layout contains the confirmed infected cases in the log-scale format on the Y-axis
    and Timeline in Days on the X-axis.
    ### The dropdown menu enables selection of one or multiple countries for visualization.

    * This dashboard plots two curves for each country:

    1. The first curve represents the confirmed infected cases along the timeline.
    2. The second curve represents the simulated infected cases after applying the SIR model along the timeline.

    '''),

    dcc.Markdown('''
    ## Multi-Select Country for visualization
    '''),
    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in df_data.columns[1:200]],
        value=['Germany','India'], # which are pre-selected
        multi=True),dcc.Graph(figure=fig, id='main_window_slope')])

@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value')])
def update_figure_layout(country_list):
    v = 0
    my_yaxis={'type':"log",'title':'Confirmed infected people (From johns hopkins csse, log-scale)'}
    traces = []
    for each in country_list:
        traces.append(dict(x=df_data['Date'],y=df_data[each],
                                mode='line', line = dict(color = color_list[v]), opacity=1.0,name=each))
        traces.append(dict(x=df_data['Date'],
                                y=df_data[each+'_fitted'],
                                mode='markers+lines',line = dict(color=color_list[v]), opacity=1.0,name=each+'_simulated'))

        v = v+1
    return {
            'data': traces,
            'layout': dict (
                width=1000,height=650,
                xaxis={'title':'Timeline','tickangle':-45,'nticks':20,
                'tickfont':dict(size=14,color="#0c6887"),},yaxis=my_yaxis)}

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
