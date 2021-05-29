import json
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import time
import numpy as np
import requests
import flask
from dateutil import relativedelta
from mongo_connect import DB
from dash import Dash
from dash.dependencies import Input, Output, State
from post_end_point import server
from update_crawl_attribute import update_crawl_period_handler, update_crawl_time_handler
from datetime import datetime as dt, timedelta
from urllib.request import Request, urlopen

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(
    __name__,
    server=server,
    url_base_pathname='/index/',
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}
def get_topic_id():
    options = [{'label': 'All Topic', 'value': 'All Topic'}]

    for x in DB.topic.find({}, {"_id": 0, "topic_id":1}):
        topic = x["topic_id"]
        options.append({'label': topic, 'value': topic})
    return options, options[1:]

def form_pipe_line(start_date, end_date, grouped_by_type, topic_id):
    
    keys = {"created_date": {"$gt": start_date, "$lt": end_date}}

    keys["is_updated"] = True
    if topic_id != "All Topic":
        keys["topic_id"] = int(topic_id)

    group = {}

    if grouped_by_type == 'MONTH':
        group = {
        "month": { "$month": "$created_date" },
        "year": { "$year": "$created_date" },
        "model": "$predict.model"
        }
    elif grouped_by_type == 'YEAR':
        group = {
        "year": { "$year": "$created_date" },
        "model": "$predict.model"
        }
    else:
        group = {
        "month": { "$month": "$created_date" },
        "year": { "$year": "$created_date" },
        "date": {"$dayOfMonth": "$created_date"},
        "model": "$predict.model"
        }

    pipe_line = [{
            "$match": keys,
        },
        {
            "$unwind": "$predict"
        },
        {
            "$group": {
                "_id": group,
                "true_positive": {
                    "$sum": {"$cond": [ {"$and": [{"$eq": ["$true_label", True]}, {"$eq":["$predict.label", True]}]}, 1, 0 ]}
                },
                "false_positive": {
                    "$sum": {"$cond": [ {"$and": [{"$eq": ["$true_label", True]}, {"$eq":["$predict.label", False]}]}, 1, 0 ]}
                },
                "false_negative": {
                    "$sum": {"$cond": [ {"$and": [{"$eq": ["$true_label", False]}, {"$eq":["$predict.label", True]}]}, 1, 0 ]}
                },
                "created_date": {"$min": "$created_date"}
        }
    }]
    return pipe_line
def form_dataframe(data, grouped_by_type):

    if grouped_by_type == 'MONTH':
        prensent_func = lambda x: dt(year=x.year,month=x.month,day=1)
    elif grouped_by_type == 'YEAR':
        prensent_func = lambda x: dt(year=x.year,month=1,day=1)
    else:
        prensent_func = lambda x: dt(x.year,x.month,x.day)

    df = pd.DataFrame(data=data)
    if df.empty:
        return df
    df["model"] = list(map(lambda x: x.get("model", "None"), df["_id"]))
    df = df[df["model"] != "None"]
    df["precision"] = df["true_positive"] / (df["true_positive"] + df["false_positive"])
    df["recall"] = df["true_positive"] / (df["true_positive"] + df["false_negative"])
    df["created_date"] = list(map(prensent_func, df['created_date']))
    df = df.fillna(0)[["precision", "recall", "created_date", "model"]]
    df=df.sort_values(by=["created_date"])
    return df

def form_layout(start_date, end_date, grouped_by_type, topic_id="All Topic"):

    pipe_line = form_pipe_line(start_date, end_date, grouped_by_type, topic_id)
    temp = DB.mention.aggregate(pipe_line)

    layout = []
    df = form_dataframe(temp, grouped_by_type)
    if df.empty:
        return layout
    grouped_df = df.groupby(df["model"])
    
    for name, df in grouped_df:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["precision"],
                            mode='lines',
                            name='precision'))
        fig.add_trace(go.Scatter(x=df["created_date"], y=df["recall"],
                            mode='lines',
                            name='recall'))

        fig.update_layout(
            font_color=colors['text'],
            title="Precision and Recall of Model {}".format(name),
            xaxis_title="Timeline",
            yaxis=dict(range=[0,1])
        )
        layout.append(dcc.Graph(
            id='graph_of_model_{}'.format(name),
            figure=fig
        ))

    return layout

