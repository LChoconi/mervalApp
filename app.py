import pandas as pd
import yfinance as yf
from datetime import date
import datetime
import plotly.express as px
from dateutil.relativedelta import relativedelta
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px

dateTodayVar = date.today()
dateTodayVar = datetime.datetime.strptime(str(dateTodayVar),'%Y-%m-%d').strftime('%Y-%m-%d')
firstDateVar = date.today()-relativedelta(years=1)
firstDateVar = datetime.datetime.strptime(str(firstDateVar),'%Y-%m-%d').strftime('%Y-%m-%d')
fixedTickersVar = ['ALUA.BA', 'BBAR.BA', 'BMA.BA', 'BYMA.BA', 'CEPU.BA', 'COME.BA', 'CRES.BA', 'EDN.BA', 'GGAL.BA', 'LOMA.BA', 'MIRG.BA',
                'PAMP.BA', 'SUPV.BA', 'TECO2.BA', 'TGNO4.BA', 'TGSU2.BA', 'TRAN.BA', 'TXR.BA', 'VALO.BA', 'YPFD.BA', 'M.BA']

def DataMervalUSD(firstDate=firstDateVar, lastDate=dateTodayVar, tickers=['M.BA']):
    dataGGAL = yf.download(['GGAL.BA', 'GGAL'], start=firstDate, end=lastDate)
    histCCL = dataGGAL["Adj Close"].dropna()  
    histCCL = histCCL.reset_index() 
    histCCL["USD"] = histCCL["GGAL.BA"]*10/histCCL["GGAL"]
    histCCL = histCCL.drop(columns=['GGAL','GGAL.BA'])

    dataPanelLider = yf.download(tickers, start=firstDate, end=lastDate)
    dataMerval = dataPanelLider["Adj Close"].dropna()
    dataMerval = dataMerval.reset_index()
    dataMerval = dataMerval.rename({'Adj Close': 'Close'}, axis='columns') 
    dataMerval['Ticker'] = tickers[0]
    dataMerval = pd.DataFrame(pd.merge(histCCL, dataMerval, how='left', on=['Date'])).dropna() 
    dataMerval ['Close USD'] = dataMerval['Close']/dataMerval['USD']
    dataMerval = dataMerval[~((dataMerval.Date=="2022-07-14") & (dataMerval.Ticker=="M.BA"))] ## Filter inaccurate data in Merval
    return dataMerval, histCCL


external_stylesheets = [dbc.themes.ZEPHYR]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Merval"
app.layout = html.Div([
                        html.H1(
                            "Historical Data - S&P Merval",
                            style={'text-align': 'left', 'background-color':'#0466C8', 'color':'#EBEBEB', "margin-bottom": "15px" ,  "padding": "10px"}
                            ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H3("Select Ticker:",
                                    style={'text-align': 'left', 'color':'#9B9C9B', "margin-bottom": "15px"}
                                    ),
                                    width="auto"),

                                dbc.Col(
                                    dcc.Dropdown(
                                        id="Select_Ticker",                    
                                        options=[{'label': x, 'value': x} for x in fixedTickersVar],
                                        multi=False,
                                        placeholder="Select a Ticker",
                                        value='M.BA',
                                        style={'width': "200px", 'color': '#9B9C9B'}
                                        ),
                                    width="auto"
                                    ),

                                dbc.Col(
                                    html.H3("Select Date:",
                                    style={'text-align': 'left', 'color':'#9B9C9B', "margin-bottom": "15px"}
                                    ),
                                    width="auto"),

                                dbc.Col(
                                    dcc.DatePickerRange(
                                        id='my-date-picker-range',
                                        display_format='DD-MM-YYYY',
                                        number_of_months_shown = 1,
                                        min_date_allowed = date(1995, 8, 5),
                                        max_date_allowed = date(2100, 9, 19),
                                        start_date = firstDateVar,
                                        end_date = dateTodayVar
                                    )
                                )
                            ],
                        ),


                        dbc.Row(
                                [
                                    dbc.Col(

                                        dcc.Graph(id='lines_plot_USD',config={"displayModeBar": True,
                                                                              'displaylogo': False,
                                                                              'modeBarButtonsToRemove': ['select', 'zoomIn', 'zoomOut', 'autoScale']},
                                                                               style={"width": 600, "height": 400}, figure={}),
                                        width="auto"),
                                
                                    dbc.Col(
                                        dcc.Graph(id='lines_plot_ARP',config={"displayModeBar": True,
                                                                              'displaylogo': False,
                                                                              'modeBarButtonsToRemove': ['select', 'zoomIn', 'zoomOut', 'autoScale']}, 
                                                                              style={"width": 600, "height": 400}, figure={}),
                                        width="auto"),

                                    dbc.Col(
                                        dcc.Graph(id='lines_plot_CCL',config={"displayModeBar": True,
                                                                              'displaylogo': False,
                                                                              'modeBarButtonsToRemove': ['select', 'zoomIn', 'zoomOut', 'autoScale']}, 
                                                                              style={"width": 600, "height": 400}, figure={}),
                                        width="auto"),

                                ],
                                justify="evenly",
                                ),
                        ])
                      
                    
@callback(
    Output('lines_plot_USD', 'figure'),
    Output('lines_plot_ARP', 'figure'),
    Output('lines_plot_CCL', 'figure'),
    Input('Select_Ticker', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))


def update_output(value, start_date, end_date):
    dataTickers, dataFx = DataMervalUSD(firstDate=start_date, lastDate=end_date,tickers=[value])
    dff = dataTickers[dataTickers["Ticker"] == value]

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
    fig3 = {
                                              "data": [
                                                  {
                                                      "x": dataFx["Date"],
                                                      "y": dataFx["USD"],
                                                      "type": "lines",
                                                      "hovertemplate": "%{y:,.0f}<extra></extra>",
                                                  },
                                              ],
                                              "layout": {
                                                  "title": {
                                                      "text": "Fx Rate Peso-USD (CLL)",
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

    return fig1, fig2, fig3

if __name__ == '__main__':
    app.run(debug=True)