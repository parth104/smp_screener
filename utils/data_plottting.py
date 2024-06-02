import pandas as pd
from datetime import timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_rangebreaks(index):
    # Convert the index to a series so we can use diff
    s = pd.Series(index)

    # Find the gaps in the index where the difference between two dates is more than 1 day
    gaps = s[s.diff() > pd.Timedelta(days=1)]

    # Create range breaks for each gap
    rangebreaks = [
        {
            "bounds": [
                s.iloc[idx - 1] + pd.Timedelta(days=1),
                s.iloc[idx],
            ]
        }
        for idx in gaps.index
    ]
    return rangebreaks


def convert_to_trillion(number):
    trillion = number / 1_000_000_000_000
    return f"{trillion:.2f} trillion"


def create_stock_chart(data, ticker, stock_info):

    # Create subplots
    num_subplots = 2
    candlestick_height = 0.85
    remaining_height = (1 - candlestick_height) / (num_subplots - 1)
    subplot_heights = [candlestick_height] + \
        [remaining_height] * (num_subplots - 1)

    fig = make_subplots(
        rows=num_subplots,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=subplot_heights,
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["close"],
            name=ticker,
            mode="lines",
            line=dict(color="white"),
            fill="tozeroy",
            fillcolor="rgba(0, 100, 80, 0.2)",
        ),
        row=1,
        col=1,
    )
    # else:
    # fig.add_trace(
    #     go.Candlestick(
    #         x=data.index,
    #         open=data["open"],
    #         high=data["high"],
    #         low=data["low"],
    #         close=data["close"],
    #         name=ticker,
    #     ),
    #     row=1,
    #     col=1,
    # )

    # Add moving average traces
    ma_colors = {30: "magenta", 50: "green", 200: "yellow"}
    for ma, color in ma_colors.items():
        ma_column = f"SMA_{ma}"
        if ma_column in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[ma_column],
                    mode="lines",
                    name=f"{ma}-day SMA",
                    line=dict(color=color),
                    # hoverinfo="none"
                ),
                row=1,
                col=1,
            )

    # Add volume to the second row
    fig.add_trace(
        go.Bar(x=data.index, y=data["volume"],
               name="Volume", marker_color="#8C127C"),
        row=2,
        col=1,
    )

    # Update layout to be dynamic and not use subplot titles
    fig.update_layout(
        autosize=True,  # Enable dynamic sizing
        xaxis_rangeslider_visible=False,
        showlegend=False,  # Hide the legend
    )

    max_date = data.index.max()
    min_date = data.index.min()
    min_close = data['close'].min() - 25
    max_close = data['close'].max() + 25
    date_range = max_date - min_date
    extra_space = date_range.days // 20

    if extra_space <= 2:
        extra_space = 1

    extra_space = timedelta(days=extra_space)
    fig.update_xaxes(
        range=[data.index.min() - extra_space, max_date + extra_space])
    fig.update_layout(
        hovermode="x",
        yaxis=dict(range=[min_close, max_close])
    )

    rangebreaks = get_rangebreaks(data.index)
    fig.update_layout(
        xaxis=dict(
            rangebreaks=rangebreaks,
        ),
    )

    return fig
