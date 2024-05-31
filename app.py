import dash
from dash import dcc, dash_table
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import talib
import plotly.graph_objs as go
from screener import get_screen_df, get_stock_info
import dash_bootstrap_components as dbc
from utils.data_fetching import fetch_stock_data_yahoo
from utils.data_plottting import create_stock_chart
import utils.layout
import plotly.io as pio
# Set default to dark chart
pio.templates.default = 'dark_chart'

df = pd.DataFrame()
# Initialize the app
external_stylesheets = [dbc.themes.COSMO]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

chart_container_style = {
    "padding": "20px",
    "height": "100vh",
}

app.layout = html.Div(
    style={'backgroundColor': 'black', 'color': 'white'},
    children=[
        html.H1("DMK Capital Advisors", className='display-5', style={
                'textAlign': 'center', 'margin-bottom': '20px', 'color': 'skyblue', 'font-style': 'italic'}),
        html.Div(
            children=[
                html.Label("Period:", style={
                           'margin-right': '10px', 'color': 'white', 'margin-left': '10px', 'font-size': '20px'}),
                dcc.Dropdown(
                    id='time-range-dropdown',
                    options=[
                        {'label': '1D', 'value': '1d'},
                        {'label': '5D', 'value': '5d'},
                        {'label': '1M', 'value': '1mo'},
                        {'label': '3M', 'value': '3mo'},
                        {'label': '6M', 'value': '6mo'},
                        {'label': 'YTD', 'value': 'ytd'},
                        {'label': '1Y', 'value': '1y'},
                        {'label': '2Y', 'value': '2y'},
                        {'label': '5Y', 'value': '5y'},
                        {'label': 'MAX', 'value': 'max'},
                    ],
                    value='1y',
                    style={'width': '80px', 'color': 'black'}
                ),
                html.Button('Refresh Table', id='refresh-button', className='btn btn-primary', n_clicks=0,
                            style={'border-radius': '10px', 'margin-left': '10px'}),
            ],
            style={'display': 'flex', 'justifyContent': 'center',
                   'paddingTop': '20px', 'paddingBottom': '20px'}
        ),
        html.Div([
            dcc.Loading(
                dash_table.DataTable(
                    id='stock-table',
                    # columns=[{"name": i, "id": i} for i in df.columns],
                    columns=[
                        {"name": 'Stock Ticker', "id": 'Stock Ticker'},
                        # {"name": 'Stock Name', "id": 'Stock Name'},
                        {"name": 'Signal Name', "id": 'Signal Name'},
                        # {"name": 'Signal Time', "id": 'Signal Time'},
                        # {"name": 'Current Price', "id": 'Current Price'},
                        {"name": '% Change', "id": '% Change'},
                    ],
                    data=df.to_dict('records'),
                    row_selectable='single',
                    sort_action="native",
                    # page_action="native",
                    # page_current=0,
                    # page_size=10,
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{% Change} >= 0',
                                'column_id': '% Change'
                            },
                            'backgroundColor': 'green',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{% Change} < 0',
                                'column_id': '% Change'
                            },
                            'backgroundColor': 'red',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Signal Name} contains "above"',
                                'column_id': 'Signal Name'
                            },
                            # 'backgroundColor': 'green',
                            'color': 'green'
                        },
                        {
                            'if': {
                                'filter_query': '{Signal Name} contains "below"',
                                'column_id': 'Signal Name'
                            },
                            # 'backgroundColor': 'red',
                            'color': 'red'
                        }
                    ],
                    style_table={'overflowX': 'auto', 'width': '30%',
                                 'height': '25vh', 'overflowY': 'auto'},
                    style_header={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'fontWeight': 'bold'
                    },
                    style_cell={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white'
                    },
                    # column_selectable='single',
                    # editable=True,
                    fixed_rows={'headers': True}
                ),
                type='graph'),
            dcc.Loading(
                dcc.Graph(
                    id="stock-chart",
                    style=chart_container_style,
                    config={
                        "doubleClick": "reset",
                        "displayModeBar": True,
                        "modeBarButtonsToRemove": [
                            "pan2d",
                            "select2d",
                            "lasso2d",
                            "autoScale2d",
                            "resetScale2d",
                        ],
                    },
                    figure={},
                ),
                type='graph'
            ),
        ]),
        # dcc.Loading(
        #     dash_table.DataTable(
        #         id='stock-table',
        #         # columns=[{"name": i, "id": i} for i in df.columns],
        #         columns=[
        #             {"name": 'Stock Ticker', "id": 'Stock Ticker'},
        #             # {"name": 'Stock Name', "id": 'Stock Name'},
        #             {"name": 'Signal Name', "id": 'Signal Name'},
        #             # {"name": 'Signal Time', "id": 'Signal Time'},
        #             # {"name": 'Current Price', "id": 'Current Price'},
        #             {"name": '% Change', "id": '% Change'},
        #         ],
        #         data=df.to_dict('records'),
        #         row_selectable='single',
        #         sort_action="native",
        #         page_action="native",
        #         page_current=0,
        #         page_size=10,
        #         style_data_conditional=[
        #             {
        #                 'if': {
        #                     'filter_query': '{% Change} >= 0',
        #                     'column_id': '% Change'
        #                 },
        #                 'backgroundColor': 'green',
        #                 'color': 'white'
        #             },
        #             {
        #                 'if': {
        #                     'filter_query': '{% Change} < 0',
        #                     'column_id': '% Change'
        #                 },
        #                 'backgroundColor': 'red',
        #                 'color': 'white'
        #             },
        #             {
        #                 'if': {
        #                     'filter_query': '{Signal Name} contains "above"',
        #                     'column_id': 'Signal Name'
        #                 },
        #                 # 'backgroundColor': 'green',
        #                 'color': 'green'
        #             },
        #             {
        #                 'if': {
        #                     'filter_query': '{Signal Name} contains "below"',
        #                     'column_id': 'Signal Name'
        #                 },
        #                 # 'backgroundColor': 'red',
        #                 'color': 'red'
        #             }
        #         ],
        #         style_table={'overflowX': 'auto', 'width': '30%'},
        #         style_header={
        #             'backgroundColor': 'rgb(230, 230, 230)',
        #             'fontWeight': 'bold'
        #         },
        #     ),
        #     type='graph'),
        # dcc.Loading(
        #     dcc.Graph(
        #         id="stock-chart",
        #         style=chart_container_style,
        #         config={
        #            "doubleClick": "reset",
        #            "displayModeBar": True,
        #             "modeBarButtonsToRemove": [
        #                 "pan2d",
        #                 "select2d",
        #                 "lasso2d",
        #                 "autoScale2d",
        #                 "resetScale2d",
        #             ],
        #         },
        #         figure={},
        #     ),
        #     type='graph'
        # ),
        html.H2('General Info'),
        dash_table.DataTable(
            id='info-table-1',
            data=df.to_dict('records'),
            columns=[
                {"name": "Previous", "id": "Previous close"},
                {"name": "Open", "id": "Open"},
                # {"name": "Day's range", "id": "Day's range"},
                # {"name": "52-week range", "id": "52-week range"},
                # {"name": "Volume", "id": "Volume"},
                # {"name": "Avg. volume", "id": "Avg. volume"},
                {"name": "Market cap", "id": "Market cap"},
                {"name": "Beta (5Y monthly)", "id": "Beta (5Y monthly)"},
                # {"name": "PE ratio (TTM)", "id": "PE ratio (TTM)"},
                # {"name": "EPS (TTM)", "id": "EPS (TTM)"},
                {"name": "Earnings date", "id": "Earnings date"},
                {"name": "Fwd dividend & yield", "id": "Forward dividend & yield"},
                {"name": "Ex-dividend date", "id": "Ex-dividend date"},
                {"name": "1y target est", "id": "1y target est"},
            ],
            style_table={'overflowX': 'auto', 'width': '100%'},
            style_header={
                'backgroundColor': 'rgb(50, 50, 50)',
                'fontWeight': 'bold'
            },
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            },
        ),
        dcc.Interval(
            id='interval-component',
            interval=60*60*1000,  # in milliseconds
        )
        # dbc.Table(id='info-table', bordered=True,
        #           hover=True, responsive=True, striped=True),
        # dbc.Table([
        #     html.Tbody([
        #         html.Tr([html.Td('Previous close'), html.Td('913.56')]),
        #         html.Tr([html.Td('Open'), html.Td('924.72')]),
        #         html.Tr([html.Td('Bid'), html.Td('928.80 x 100')]),
        #         html.Tr([html.Td('Ask'), html.Td('930.00 x 100')]),
        #         html.Tr([html.Td('Day\'s range'), html.Td('915.99 - 932.30')]),
        #         html.Tr([html.Td('52-week range'), html.Td('294.30 - 974.00')]),
        #         html.Tr([html.Td('Volume'), html.Td('9,671,785')]),
        #         html.Tr([html.Td('Avg. volume'), html.Td('51,403,463')]),
        #         html.Tr([html.Td('Market cap'), html.Td('2.323T')]),
        #         html.Tr([html.Td('Beta (5Y monthly)'), html.Td('1.75')]),
        #         html.Tr([html.Td('PE ratio (TTM)'), html.Td('77.67')]),
        #         html.Tr([html.Td('EPS (TTM)'), html.Td('11.97')]),
        #         html.Tr([html.Td('Earnings date'), html.Td('22 May 2024')]),
        #         html.Tr([html.Td('Forward dividend & yield'), html.Td('0.16 (0.02%)')]),
        #         html.Tr([html.Td('Ex-dividend date'), html.Td('05 Mar 2024')]),
        #         html.Tr([html.Td('1y target est'), html.Td('1,032.95')]),
        #     ])
        # ], bordered=True, hover=True, responsive=True, striped=True),

    ],
    id="page-content",
)