form = html.Div(children =[
    html.Div([
        dcc.Dropdown(
            id='demo-dropdown',
            options=get_topic_id()[0],
            value = "All Topic",
        )
    ],
    style={'width': '19%', 'margin': 'auto','align-content':'center'}
    ),
    html.Div([
        dcc.RadioItems(
            options=[
                {'label': 'Date', 'value': 'DATE'},
                {'label': 'Month', 'value': 'MONTH'},
                {'label': 'Year', 'value': 'YEAR'}
            ],
            value='DATE',
            labelStyle={'display': 'inline-block', 'vertical-align': 'middle', 'margin-right': '10px'},
            inputStyle={'vertical-align': 'middle'},
            id='data-radio-items'
        ),
    ],
        style={ 'margin': 'auto', 'align-content':'center'}
    ),

    html.Div([
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=dt(1995, 8, 5),
            max_date_allowed=dt.now()+timedelta(1),
            initial_visible_month=dt.now(),
            display_format='DD/MM/YYYY',
            start_date=dt.now()-timedelta(1),
            end_date=dt.now()
        ),
    ],
        style={ 'margin': 'auto', 'align-content':'center'}
    ),
    dbc.Button('Submit',
        id='button',
        style={ 'margin': 'auto', 'align-content':'center'},
        n_clicks=0),

], style={'display': 'flex', 'flex-flow': 'row wrap', 'align-items': 'center'})

tab1_content = dbc.Card(
    dbc.CardBody([
        form,
        html.Div(id="layout",
            children = form_layout(dt.now()-timedelta(1), dt.now()+timedelta(1), "DATE")
        )
    ]),
    className="mt-3",
)


tab2_content = dbc.Card(
    dbc.CardBody([
        html.Div([
            html.Div([
                dcc.RadioItems(
                    options=[
                        {'label': 'Update Crawl Period', 'value': 'P'},
                        {'label': 'Update Crawl Timepoint', 'value': 'TP'},
                    ],
                    labelStyle={'display': 'inline-block', 'vertical-align': 'middle', 'margin-right': '10px'},
                    inputStyle={'vertical-align': 'middle'},
                    id='update-radio-items'
                )
            ]),
            html.Div(id="update-content", children=[])
        ])
    ]),
    className="mt-3",
)

def form_topic_crawl_period_element(topic_id, crawl_period):
    div_tag = html.Div([
        html.Div([
            'Topic {} Crawl Period'.format(topic_id),
            dcc.Input(
                id="input-range-{}".format(topic_id),
                type="number",
                min=1,
                value=crawl_period,
                style={ 'width': '29%', 'margin': 'auto', 'align-content':'center'}
            ),
            html.Div([
                dcc.Dropdown(
                    id='time-option-{}'.format(topic_id),
                    options=[
                        {'label': 'second(s)', 'value': 'SECOND'},
                        {'label': 'minute(s)', 'value': 'MINUTE'},
                        {'label': 'hour(s)', 'value': 'HOUR'},
                        {'label': 'day(s)', 'value': 'DAY'}
                    ],
                    value="SECOND",
                )
                ],
                style={ 'width': '9%', 'margin': 'auto', 'align-content':'center'}
            ),
            dbc.Button('Update',
                id='update-period-button-{}'.format(topic_id),
                style={ 'margin': 'auto', 'align-content':'center'},
                n_clicks=0),
        ], style={'display': 'flex', 'flex-flow': 'row wrap', 'align-items': 'center', 'margin-bottom': '10px'}), 
        dbc.Alert(
            children=[],
            id="alert-period-auto-{}".format(topic_id),
            is_open=False,
            duration=4000,
        )
    ])
    return div_tag

def form_topic_crawl_time_element(topic_id, time):
    div_tag = html.Div([
        html.Div([
            'Topic {} Next Crawl At'.format(topic_id),
            dcc.DatePickerSingle(
                id='date-picker-single-{}'.format(topic_id),
                min_date_allowed=dt(1995, 8, 5),
                initial_visible_month=dt.now(),
                display_format='DD/MM/YYYY',
                date=time,
                style={'margin': 'auto', 'align-content':'center'}
            ),
            html.Div([
                dcc.Input(
                    id="input-hour-range-{}".format(topic_id),
                    type="number",
                    min=0, max=23,
                    value=time.hour,
                    style={'width':'49%','margin': 'auto', 'align-content':'center'}
                ),
                ':',
                dcc.Input(
                    id="input-minute-range-{}".format(topic_id),
                    type="number",
                    min=0, max=59,
                    value=time.minute,
                    style={'width':'49%','margin': 'auto', 'align-content':'center'}
                ),
            ],style={'width':'19%', 'display': 'flex', 'flex-flow': 'row wrap', 'align-items': 'center'}),

            dbc.Button('Update',
                id='update-time-button-{}'.format(topic_id),
                style={ 'margin': 'auto', 'align-content':'center'},
                n_clicks=0)
        ],
        style={'display': 'flex', 'flex-flow': 'row wrap', 'align-items': 'center', 'margin-bottom': '10px'}),
        dbc.Alert(
            children=[],
            id="alert-time-auto-{}".format(topic_id),
            is_open=False,
            duration=4000,
        )
    ])
    return div_tag

