# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import requests
import json

import pandas as pd




African_countries = [
    "Algeria", "Angola", "Benin", "Botswana","Burkina Faso", "Burundi", "Cabo Verde",
    "Cameroon", "Central African Republic (CAR)", "Chad", "Comoros", "Congo, Democratic Republic of the Congo", "Republic of the Cote d'Ivoire",
    "Djibouti","Egypt", "Equatorial Guinea", "Eritrea", "Eswatini (formerly Swaziland)","Ethiopia", "Gabon",
    "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
    "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria",
    "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa",
    "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"                 
            ]

NG_states = [
    "Abuja FCT", "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi","Bayelsa",
    "Benue","Borno","Cross River","Delta", "Ebonyi","Enugu","Edo","Ekiti","Gombe",
    "Imo","Jigawa","Kaduna","Kano","Katsina","Kebbi","Kogi","Kwara","Lagos","Nasarawa",
    "Niger","Ogun","Ondo","Osun","Oyo","Plateau","Rivers","Sokoto","Taraba","Yobe", "Zamfara",
    ]    




baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

global_stat_url = "https://coronavirus-19-api.herokuapp.com/all"


def get_global_stat(url):    
    fetch_url = requests.get(url)
    global_stat = fetch_url.content
    global_stat = json.loads(global_stat)
    global_cases = global_stat['cases']
    global_recovered = global_stat['recovered']
    global_deaths = global_stat['deaths']
    return global_cases, global_recovered, global_deaths
  
global_cases, global_recovered, global_deaths = get_global_stat(global_stat_url)

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

def loadData(fileName, columnName): 
    data = pd.read_csv(baseURL + fileName) \
             .drop(['Lat', 'Long'], axis=1) \
             .melt(id_vars=['Province/State', 'Country/Region'], var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'}, errors='ignore')
    data['Province/State'].fillna('<all>', inplace=True)
    data[columnName].fillna(0, inplace=True)
    return data

allData = loadData("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
    .merge(loadData("time_series_covid19_deaths_global.csv", "CumDeaths")) \
    .merge(loadData("time_series_covid19_recovered_global.csv", "CumRecovered"))

# allData.to_csv("alldata.csv", index=False)

# world_data = allData["Country/Region"].unique()
# world_data.sort()

african_data = allData[allData["Country/Region"].isin(African_countries)]
afri_countries = african_data['Country/Region'].unique()
afri_countries.sort()
font_awesome_url = 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR, font_awesome_url])
server = app.server
app.config.suppress_callback_exceptions=True
app.title = 'COVID-19 TRACKER (AFRICA)'

app.config.update({
     'routes_pathname_prefix': '',
     'requests_pathname_prefix': '',
})



