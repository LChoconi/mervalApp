import pandas as pd
import yfinance as yf
from datetime import date
import datetime
import plotly.express as px
from dateutil.relativedelta import relativedelta
from jupyter_dash import JupyterDash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px

dateToday = date.today()
dateToday = datetime.datetime.strptime(str(dateToday),'%Y-%m-%d').strftime('%Y-%m-%d')
fistDate = date.today()-relativedelta(years=1)
fistDate = datetime.datetime.strptime(str(fistDate),'%Y-%m-%d').strftime('%Y-%m-%d')
fixedTickers = ['ALUA.BA', 'BBAR.BA', 'BMA.BA', 'BYMA.BA', 'CEPU.BA', 'COME.BA', 'CRES.BA', 'EDN.BA', 'GGAL.BA', 'LOMA.BA', 'MIRG.BA',
                'PAMP.BA', 'SUPV.BA', 'TECO2.BA', 'TGNO4.BA', 'TGSU2.BA', 'TRAN.BA', 'TXR.BA', 'VALO.BA', 'YPFD.BA', 'M.BA']

dataGGAL = yf.download(['GGAL.BA', 'GGAL'], start=fistDate, end=dateToday)
histCCL = dataGGAL["Adj Close"].dropna()  
histCCL = histCCL.reset_index() 
histCCL["USD"] = histCCL["GGAL.BA"]*10/histCCL["GGAL"]
histCCL = histCCL.drop(columns=['GGAL','GGAL.BA'])

dataPanelLider = yf.download(fixedTickers, start=fistDate, end=dateToday)
dataMerval = dataPanelLider["Adj Close"].dropna() 
dataMerval['Index'] = range(1, len(dataMerval)+1)
dataMerval = dataMerval.reset_index()
dataMerval = pd.melt(dataMerval, id_vars='Date',
                        var_name='Ticker', value_name='Close')

dataMerval = pd.DataFrame(pd.merge(histCCL, dataMerval, how='left', on=['Date'])).dropna() 
dataMerval ['Close USD'] = dataMerval['Close']/dataMerval['USD']

dataMerval = dataMerval[~((dataMerval.Date=="2022-07-14") & (dataMerval.Ticker=="M.BA"))] ## Filter inaccurate data in Merval

CCL = "Fx Rate (CCL): "+str(round(histCCL["USD"].iloc[-1], ndigits=1))

external_stylesheets = [dbc.themes.ZEPHYR]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Merval"
app.layout = html.Div([
                        html.H1(
                            "Historical Data - S&P Merval",
                            style={'text-align': 'left', 'background-color':'#0466C8', 'color':'#EBEBEB', "margin-bottom": "15px" ,  "padding": "10px"}
                            ),

                        html.H2(
                            CCL,
                            style={'text-align': 'left', 'color':'#9B9C9B', "margin-bottom": "15px"}
                            ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H3(
                                    "Select a ticker:",
                                    style={'text-align': 'left', 'color':'#9B9C9B', "margin-bottom": "15px"}
                                    ),
                                    width="auto"),

                                dbc.Col(
                                    dcc.Dropdown(
                                        id="Select_Ticker",                    
                                        options=[{'label': x, 'value': x} for x in fixedTickers],
                                        multi=False,
                                        value='M.BA',
                                        style={'width': "200px", 'color': '#9B9C9B'}
                                        ),
                                    width="auto"
                                    )
                            ],
                        ),



                        dbc.Row(
                                [
                                    dbc.Col(

                                        dcc.Graph(id='lines_plot_USD',config={"displayModeBar": True,
                                                                              'displaylogo': False,
                                                                              'modeBarButtonsToRemove': ['select', 'zoomIn', 'zoomOut', 'autoScale']},
                                                                               style={"width": 900, "height": 500}, figure={}),
                                        width="auto"),
                                
                                    dbc.Col(
                                        dcc.Graph(id='lines_plot_ARP',config={"displayModeBar": True,
                                                                              'displaylogo': False,
                                                                              'modeBarButtonsToRemove': ['select', 'zoomIn', 'zoomOut', 'autoScale']}, 
                                                                              style={"width": 900, "height": 500}, figure={}),
                                        width="auto"),
                                ],
                                justify="evenly",
                                ),
                        ])
                      
#  style={"width": 1000, "height": 800},   
#                      
@app.callback(
    dash.dependencies.Output('lines_plot_USD', 'figure'),
    dash.dependencies.Output('lines_plot_ARP', 'figure'),
    [dash.dependencies.Input('Select_Ticker', 'value')])

def update_output(value):
    dff = dataMerval[dataMerval["Ticker"] == value]

    fig1 = {
                                              "data": [
                                                  {
                                                      "x": dff["Date"],
                                                      "y": dff["Close USD"],
                                                      "type": "lines",
                                                      "hovertemplate": "%{y:,.1f}<extra></extra>",
                                                  },
                                              ],
                                              "layout": {
                                                  "title": {
                                                      "text": "USD",
                                                      "x": 0.05,
                                                      "xanchor": "left",
                                                      "size": 20,
                                                      "family": "Arial"
                                                  },
                                                  #"yaxis": {"tickprefix": "$"},
                                                  "colorway": ["#007BBA"],
                                                  "xaxis": {"showgrid": False},
                                              },
                                          }
    fig2 = {
                                              "data": [
                                                  {
                                                      "x": dff["Date"],
                                                      "y": dff["Close"],
                                                      "type": "lines",
                                                      "hovertemplate": "%{y:,.0f}<extra></extra>",
                                                  },
                                              ],
                                              "layout": {
                                                  "title": {
                                                      "text": "ARS (Argentine Peso)",
                                                      "x": 0.05,
                                                      "xanchor": "left",
                                                      "size": 20,
                                                      "family": "Arial"
                                                  },
                                                  #"yaxis": {"tickprefix": "$"},
                                                  "colorway": ["#7CCDF4"],
                                                  "xaxis": {"showgrid": False},
                                              },
                                          }    

    return fig1, fig2
                              
              
app.run_server(debug=True, use_reloader=True)