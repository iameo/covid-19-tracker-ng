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
import numpy as np



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


colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333',
    'red': '#BF0000'
}


baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

global_stat_url = "https://coronavirus-19-api.herokuapp.com/all"
ng_stat_url = 'https://coronavirus-19-api.herokuapp.com/countries'

def get_global_stat(url):    
    fetch_url = requests.get(url)
    global_stat = fetch_url.content
    global_stat = json.loads(global_stat)
    global_cases = global_stat['cases']
    global_recovered = global_stat['recovered']
    global_deaths = global_stat['deaths']
    return global_cases, global_recovered, global_deaths
  
global_cases, global_recovered, global_deaths = get_global_stat(global_stat_url)


def get_nigeria_stat(url):
    fetch_url = requests.get(url)
    global_stat = fetch_url.content
    global_stat = json.loads(global_stat)
    j = []
    for i in range(len(global_stat)):
        if global_stat[i]['country'] == 'Nigeria':
            j.append(i)
    global_stat = global_stat[j[0]]
    ng_active_cases = global_stat['active']
    ng_recovered = global_stat['recovered']
    ng_critical = global_stat['critical']
    ng_confirmed_cases = global_stat['cases']
    ng_confirmed_cases_today = global_stat['todayCases']
    ng_death_cases = global_stat['deaths']
    ng_death_cases_today = global_stat['todayDeaths']
    ng_tests = global_stat['totalTests']
    return ng_active_cases, ng_confirmed_cases, ng_confirmed_cases_today, ng_death_cases, ng_critical, ng_death_cases_today, ng_recovered, ng_tests

ng_active_cases, ng_confirmed_cases, ng_confirmed_cases_today, ng_death_cases, ng_critical, ng_death_cases_today, ng_recovered, ng_tests = get_nigeria_stat(ng_stat_url)

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


