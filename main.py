# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 20:28:45 2020

@author: InvictaeGuy
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from attparser.attparser import Parser
from attparser.attmodel import Converter, Loader

url = 'http://www.emii.ru'

domen1, domen2 = Converter.convert(url)
keyword = domen2
coef, df, pr = Parser.getPopular(domen2)
wordscount, pagescount, content, text = Parser.getContent(url, domen2, 'ru')
att = Parser.getAttendance(url)
spam, water, dist = Parser.getIndexing(content, text)
print(att)
print(wordscount, pagescount, spam, coef, water, att, domen1, domen2)

Loader.load_to_DB(wordscount, pagescount, spam, coef, water, att, domen1, domen2)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {'background': '#111111','text': '#7FDBFF'}
app.layout = html.Div(children=[
    html.H1(children='Attendance Predictor', style={'textAlign': 'center'}),

    html.Div(children='''Predict the attendance of any site with modern algorytmes.''', 
             style={'textAlign': 'center'}),
             dcc.Graph(id='1', figure={'data': [{'x': df['date'], 
                                                 'y': df[keyword], 
                                                 'type': 'scatter', 
                                                 'name': keyword + ' queries'}],
                                       'layout': {'title': 'Popularity of "' + keyword + '" visualization'}}),

             dcc.Graph(id='2', figure={'data': [{'x': [x[0] for x in dist.most_common(50)], 
                                                 'y': [x[1] for x in dist.most_common(50)], 
                                                 'type': 'bar', 
                                                 'name': keyword + ''}],
                                       'layout': {'title': 'Word distribution'}}),
            
             dcc.Graph(id='3', figure={'data': [{'x': [xx for xx in range(1, 7)],
                                                 'y': att,
                                                 'type': 'scatter',
                                                 'name': 'Attendance of ' + keyword}],
                                       'layout': {'title': 'Attendance'}})])

if __name__ == '__main__':
    app.run_server(debug=False)