app.layout = html.Div(
    [
        dbc.Container([
        html.H1('DOCUMENTED COVID-19 CASES IN AFRICA', className = "text-center"),
        html.P("(A possible 1-day delay in data transmission. If you're in Nigeria, check the last graph for more visuals)", className = "text-center"),
        
        dbc.Row([
                dbc.Col(
                    [
                        html.H5('Country'),
                        dcc.Dropdown(
                        id='country',
                        options=[{'label':c, 'value':c} for c in afri_countries],
                        value='Nigeria'
                        ),
                    ], width=6, sm=6, md=6,
                    ),
                dbc.Col(
                    [
                        html.H5('Data Metrics'),
                        dbc.Checklist(
                        id='metrics',
                        options=[{'label':m, 'value':m} for m in ['Confirmed', 'Recovered', 'Deaths']],
                        value=['Confirmed', 'Recovered']
                        )
                    ], width=6, sm=6, md=6,

                    ),# style={ 'font-family':"Courier New, monospace" },
                    
                ],justify="between"), #container
         
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div(children = ["Confirmed (Global)",
            html.Div(id='live-update-confirmed', style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(100,140,240)'}),
            dcc.Interval(
                id='interval-component-1',
                interval=1*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=4, width=4),

        dbc.Col([
            html.Div(children = ["Recovered (Global)",
            html.Div(id='live-update-recovered',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(30,200,30)'}),
            dcc.Interval(
                id='interval-component-2',
                interval=1*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=4, width=4, style = {'text-align':'center'}),

        dbc.Col([
            html.Div(children = ["Deaths (Global)",
            html.Div(id='live-update-deaths',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'red'}),
            dcc.Interval(
                id='interval-component-3',
                interval=1*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=4, width=4, style = { 'text-align': 'right',
                                        'justify-content': 'right'})

    ],justify="between"),

    dbc.Row([
        dbc.Col([
            html.P("Confirmed (Africa): "

            )

        ],sm=4),
        dbc.Col([
            html.P("Recovered (Africa): "
                
            )

        ],sm=4),
        dbc.Col([
            html.P(
                "Deaths (Africa): "
            )

        ],sm=4)

    ]),
    ]),
  
  
    dbc.Container([
    dcc.Graph(
        id="plot_new_metrics",
        config={ 'displayModeBar': False }
    ),
    dcc.Graph(
        id="plot_cum_metrics",
        config={ 'displayModeBar': False }
    ),
    ], style = {'padding-left':'10px', 'padding-right':'10px'}),

    html.Br(),
    
    dbc.Container([
    dbc.Alert(
        [
            "This section is reserved for Nigeria. ", 
            html.A("click here to view general data", href="#", className="alert-link"),
            ],
            color="primary", style = {'textAlign': "center", 'text-align':'center'}
        ),

    dbc.Row(
            [
            dbc.Col([
                dcc.Dropdown(
                id='state_ng',
                options=[{'label':d, 'value':d} for d in NG_states],
                value = 'Lagos',
                ),
  
                ], md=6),

            dbc.Col([
                html.Div(id='state_output'),
                ], md=6,
                ),
            ]),
        ]),
        html.Hr(),


    dbc.Container([
    dbc.Row([ 
            dbc.Col(
                [  
                    dcc.Markdown("[EMMANUEL](https://www.twitter.com/__oemmanuel__)", style={'text-decoration': 'none',
                                                                            'cursor': 'grab',
                                                                            'color': 'whitesmoke',
                                                                            'font-weight': 'bold'}),
                ], xs=6),

            dbc.Col(
                [
                    dcc.Markdown(
                    "Resources: [JHU DATA](https://github.com/CSSEGISandData/COVID-19)|[NCDC](https://ncdc.gov.ng/)|[Ploner](https://github.com/ploner/coronavirus-py)", style = {'textAlign': 'right'}),
                    ], xs=6, 
                    # style = {'textAlign':'right'},
                ),

    ]),
    ]),

    ])




def nonreactive_data(country):
    data = african_data.loc[african_data['Country/Region'] == country] \
                  .drop('Country/Region', axis=1)
    # if state == '<all>':
    #     data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
    # else:
    data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
    newCases = data.select_dtypes(include='Int64').diff().fillna(0)
    newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
    data = data.join(newCases)
    data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
    return data

def barchart(data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure(data=[
        go.Bar( 
            name=metric, x=data.date, y=data[prefix + metric],
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color={ 'Deaths':'rgb(200,30,30)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,140,240)'}[metric]
        ) for metric in metrics
    ])
    figure.update_layout( 
              barmode='group', legend=dict(x=.05, y=0.95), 
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes( 
              title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
              tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure

@app.callback(
    Output('plot_new_metrics', 'figure'), 
    [Input('country', 'value'), Input('metrics', 'value')]
)
def update_plot_new_metrics(country, metrics):
    data = nonreactive_data(country)
    return barchart(data, metrics, prefix="New", yaxisTitle="New Cases per Day")

@app.callback(
    Output('plot_cum_metrics', 'figure'), 
    [Input('country', 'value'), Input('metrics', 'value')]
)
def update_plot_cum_metrics(country, metrics):
    data = nonreactive_data(country)
    return barchart(data, metrics, prefix="Cum", yaxisTitle="Cumulated Cases")


@app.callback(
    Output(component_id='state_output', component_property='children'),
    [Input('state_ng', 'value')]
)
def update_output_div(input_value):
    if input_value == "Lagos":
        return 'Extracting data and making plots for "{}" '.format(input_value), "(Èkó ò ní bàjé oooooo!)"
    return 'Extracting data and making plots for "{}"'.format(input_value)


@app.callback(
    Output('live-update-confirmed', 'children'),
    [Input('interval-component-1', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return global_cases

@app.callback(
    Output('live-update-recovered', 'children'),
    [Input('interval-component-2', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return global_recovered

@app.callback(
    Output('live-update-deaths', 'children'),
    [Input('interval-component-3', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return global_deaths






if __name__ == '__main__':
    app.run_server(debug=False)