@app.callback(
    Output('update-content', 'children'),
    [Input('update-radio-items', 'value')]
)
def show_crawl_type(update_type):
    
    topic_lists = DB.topic.find({}, {"_id": 0})
    
    if update_type == 'P':
        update_crawl_period_content = []
        for topic in topic_lists:
            update_crawl_period_content.append(
                form_topic_crawl_period_element(topic["topic_id"], topic["crawl_period"] )
            )
        return update_crawl_period_content
    elif update_type == 'TP':
        update_crawl_timepoint_content = []
        for topic in topic_lists:
            update_crawl_timepoint_content.append(
                form_topic_crawl_time_element(topic["topic_id"], topic["next_crawl_at"] )
            )
        return update_crawl_timepoint_content
    else:
        return []


app.layout = html.Div(style={'backgroundColor': colors['background']},
    children=[
        html.H1(
            children='Spam Monitor System',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        
        dcc.Tabs([
            dcc.Tab(tab1_content, label="Chart"),
            dcc.Tab(tab2_content, label="Modify Crawl Period/Timepoint"),
        ]),
        
    ])

@app.callback(
    Output('layout', 'children'),
    [Input('button', 'n_clicks')],
    state=[State('data-radio-items', 'value'),
    State('demo-dropdown', 'value'),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date'),])
def update_graph(n,  grouped_by_type, topic_id,
                 start_date, end_date):
    if n > 0:
        print("{} {} {}".format(grouped_by_type, start_date, end_date))

        start_date = dt.fromisoformat(start_date)
        end_date = dt.fromisoformat(end_date) + timedelta(1)

        layout = form_layout(start_date,end_date,grouped_by_type,topic_id)
        return layout
    else: return []

for topic in DB.topic.find({}, {"_id": 0}):
# n0_time_clicks = 0
    @app.callback(
        [Output("alert-time-auto-{}".format(topic["topic_id"]), "is_open"),
        Output("alert-time-auto-{}".format(topic["topic_id"]), "children")],
        [Input("update-time-button-{}".format(topic["topic_id"]), "n_clicks")],
        [State('input-hour-range-{}'.format(topic["topic_id"]), 'value'),
        State('input-minute-range-{}'.format(topic["topic_id"]), 'value'),
        State('date-picker-single-{}'.format(topic["topic_id"]), 'date'),
        State("alert-time-auto-{}".format(topic["topic_id"]), "is_open"),
        State("alert-time-auto-{}".format(topic["topic_id"]), "children")]
    )
    def toggle_crawl_timepoint_alert(n, hour, minute, date, is_open, body, topic=topic["topic_id"]):
        if n > 0:
            print("{} {} {}".format(date, hour, minute))
            date = dt.fromisoformat(date)
            time_n_date = date.replace(hour=hour, minute=minute)
            data = {
                "topic_id": int(topic),
                "new_time_point": time_n_date.isoformat()
            }
            response = update_crawl_time_handler(DB, data)
            #print(response)
            return True, json.dumps(response)
        else: return False, " "

    @app.callback(
        [Output("alert-period-auto-{}".format(topic["topic_id"]), "is_open"),
        Output("alert-period-auto-{}".format(topic["topic_id"]), "children")],
        [Input("update-period-button-{}".format(topic["topic_id"]), "n_clicks")],
        [State('input-range-{}'.format(topic["topic_id"]), 'value'),
        State('time-option-{}'.format(topic["topic_id"]), 'value'),
        State("alert-period-auto-{}".format(topic["topic_id"]), "is_open"),
        State("alert-period-auto-{}".format(topic["topic_id"]), "children")],
    )
    def toggle_crawl_period_alert(n, time, unit, is_open, body, topic=topic["topic_id"]):
        if n > 0:
            if unit == 'MINUTE':
                time = time*60
            elif unit == 'HOUR':
                time = time*60*60
            elif unit == 'DAY':
                time = time*60*60*24
            print("{} {} {}".format(time, unit, topic))

            data = {
                "topic_id": int(topic),
                "new_crawl_period": int(time)
            }
            response = update_crawl_period_handler(DB, data)
            #print(response)
            return True, json.dumps(response)
        else: return False, " "
    
@server.route('/')
@server.route('/index')
def index():
    return app.index()

