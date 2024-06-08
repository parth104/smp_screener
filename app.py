import dash
from dash import dcc, dash_table
from dash import html
from dash.dependencies import Input, Output, State
from smp_tickers import ALL_TICKERS
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
        html.H1("DMK Capital Advisors", className='display-6', style={
                'textAlign': 'center', 'margin-bottom': '20px', 'color': 'skyblue', 'font-style': 'italic'}),
        html.Div(
            children=[
                html.Button('Refresh Table', id='refresh-button', className='btn btn-primary', n_clicks=0,
                            style={'border-radius': '10px', 'margin-left': '5px'}),
                html.Label("Period:", style={
                           'margin-right': '10px', 'color': 'white', 'font-size': '20px',  'margin-left': '600px',
                           }),
                dcc.Dropdown(
                    id='time-range-dropdown',
                    options=[
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
                dcc.Input(
                    id="stock-ticker-input",
                    list='stock-names',
                    placeholder='Enter Stock Name',
                    type='text',
                    style={'marginRight': '10px',
                           'marginLeft': '10px', 'textAlign': 'center'}
                ),
                html.Button('Load Chart', id='load-chart', className='btn btn-primary', n_clicks=0,
                            style={'border-radius': '10px', 'margin-left': '5px'}),
                html.Datalist(
                    id='stock-names',
                    children=[],
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
                            'width': '100%',
                            'height': '100%',
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
                children=[
                    dcc.Loading(
                        dcc.Graph(
                            id="stock-chart",
                            # Center the graph horizontally
                            style={'height': '60vh',
                                   'width': '70vw', 'margin': 'auto'},
                            config={
                                "scrollZoom": True,
                                "doubleClick": "reset",
                                "displayModeBar": True,
                                "modeBarButtonsToRemove": [
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
                    dbc.Table(id='info-table', bordered=True, class_name='table table-dark table-striped',
                              hover=True, striped=True, size='sm', style={'width': '70vw', 'margin': 'auto'}),
                    # Adjust margins as needed
                ],
                style={'flex': '1', 'margin': '10px'}
            ),
        ], style={'display': 'flex'}),
        # dbc.Table(id='info-table', bordered=True, class_name='table table-dark table-striped',
        #           hover=True, striped=True, size='sm', style={'margin-left': '30%', 'width': '60%'}),
        dcc.Interval(
            id='interval-component',
            interval=60*60*1000,  # in milliseconds
        )
    ],
    id="page-content",
)


@app.callback(
    Output('stock-chart', 'figure'),
    [
        Input('stock-table', 'selected_rows'),
        Input('time-range-dropdown', 'value'),
        Input('load-chart', 'n_clicks'),
    ],
    [
        State('stock-table', 'data'),
        State('stock-ticker-input', 'value'),
    ]
)
def display_chart(selected_rows, period, load_chart, data, selected_ticker):

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'load-chart':
        if selected_ticker is None:
            return go.Figure()
    elif button_id == 'stock-table' or button_id == 'time-range-dropdown':
        if selected_rows is None or len(selected_rows) == 0:
            return go.Figure()
        row = selected_rows[0]
        selected_ticker = data[row]['Stock Ticker']
    else:
        return go.Figure()

    period_num_rows = {
        '3mo': 65,
        '6mo': 120,
        'ytd': 200,
        '1y': 250,
        '2y': 500,
        '5y': 1265,
        'max': 20000
    }

    old_period = period
    if period in {'3mo', '6mo', 'ytd', '1y'}:
        period = '2y'
    elif period in {'2y', '5y'}:
        period = 'max'

    stock_data, info = fetch_stock_data_yahoo(selected_ticker, period, '1d')
    stock_data['SMA_30'] = talib.SMA(stock_data['close'], timeperiod=30)
    stock_data['SMA_50'] = talib.SMA(stock_data['close'], timeperiod=50)
    stock_data['SMA_200'] = talib.SMA(stock_data['close'], timeperiod=200)
    # stock_data = stock_data.tail(250)
    num_rows = period_num_rows.get(old_period, 200) // 1
    stock_data = stock_data.tail(num_rows)
    fig = create_stock_chart(stock_data, selected_ticker, info)
    fig.update_layout(
        autosize=True,
        title=f"<a href='https://finance.yahoo.com/quote/{selected_ticker}/'>{selected_ticker}</a>",
        #   xaxis_title='Date', yaxis_title='Price'
    )
    return fig


@app.callback(
    Output('stock-names', 'children'),
    [Input('stock-ticker-input', 'value')]
)
def update_stock_name_suggestions(value):
    if value is None:
        return []
    suggestions = [stock for stock in ALL_TICKERS if value.lower()
                   in stock.lower()]
    return [html.Option(value=suggestion) for suggestion in suggestions]


@app.callback(
    Output('stock-table', 'data'),
    [
        Input('interval-component', 'n_intervals'),
        Input('refresh-button', 'n_clicks')
    ]
)
def update_data(intervals, n):
    df = get_screen_df()
    return df.to_dict('records')


@app.callback(
    Output('info-table', 'children'),
    [
        Input('stock-table', 'selected_rows'),
        Input('load-chart', 'n_clicks'),
    ],
    [
        State('stock-table', 'data'),
        State('stock-ticker-input', 'value'),
    ]
)
def update_info_table(selected_rows, n, data, selected_ticker):

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'load-chart':
        if selected_ticker is None:
            return html.Tbody([])
    elif button_id == 'stock-table':
        if selected_rows is None or len(selected_rows) == 0:
            return html.Tbody([])
        row = selected_rows[0]
        selected_ticker = data[row]['Stock Ticker']
    else:
        return html.Tbody([])

    stock_data = get_stock_info(selected_ticker)
    stock_data_items = list(stock_data.items())

    # Create rows with 4 columns each (2 rows)
    rows = []
    for i in range(0, len(stock_data_items), 2):
        row = stock_data_items[i:i+2]
        cells = []
        for key, value in row:
            # make the key bold
            cells.append(html.Td(html.B(key)))
            cells.append(html.Td(value))
        rows.append(html.Tr(cells))

    return html.Tbody(rows)


if __name__ == '__main__':
    app.run_server(debug=True)