custom = '/assets/font_custom.css'
app = dash.Dash(__name__, external_stylesheets=[custom, dbc.themes.SOLAR, font_awesome_url])
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
            html.Div(id='live-update-confirmed', style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(100,140,240)','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-1',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=4, width=4),

        dbc.Col([
            html.Div(children = ["Recovered (Global)",
            html.Div(id='live-update-recovered',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(30,200,30)','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-2',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=4, width=4, style = {'text-align':'center'}),

        dbc.Col([
            html.Div(children = ["Deaths (Global)",
            html.Div(id='live-update-deaths',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'red','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-3',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=4, width=4, style = { 'text-align': 'right',
                                        'justify-content': 'right'})

    ],justify="between"),

    # dbc.Row([
    #     dbc.Col([
    #         html.P("Confirmed (Africa): "

    #         )

    #     ],sm=4),
    #     dbc.Col([
    #         html.P("Recovered (Africa): "
                
    #         )

    #     ],sm=4),
    #     dbc.Col([
    #         html.P(
    #             "Deaths (Africa): "
    #         )

    #     ],sm=4)

    # ]),
    ]),
  
  
    dbc.Container([
    # dcc.Graph(
    #     id = "country-confirmed-line"),
    #     dcc.Interval(
    #             id='interval-component-4',
    #             interval=700*10000, # in milliseconds
    #             n_intervals=0
    #             ),
 
    dcc.Graph(
        id="plot_new_metrics",
        config={ 'displayModeBar': False }
    ),
    dcc.Graph(
        id="plot_cum_metrics",
        config={ 'displayModeBar': False }
    ),
    ], style = {'padding-left':'10px', 'padding-right':'10px'}),
    
    # html.Div(dcc.Checklist(id='global_format',
    #         options=[{'label': i, 'value': i} for i in ['Africa', 'Nigeria']],
    #         value="Africa",
    #         labelStyle={'float': 'center', 'display': 'inline-block'},
    #         ), style={'textAlign': 'center',
    #             'color': colors['text'],
    #             'width': '100%',
    #             'float': 'center',
    #             'display': 'inline-block'
    #         }
    #     ),

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
            dbc.Col(["Conducted Medical Test"], xs=12, sm=12, md=12, style={'font-size':'32px', 'text-align':'center', 'font-weight':'bold', 'padding-top':'20px'}),
            ),
        dbc.Row([
        dbc.Col([
            # html.Div(children = ["Conducted Tests",
            html.Div(id='tally-tests', style = {'font-size': '32px', 'font-weight': 'bold', 'color':'lightyellow', 'text-align':'center','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-tests-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
            ),
            # ]),
            ], className='orbit-font', xs=12, sm=12, md=12, style={'font-size':'30px', 'text-align':'center', 'font-weight':'bold', 'padding-top':'8px','font-family': 'Orbitron'}),
        ]),


         dbc.Row([
        dbc.Col([
            html.Div(children = ["Confirmed (NG)",
            html.Div(id='tally-update-confirmed-ng', style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(100,140,240)','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-1-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=3, width=3),

            dbc.Col([
            html.Div(children = ["Active (NG)",
            html.Div(id='tally-update-active-ng',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'yellowgreen','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-2-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=3, width=3, style = {'text-align':'center'}),


        dbc.Col([
            html.Div(children = ["Recovered (NG)",
            html.Div(id='tally-update-recovered-ng',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(30,200,30)','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-3-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=3, width=3, style = {'text-align':'center'}),


        dbc.Col([
            html.Div(children = ["Deaths (NG)",
            html.Div(id='tally-update-deaths-ng',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'red','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-4-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=3, width=3, style = { 'text-align': 'right',
                                        'justify-content': 'right'})

    ],style = {'padding-bottom':'10px'}),

    dbc.Row(
        dbc.Col(["The Last 24H"], xs=12, sm=12, md=12, style={'font-size':'35px', 'text-align':'center', 'font-weight':'bold', 'padding-top':'20px'})),

        dbc.Row([
        dbc.Col([
            html.Div(children = ["Confirmed (NG)",
            html.Div(id='live-update-confirmed-ng', style = {'font-size': '32px', 'font-weight': 'bold', 'color':'rgb(100,140,240)','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-1a-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=6, width=6),


        dbc.Col([
            html.Div(children = ["Deaths (NG)",
            html.Div(id='live-update-deaths-ng',  style = {'font-size': '32px', 'font-weight': 'bold', 'color':'red','font-family': 'Orbitron'}),
            dcc.Interval(
                id='interval-component-4a-ng',
                interval=7000*10000, # in milliseconds
                n_intervals=0
                ),
            ]),
            ], md=6, width=6, style = { 'text-align': 'right',
                                        'justify-content': 'right'})

    ],justify="between", style = {'padding-bottom':'10px'}),


    dbc.Row(
            [
            dbc.Col([
                dcc.Dropdown(
                id='state_ng',
                options=[{'label':d, 'value':d} for d in NG_states],
                value = 'Lagos',
                ),
  
                ],sm=8, md=8),

            dbc.Col([
                html.Div(id='state_output'),
                ], sm = 4, md=4,
                ),
            ], style = {'padding-top':'10px'}),
        ]),

    html.Hr(),


    dbc.Container([
    dbc.Row([ 
 
            dbc.Col(children = ["NCDC EMERGENCY LINES    ",
            dcc.Markdown('''
  
            [0800-9700-0010](tel:080097000010) & [+234-708-7110839](tel:+2347087110839)
                '''),
             ], xs=12),
    ]),
        

    dbc.Row([ 
            dbc.Col(
                [  
                    dcc.Markdown("[EMMANUEL](https://www.twitter.com/__oemmanuel__)", style={'text-decoration': 'none',
                                                                            'cursor': 'grab',                                                  'color': 'whitesmoke',
                                                                            'font-weight': 'bold'}),
                ], xs=6),

            dbc.Col(
                [
                    dcc.Markdown(
                    "Resources: [JHU DATA](https://github.com/CSSEGISandData/COVID-19)|[NCDC](https://ncdc.gov.ng/)|[Ploner](https://github.com/ploner/coronavirus-py)", style = {'textAlign': 'right'}),
                    ], xs=6, 
                ),

    ]),
    ]),

    ])


# country_group = allData.groupby(by='Country/Region')

# data_reg = []
# xx = []
# yy = []
# colors=['red', 'blue', 'green']

# for group, dataframe in country_group:
#     dataframe = dataframe.sort_values(by=['date'])
#     trace = go.Scatter(x=dataframe.date.tolist(), 
#                        y=dataframe.CumConfirmed.tolist(),
#                     #    marker=dict(color=colors[len(data_reg)]),
#                        name=group)
#     xx.append(dataframe.date)
#     yy.append(dataframe.CumConfirmed)
#     data_reg.append(trace)


# def line_graph():
#     figure = go.Figure(data=[
#         go.Bar( 
#             x=xx, y=yy,
#             marker_line_color='rgb(0,0,0)', marker_line_width=1,
#             # marker_color={ 'Deaths':'rgb(200,30,30)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,140,240)'}[metric]
#         )
#     ])
#     figure.update_layout( 
#               barmode='group', legend=dict(x=.05, y=0.95), 
#               plot_bgcolor='whitesmoke', font=tickFont) \
#           .update_xaxes( 
#               title="", tickangle=-90, showgrid=True, gridcolor='#DDDDDD', 
#               tickfont=tickFont, ticktext=xx, tickvals=xx) \
#           .update_yaxes(
#              showgrid=True, gridcolor='#DDDDDD')
#     return figure



# @app.callback(
#     Output('trajectory', 'figure'),
#     [Input('global_format', 'value')])
# def trajectory(view, date_index):
#     if view == 'Africa':
#         df = african_data
#         scope = 'countries'
#         threshold = 1000
#     elif view == 'Nigeria':
#         df = african_data[african_data['Country/Region'] == 'Nigeria']
#         df = df.drop('Country/Region', axis=1)
#         df = df.rename(columns={'Province/State': 'Country/Region'})
#         scope = 'states'
#         threshold = 1000
#     else:
#         df = african_data
#         scope = 'countries'
#         threshold = 1000

#     date = african_data['date'].unique()[date_index]

#     df = df.groupby(['date', 'Country/Region'], as_index=False)['Confirmed'].sum()
#     df['previous_week'] = df.groupby(['Country/Region'])['Confirmed'].shift(7, fill_value=0)
#     df['new_cases'] = df['Confirmed'] - df['previous_week']
#     data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
#     newCases = data.select_dtypes(include='Int64').diff().fillna(0)
#     newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
#     newCases.to_csv("neww.csv", index=False)
#     data = data.join(newCases)
#     data.to_csv("neww2.csv", index=False)
#     xmax = np.log(1.25 * df['Confirmed'].max()) / np.log(10)
#     xmin = np.log(threshold) / np.log(10)
#     ymax = np.log(1.25 * df['new_cases'].max()) / np.log(10)
#     ymin = np.log(.8 * df[df['Confirmed'] >= threshold]['new_cases'].min()) / np.log(10)

#     countries_full = df.groupby(by='Country/Region', as_index=False)['Confirmed'].max().sort_values(by='Confirmed', ascending=False)['Country/Region'].to_list()
    
#     df = df[df['date'] <= date]

#     countries = df.groupby(by='Country/Region', as_index=False)['Confirmed'].max().sort_values(by='Confirmed', ascending=False)
#     countries = countries[countries['Confirmed'] > threshold]['Country/Region'].to_list()
#     countries = [country for country in countries_full if country in countries]

#     traces = []

#     for country in countries:
#         filtered_df = df[df['Country/Region'] == country].reset_index()
#         idx = filtered_df['Confirmed'].sub(threshold).gt(0).idxmax()
#         trace_data = filtered_df[idx:]
#         trace_data['date'] = pd.to_datetime(trace_data['date'])
#         trace_data['date'] = trace_data['date'].dt.strftime('%b %d, %Y')

#         traces.append(
#             go.Scatter(
#                     x=trace_data['Confirmed'],
#                     y=trace_data['new_cases'],
#                     mode='lines',
#                     name=country,
#                     text=trace_data['date'],
#                     hoverinfo='x+text+name')
#         )

#     return {
#         'data': traces,
#         'layout': go.Layout(
#                 title='Trajectory of Cases<br>({} with greater than {} confirmed cases)'.format(scope, threshold),
#                 xaxis_type="log",
#                 yaxis_type="log",
#                 xaxis_title='Total Confirmed Cases',
#                 yaxis_title='New Confirmed Cases (in the past week)',
#                 font=dict(color=colors['text']),
#                 paper_bgcolor=colors['background'],
#                 plot_bgcolor=colors['background'],
#                 xaxis=dict(gridcolor=colors['grid'],
#                            range=[xmin, xmax]),
#                 yaxis=dict(gridcolor=colors['grid'],
#                            range=[ymin, ymax]),
#                 hovermode='closest',
#                 showlegend=True
#             )
#         }


# @app.callback(
#     Output('country-confirmed-line', 'figure'), 
#     [Input('interval-component-4', 'n_intervals')]
# )
# def update_line(n):
#     return line_graph()




def nonreactive_data(country):
    data = african_data.loc[african_data['Country/Region'] == country] \
                  .drop('Country/Region', axis=1)
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
            marker_line_color='rgb(0,0,0)', marker_line_width=1.1,
            marker_color={ 'Deaths':'rgb(200,30,30)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,140,240)'}[metric]
        ) for metric in metrics
    ])
    figure.update_layout( 
              barmode='group', legend=dict(x=.05, y=0.95), 
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes( 
              title="Date", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
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

#global
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



#NG-tally
@app.callback(
    Output('tally-tests', 'children'),
    [Input('interval-component-tests-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_tests


@app.callback(
    Output('tally-update-confirmed-ng', 'children'),
    [Input('interval-component-1-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_confirmed_cases

@app.callback(
    Output('tally-update-active-ng', 'children'),
    [Input('interval-component-2-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_active_cases


@app.callback(
    Output('tally-update-recovered-ng', 'children'),
    [Input('interval-component-3-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_recovered

@app.callback(
    Output('tally-update-deaths-ng', 'children'),
    [Input('interval-component-4-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_death_cases


#NG-Live
@app.callback(
    Output('live-update-confirmed-ng', 'children'),
    [Input('interval-component-1a-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_confirmed_cases_today

@app.callback(
    Output('live-update-active-ng', 'children'),
    [Input('interval-component-2a-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_active_cases


@app.callback(
    Output('live-update-recovered-ng', 'children'),
    [Input('interval-component-3a-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_recovered


@app.callback(
    Output('live-update-deaths-ng', 'children'),
    [Input('interval-component-4a-ng', 'n_intervals')]
)
def fetch_confirmed_cases(n):
    return ng_death_cases_today




if __name__ == '__main__':
    app.run_server(debug=False)