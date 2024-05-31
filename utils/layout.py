import plotly.graph_objects as go
import plotly.io as pio

# Define your custom dark theme template
dark_chart = go.layout.Template({
    'layout': {
        'plot_bgcolor': '#121212',  # Dark background for the plot area
        'paper_bgcolor': '#121212',  # Dark background for the surrounding paper
        'font': {
            'color': 'white'  # White font for better contrast
        },
        'xaxis': {
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 'M1',
            'showgrid': False,
            'gridcolor': '#343434',  # Darker grid lines for subtlety
            'gridwidth': 2,
            'zerolinecolor': '#444444',  # Dark zero line color
            'zerolinewidth': 2,
            'tickcolor': 'white',  # White ticks to match the font color
            'tickwidth': 0.5,
            'griddash': 'solid',
            'linecolor': '#444444',  # Axis line color
            'linewidth': 2
        },
        'yaxis': {
            'tickmode': 'auto',
            'showgrid': False,
            'gridcolor': '#343434',
            'gridwidth': 2,
            'zerolinecolor': '#444444',
            'zerolinewidth': 2,
            'tickcolor': 'white',
            'tickwidth': 0.5,
            'griddash': 'solid',
            'linecolor': '#444444',
            'linewidth': 2,
            'side': 'right'
        }
    }
})

# Register the custom template under a name
pio.templates['dark_chart'] = dark_chart
