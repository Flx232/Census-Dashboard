from dash import Dash, dash_table, html, dcc
import plotly.express as px
import pandas as pd
from data_process import limit_map_countries_gdp_yr, AMALGAMATED_DATA, GDP_DF, IDB_DF, COUNTRIES_DF
from callbacks import get_callbacks

gdp_map_data = limit_map_countries_gdp_yr()
all_data = AMALGAMATED_DATA.copy()
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
GRAPH_LAYOUT = {'flex': '1', 'minHeight': '0', 'minWidth': '0'}
GRAPH_ROW = {'flex': '1', 'display': 'flex', 'flexDirection': 'row'}
dataset_tab = dcc.Tab(
    label="DataTables",
    children = [
        html.H3('Amalgamated Data of IDB5yr, GDP data and Countries codes'),
        html.Div([dcc.Dropdown(
            [year for year in range(AMALGAMATED_DATA['yr'].min(), AMALGAMATED_DATA['yr'].max()+1)],
            AMALGAMATED_DATA['yr'].max(),
            id='yr-dropdown',
        )], style={"width": "15%"}),
        dash_table.DataTable(
            id = "amalg-data",
            page_size=15, sort_action="native",
            style_table={'overflowX': 'scroll'},
        ),
        html.H3(['GDP data from: ',
            html.A(
                'World Bank Group GDP dataset',
                href='https://data.worldbank.org/indicator/NY.GDP.MKTP.CD',
                target='_blank',
            )]
        ),
        dash_table.DataTable(
            data=GDP_DF.to_dict("records"), 
            page_size=10, sort_action="native",
            style_table={'overflowX': 'scroll'},
        ),
        html.H3(['IDB5yr data from: ',
            html.A(
                'US Census International Database',
                href='https://www.census.gov/programs-surveys/international-programs/about/idb.html',
                target='_blank',
            )]
        ),
        dash_table.DataTable(
            data=IDB_DF[IDB_DF['YR'] == 2024].to_dict("records"), 
            page_size=10, sort_action="native",
            style_table={'overflowX': 'scroll'},
        ),
        html.H3(['Countries codes dataset from: ',
            html.A(
                'tadast on GitHub',
                href='https://gist.github.com/tadast/8827699',
                target='_blank',
            )]
        ),
        dash_table.DataTable(
            data=COUNTRIES_DF.to_dict("records"), 
            page_size=10, sort_action="native",
            style_table={'overflowX': 'scroll'},
        ),
    ]
)

data_graphs = dcc.Tab(
    label="Data Graphs",
    children = [
        html.Div([
            html.Div([
                dcc.Graph(id='wealth-diff-world', style=GRAPH_LAYOUT),
                dcc.Graph(id='gdp-cumulation', style=GRAPH_LAYOUT)
            ], style=GRAPH_ROW),
            html.Div(dcc.RangeSlider(
                gdp_map_data['yr'].min(),
                gdp_map_data['yr'].max(),
                id='wealth-range-year-slider',
                step=1,
                value=[gdp_map_data['yr'].min(), gdp_map_data['yr'].max()]
            )),
        ], style={"padding-bottom": '3rem'}),
        html.Div([
            html.Div([dcc.Dropdown(
                ["pop", "births", "deaths", "area"],
                'pop',
                id='quant-dropdown',
            )], style={"width": "15%"}),
            html.Div([
                dcc.Graph(id='scatter-world')
            ]),
             html.Div(dcc.Slider(
                gdp_map_data['yr'].min(),
                gdp_map_data['yr'].max(),
                id='year-picker',
                step=1,
                value=gdp_map_data['yr'].max()
            )),
        ], style={"padding": '3rem 0rem'}),
    ]
)

map_tab = dcc.Tab(
    label="Map Dashboard",
    children = [
    dcc.Graph(
        id='map-dashboard',
        style={'height': '100%', 'width': '100%'}
    ),
    html.Div(dcc.Slider(
        gdp_map_data['yr'].min(),
        gdp_map_data['yr'].max(),
        id='year-slider',
        step=1,
        value=gdp_map_data['yr'].max()
    )),
])

graphs_tab = dcc.Tab(
    label="Graphs",
    children = [
    html.Div([
        html.Div([
            dcc.Graph(id='gdp-graph', style=GRAPH_LAYOUT),
            dcc.Graph(id='pop-bar', style=GRAPH_LAYOUT)
        ], style=GRAPH_ROW),
        html.Div([
            dcc.Graph(id='births-graph', style=GRAPH_LAYOUT),
            dcc.Graph(id='pop-graph', style=GRAPH_LAYOUT),
            dcc.Graph(id='e0-graph', style=GRAPH_LAYOUT),
        ], style=GRAPH_ROW),
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='birth-age-graph', style=GRAPH_LAYOUT),
            dcc.Graph(id='pop-age-graph', style=GRAPH_LAYOUT)
        ], style=GRAPH_ROW),
        html.Div(dcc.Slider(
            1950,
            2100,
            id='age-slider',
            step=1,
            value=gdp_map_data['yr'].min()
        )),
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='pop-increase-hist', style=GRAPH_LAYOUT),
            dcc.Graph(id='rate-graph', style=GRAPH_LAYOUT)
        ], style=GRAPH_ROW),
        html.Div([
            html.Div(dcc.RangeSlider(id = 'date-slider')),
        ]),
    ]),
], id='graphs', style={'display': 'none'})

corr_mat = all_data.corr(method='spearman', numeric_only=True)
correlation_tab = dcc.Tab(
    label="Correlation Matrix",
    children = [
    dcc.Graph(
        figure=px.imshow(
            corr_mat,
            text_auto=True,
            title="Feature Correlation Matrix",
            labels={"color": "Correlation"}
        ).update_layout(height=600)
    )
])

app = Dash()
app.layout = [
    html.Section([
        dcc.Store(id='selected-country', data=None),
        html.H1("Global Data Dashboard", style={'textAlign': 'center'}),
        dcc.Tabs(
            [map_tab, graphs_tab, dataset_tab, data_graphs, correlation_tab]
        ),
        
    ],style={'padding': '2rem'})
]
get_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)