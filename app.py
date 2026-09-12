from dash import Dash, dash_table, html, dcc
import plotly.express as px
import pandas as pd
from data_process import limit_map_countries_gdp_yr
from callbacks import get_callbacks

gdp_map_data = limit_map_countries_gdp_yr()
def create_dropdown(options, selected_value, id, debounce=False, closeOnSelect=True, is_multi=False):
    return dcc.Dropdown(
        options,
        selected_value,
        id=id,
        debounce=debounce,
        closeOnSelect=closeOnSelect,
        multi=is_multi,
        style={'width': '75%'}
    )

def generic_div(dccFunc):
    return html.Div(
        [dccFunc],
        style={'flex': 1, 'padding-left': '1rem', 'padding-right': '1rem'}
    )

app = Dash()
app.layout = [
    html.Section([
        html.H1("Global Data Dashboard", style={'textAlign': 'center'}),
        html.Section([
            dcc.Graph(id='map-dashboard'),
            html.Div(dcc.Slider(
                gdp_map_data['yr'].min(),
                gdp_map_data['yr'].max(),
                id='year-slider',
                step=1,
                value=gdp_map_data['yr'].max()
            )),
        ]),
        dcc.Store(id='selected-country', data=None),
        html.Section([
            html.Div([
                dcc.Graph(id='gdp-graph', style={'flex': '1', 'minHeight': '0'}),
                dcc.Graph(id='pop-bar', style={'flex': '1', 'minHeight': '0'})
            ], style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'row'
            }),
            html.Div([
                dcc.Graph(id='births-graph', style={'flex': '1', 'minHeight': '0'}),
                dcc.Graph(id='e0-graph', style={'flex': '1', 'minHeight': '0'}),
            ], style={
                'flex': '1',
                'display': 'flex',
                'flexDirection': 'row'
            }),
        ]),
    ],
    style={'padding': '2rem'})
]
get_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)