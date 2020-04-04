


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc



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

external_stylesheets = [
{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}
]

baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

def loadData(fileName, columnName): 
    data = pd.read_csv(baseURL + fileName) \
             .drop(['Lat', 'Long'], axis=1) \
             .melt(id_vars=['Province/State', 'Country/Region'], var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'}, errors='ignore')
    data['Province/State'].fillna('<all>', inplace=True)
    data[columnName].fillna(0, inplace=True)
    # data.to_csv("bleh.csv")
    return data

allData = loadData("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
    .merge(loadData("time_series_covid19_deaths_global.csv", "CumDeaths")) \
    .merge(loadData("time_series_covid19_recovered_global.csv", "CumRecovered"))

african_data = allData[allData["Country/Region"].isin(African_countries)]
countries = african_data['Country/Region'].unique()
countries.sort()

resources_credit = dcc.Link()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR, external_stylesheets])




# footer = dbc.Row(
#     dbc.Col(),
#     dbc.Col(
#         dbc.Button("Toggle fade", id="fade-transition-button"),
#         dbc.Fade()
#     )
# )
app.layout = dbc.Container(
    [
        html.H1('Documented COVID-19 Cases in Africa.'),
        html.P("(A possible 1-day delay in data transmission. If you're in Nigeria, check the last graph for more visuals)"),

        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5('Country'),
                        dcc.Dropdown(
                        id='country',
                        options=[{'label':c, 'value':c} for c in countries],
                        value='Nigeria'
            ),
                    ], md=8,
                ),

                # dbc.Col(
                #     [
                #         html.H5('State'),
                #         dcc.Dropdown(
                #             id='state'
                #         )
                #     ], md=4,
                # ),

                dbc.Col(
                    [
                        html.H5('Data Metrics'),
                        dbc.Checklist(
                        id='metrics',
                        options=[{'label':m, 'value':m} for m in ['Confirmed', 'Recovered', 'Deaths']],
                        value=['Confirmed', 'Recovered']
            )
                    ], md=4,

                ),# style={ 'font-family':"Courier New, monospace" },
            ]),

    dcc.Graph(
        id="plot_new_metrics",
        config={ 'displayModeBar': False }
    ),
    dcc.Graph(
        id="plot_cum_metrics",
        config={ 'displayModeBar': False }
    ),
    html.Br(),
    dbc.Alert(
        [
            "This section is reserved for Nigeria. ",
            html.A("click here to view general data", href="#", className="alert-link"),
            ],
            color="primary",
        ),

    dbc.Row([
            # dbc.Col(
            #     [
            #         html.H6('Country'),
            #         dcc.Dropdown(
            #         id='country_ng',
            #         options=[{'label':c, 'value':c} for c in [{'label':"Nigeria", 'value':"NG"]],
            #         value='Nigeria'
            # ),
            #     ], md=6,
            # ),
        
            dbc.Col(
                 [
                    dcc.Dropdown(
                    id='state_ng',
                    options=[{'label':d, 'value':d} for d in NG_states],
                    value = 'Lagos',
                    ),
                    html.Div(id='divv'),
                    ], md=6,
                    
                ),
    ]),
    html.Hr(),

    dbc.Row([
    #     dbc.Col(children=[
    #         html.P(children=["Made with ",html.I(className='fa fa-heart',  style = {'color':'red'}),html.P(" by Emmanuel")]),
    #         html.Div(" by Emmanuel"),
    # ]
            
    #     ),  
            dbc.Col(
                [
                    html.H6('Made With love by Emmanuel'),
   
                    ], md=8,
                ),
            dbc.Col(
                [
                    html.P('Resources | Credit'),
                        dcc.Dropdown(
                        id='resources_credit',
                        options=[{'label':c, 'value':c} for c in resources_credit],
                        value='NCDC'
            ),
            
                    ], md=4,
                ),


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
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
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
    Output(component_id='divv', component_property='children'),
    [Input('state_ng', 'value')]
)
def update_output_div(input_value):
    if input_value == "Lagos":
        return 'Extracting data and making plots for "{}" '.format(input_value), "(Eko o ni baje o)"
    return 'Extracting data and making plots for "{}"'.format(input_value)
    # else:
    #     state_options = [{'label':"Not Defined", 'value':"N/A"}]
    #     state_value = state_options[0]['value']
    #     return state_options, state_value
    # return

# def update_states():
#     states = list(NG_states)
#     states.insert(0, '<all>')
#     states.sort()
#     state_options = [{'label':s, 'value':s} for s in states]
#     state_value = state_options[0]['value']
#     return state_options, state_value



# @app.callback(
#     Output('plot_new_metrics', 'figure'), 
#     [Input('resources_credit', 'value')]
# )
server = app.server




if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)




# body = dbc.Container(
#     [
#        dbc.Row(
#            [
#                dbc.Col(
#                   [
#                      html.H2("Heading"),
#                      html.P(
#                          """\
# Donec id elit non mi porta gravida at eget metus.Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentumnibh, ut fermentum massa justo sit amet risus. Etiam porta semmalesuada magna mollis euismod. Donec sed odio dui. Donec id elit nonmi porta gravida at eget metus. Fusce dapibus, tellus ac cursuscommodo, tortor mauris condimentum nibh, ut fermentum massa justo sitamet risus. Etiam porta sem malesuada magna mollis euismod. Donec sedodio dui."""
#                            ),
#                            dbc.Button("View details", color="secondary"),
#                    ],
#                   md=6,
#                ),
#               dbc.Col(
#                  [
#                      html.H2("Graph"),
#                      dcc.Graph(
#                          figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
#                             ),
#                         ]
#                      ),
#                 ]
#             )
#        ],
# className="mt-4",
# )
