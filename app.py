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
                html.Button('Refresh Table', id='refresh-button', className='btn btn-primary', n_clicks=0,
                            style={'border-radius': '10px', 'margin-left': '5px'}),
                html.Label("Period:", style={
                           'margin-right': '10px', 'color': 'white', 'font-size': '20px',  'margin-left': '800px',
                           }),

                dcc.Dropdown(
                    id='time-range-dropdown',
                    options=[
                        {'label': 'YTD', 'value': 'ytd'},
                        {'label': '1Y', 'value': '1y'},
                        {'label': '2Y', 'value': '2y'},
                        {'label': '5Y', 'value': '5y'},
                        {'label': 'MAX', 'value': 'max'},
                    ],
                    value='1y',
                    style={'width': '80px', 'color': 'black'}
                ),

            ],
            style={'display': 'flex', 'justifyContent': 'center',
                   'paddingTop': '20px', 'paddingBottom': '20px'}
        ),
        html.Div([
            html.Div(
                dcc.Loading(
                    dash_table.DataTable(
                        id='stock-table',
                        columns=[
                            {"name": 'Stock Ticker', "id": 'Stock Ticker'},
                            {"name": 'Signal Name', "id": 'Signal Name'},
                            {"name": '% Change', "id": '% Change'},
                        ],
                        data=df.to_dict('records'),
                        row_selectable='single',
                        sort_action="native",
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{% Change} >= 0', 'column_id': '% Change'},
                                'backgroundColor': 'green',
                                'color': 'white'
                            },
                            {
                                'if': {'filter_query': '{% Change} < 0', 'column_id': '% Change'},
                                'backgroundColor': 'red',
                                'color': 'white'
                            },
                            {
                                'if': {'filter_query': '{Signal Name} contains "above"', 'column_id': 'Signal Name'},
                                'color': 'green'
                            },
                            {
                                'if': {'filter_query': '{Signal Name} contains "below"', 'column_id': 'Signal Name'},
                                'color': 'red'
                            }
                        ],
                        style_table={
                            'overflowX': 'auto',
                            'width': '90%',
                            'height': '60vh',
                            'overflowY': 'auto',
                            'margin': 'auto'
                        },
                        style_header={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'fontWeight': 'bold'
                        },
                        style_cell={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'color': 'white'
                        },
                        fixed_rows={'headers': True}
                    ),
                    type='dot'
                ),
                # Adjust margins as needed
                style={'flex': '1', 'margin': '10px'}
            ),

            # Right side: Graph
            html.Div(
                dcc.Loading(
                    dcc.Graph(
                        id="stock-chart",
                        # Center the graph horizontally
                        style={'height': '60vh',
                               'width': '70vw', 'margin': 'auto'},
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
                # Adjust margins as needed
                style={'flex': '1', 'margin': '10px'}
            ),
        ], style={'display': 'flex'}),
        html.H2('General Info'),
        dash_table.DataTable(
            id='info-table-1',
            data=df.to_dict('records'),
            columns=[
                {"name": "Previous", "id": "Previous close"},
                {"name": "Open", "id": "Open"},
                {"name": "Market cap", "id": "Market cap"},
                {"name": "Beta (5Y monthly)", "id": "Beta (5Y monthly)"},
                {"name": "Earnings date", "id": "Earnings date"},
                {"name": "Fwd dividend & yield", "id": "Forward dividend & yield"},
                {"name": "Ex-dividend date", "id": "Ex-dividend date"},
                {"name": "1y target est", "id": "1y target est"},
            ],
            style_table={'overflowX': 'auto', 'width': '100%',
                         'margin-bottom': '40px', 'padding': '10px'},
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

    period_num_rows = {
        'ytd': 200,
        '1y': 250,
        '2y': 500,
        '5y': 1300,
        'max': 20000
    }

    old_period = period

    if period in {'ytd', '1y', '2y', '5y'}:
        period = '5y'

    row = selected_rows[0]
    selected_ticker = data[row]['Stock Ticker']
    print(selected_ticker, period)
    stock_data, info = fetch_stock_data_yahoo(selected_ticker, period, '1d')
    stock_data['SMA_30'] = talib.SMA(stock_data['close'], timeperiod=30)
    stock_data['SMA_50'] = talib.SMA(stock_data['close'], timeperiod=50)
    stock_data['SMA_200'] = talib.SMA(stock_data['close'], timeperiod=200)
    # stock_data = stock_data.tail(250)
    num_rows = period_num_rows.get(old_period, 200) // 1
    stock_data = stock_data.tail(num_rows)
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
    app.run_server(debug=False)