@app.callback(
    Output('stock-chart', 'figure'),
    [Input('stock-table', 'selected_rows'),
     Input('time-range-dropdown', 'value')],
    [
        State('stock-table', 'data'),
        # State('time-range-dropdown', 'value'),
    ]
)
def display_chart(selected_rows, period, data):

    if selected_rows is None or len(selected_rows) == 0:
        return go.Figure()
    row = selected_rows[0]
    selected_ticker = data[row]['Stock Ticker']
    print(selected_ticker)
    stock_data, info = fetch_stock_data_yahoo(selected_ticker, period, '1d')
    stock_data['SMA_30'] = talib.SMA(stock_data['close'], timeperiod=30)
    stock_data['SMA_50'] = talib.SMA(stock_data['close'], timeperiod=50)
    stock_data['SMA_200'] = talib.SMA(stock_data['close'], timeperiod=200)
    stock_data = stock_data.tail(250)
    fig = create_stock_chart(stock_data, selected_ticker, info)
    fig.update_layout(
        title=f"<a href='https://finance.yahoo.com/quote/{selected_ticker}/'>{selected_ticker}</a>",
        #   xaxis_title='Date', yaxis_title='Price'
    )
    return fig


@app.callback(
    Output('stock-table', 'data'),
    [
        Input('interval-component', 'n_intervals'),
        Input('refresh-button', 'n_clicks')
    ]
)
def update_data(intervals, n):
    print("intervals", intervals)
    df = get_screen_df()
    return df.to_dict('records')


# @app.callback(
#     Output('info-table', 'children'),
#     [Input('stock-table', 'selected_rows')],
#     [State('stock-table', 'data')]
# )
# def update_table(selected_rows, data):

#     if selected_rows is None or len(selected_rows) == 0:
#         return html.Tbody([])
#     row = selected_rows[0]
#     selected_ticker = data[row]['Stock Ticker']
#     stock_data = get_stock_info(selected_ticker)
#     return html.Tbody([
#         html.Tr([html.Td(key), html.Td(value)]) for key, value in stock_data.items()
#     ])


@app.callback(
    Output('info-table-1', 'data'),
    [Input('stock-table', 'selected_rows')],
    [State('stock-table', 'data')]
)
def update_table_1(selected_rows, data):
    if selected_rows is None or len(selected_rows) == 0:
        return []
    row = selected_rows[0]
    selected_ticker = data[row]['Stock Ticker']
    stock_data = get_stock_info(selected_ticker)
    print([stock_data])
    return [stock_data]


if __name__ == '__main__':
    app.run_server(debug=True)
