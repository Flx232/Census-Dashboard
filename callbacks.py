from dash import Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from data_process import get_map_countries_data, format_gdp, get_country_data

def get_map_click_data(click_data, point_key, key):
    value = click_data['points'][0][point_key]
    country_data = get_country_data(key, value)
    return country_data

def get_country_name(df):
    return df['country_name'].unique()[0]

def get_callbacks(app):
    @app.callback(
        Output('map-dashboard', 'figure'),
        Input('year-slider', 'value')
    )
    def create_company_scatter(year):
        gdp_map_data = get_map_countries_data()
        year_data = gdp_map_data[gdp_map_data['yr'] == year]
        year_data['gdp'] = year_data['gdp'].fillna(0)
        bins = [0, 0.1, 0.26e12, 1.04e12, 2.56e12, 5.05e12, float('inf')]
        labels = ['NaN', '< $0.26T', '$0.26–1.04T', '$1.04–2.56T', '$2.56–5.05T', '≥ $5.05T']
        year_data['gdp_bin'] = pd.cut(year_data['gdp'], bins=bins, labels=labels, right=False)
        year_data['gdp_code'] = year_data['gdp_bin'].cat.codes

        year_data['gdp_english'] = year_data['gdp'].apply(format_gdp)

        fig = go.Figure()
        fig.add_choropleth(
            colorbar=dict(
                title='GDP (USD)',
                tickvals=[0, 1, 2, 3, 4],
                ticktext=labels,
                len=0.7,
            ),
            locations=year_data['alpha3'],
            locationmode='ISO-3',
            z=year_data['gdp_code'],
            zmin=0, zmax=4,
            colorscale=[
                [0.00, "#ffffff"],
                [0.01, "#8cadcc"],
                [0.25, "#569dc3"],
                [0.50, "#2b6f9b"],
                [0.75, "#0F4777"],
                [1.00, "#041938"],
            ],
            customdata=year_data[['country_name', 'gdp_english', 'gdp', 'yr']].to_numpy(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "GDP: $%{customdata[1]}<br>"
                "<extra></extra>"
            ),
        )
        fig.update_layout(title='GDP per Country')
        return fig

    @app.callback(
        Output('selected-country', 'data'),
        Input('map-dashboard', 'clickData')
    )
    def store_alpha3(click_data):
        if click_data is None:
            return
        return click_data['points'][0]['location']

    @app.callback(
        Output('gdp-graph', 'figure'),
        Input('map-dashboard', 'clickData')
    )
    def create_country_gdp_line(click_data):
        if click_data is None:
            return
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        gdp_country_data = country_data[['gdp', 'births', 'e0', 'yr']]
        gdp_country_data.dropna(inplace=True)
        fig = px.line(
            gdp_country_data,
            x = 'yr',
            y = 'gdp',
            title = f'GDP vs Time (year) of {country_name}',
            custom_data = ['births', 'e0'],
        )
        fig.update_traces(
            hovertemplate=(
                "Yr: %{x}<br>"
                "GDP: $%{y}<br>"
                "Births: %{customdata[0]}<br>"
                "E0: %{customdata[1]}<br>"
                "<extra></extra>"
            )
        )
        return fig

    def limit_year(df, column_table):
        gdp_country_data = df.dropna(subset = ['gdp'])
        max_year = gdp_country_data['yr'].max()
        return column_table[column_table['yr'] <= max_year]

    @app.callback(
        Output('births-graph', 'figure'),
        Input('map-dashboard', 'clickData')
    )
    def create_country_birth_line(click_data):
        if click_data is None:
            return
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        births_country_data = country_data[['births', 'yr']]
        births_country_data.dropna(inplace=True)
        births_country_data = limit_year(country_data, births_country_data)
        return px.line(
            births_country_data,
            x = 'yr',
            y = 'births',
            title = f'Births vs Time (year) of {country_name}'
        )

    @app.callback(
        Output('e0-graph', 'figure'),
        Input('map-dashboard', 'clickData')
    )
    def create_country_e0_line(click_data):
        if click_data is None:
            return
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        e0_country_data = country_data[['e0', 'yr']]
        e0_country_data.dropna(inplace=True)
        e0_country_data = limit_year(country_data, e0_country_data)
        return px.line(
            e0_country_data,
            x = 'yr',
            y = 'e0',
            title = f'Life expectancy at Birth vs Time (year) of {country_name}'
        )

    @app.callback(
        Output('pop-bar', 'figure'),
        Input('gdp-graph', 'clickData'),
        Input('selected-country', 'data'),
    )
    def create_country_pop_histogram(click_data, alpha3):
        if click_data is None:
            return
        country_data = get_map_click_data(click_data, 'x', 'yr')
        country_data = country_data[country_data['alpha3'] == alpha3]
        country_name = get_country_name(country_data)
        year = country_data['yr'].head(1)
        pop_country_data = country_data[['yr', 'pop_young', 'pop_middle', 'pop_old']]
        pop_country_data.dropna(inplace=True)
        pop_country_data = limit_year(country_data, pop_country_data)
        pop_long = pop_country_data.melt(
            value_vars=['pop_young', 'pop_middle', 'pop_old'],
            var_name='age_group',
            value_name='population',
        )
        return px.bar(
            pop_long,
            x = 'age_group',
            y = 'population',
            title = f'Population Distribution by age of {country_name} ({year})'
        )

    @app.callback(
        Output('birth-age-graph', 'figure'),
        Input('map-dashboard', 'clickData')
    )
    def create_country_birth_age_line(click_data):
        if click_data is None:
            return
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        e0_country_data = country_data[['birth_young', 'birth_old']]
        e0_country_data.dropna(inplace=True)
        e0_country_data = limit_year(country_data, e0_country_data)
        return px.line(
            e0_country_data,
            x = 'yr',
            y = 'e0',
            title = f'Life expectancy at Birth vs Time (year) of {country_name}'
        )
#     @app.callback(
#         Output('stock_line_graph', 'figure'),
#         Input('multi_stock_symbol_dropdown', 'value')
#     )
#     def create_stock_line_graph(symbols):
#         df = STOCKS_DF.copy()
#         if symbols:
#             if type(symbols) != list:
#                 symbols = [symbols]
#             df = df[df["Symbol"].isin(symbols)]
#         return px.line(
#             df,
#             x="Date",
#             y="Close",
#             color="Symbol",
#             title="Stock Date vs Close Price"
#         )

#     @app.callback(
#         Output('merged_stock_graph', 'figure'),
#         Input('date_picker_range', 'start_date'),
#         Input('date_picker_range', 'end_date'),
#         Input('window', 'value')
#     )
#     def create_stock_line_graph(start_date, end_date, window):
#         df = GROUPED_DF.copy()
#         df['Date'] = pd.to_datetime(df['Date'])
#         if start_date:
#             start_date = pd.to_datetime(start_date)
#             df = df[df['Date'] >= start_date]
#         if end_date:
#             end_date = pd.to_datetime(end_date)
#             df = df[df['Date'] <= end_date]
#         # df['Rollingclose'] = df[['Close']].apply(lambda x: x.rolling(window=window, min_periods=1).mean())['Close']
#         df['Rollingclose'] = df.groupby('Sector',group_keys=False)['Close'].apply(lambda x: x.rolling(window=window, min_periods=1).mean())
#         # df['Rollingclose'] = df.groupby('Sector')['Close'].transform(lambda x: x.rolling(window=window, min_periods=1).mean())
#         fig = px.line(
#             df,
#             x="Date",
#             y="Rollingclose",
#             color="Sector",
#             title="Stock Date vs Average Close Price by Sector",
#             hover_name=df['Sector']
#         )
#         fig.update_traces(showlegend=True)
#         fig.update_layout(
#             legend=dict(
#                 title="Sector",
#                 orientation="v",
#                 yanchor="top",
#                 y=0.99,
#                 xanchor="left",
#                 x=0.01,
#                 bgcolor="rgba(255,255,255,0.8)",
#                 font=dict(size=10)
#             ),
#         )
#         return fig

#     @app.callback(
#         Output('hover_graph_histogram', 'figure'),
#         Input('merged_stock_graph', 'hoverData')
#     )
#     def update_hover_graph_histogram(hover_data):
#         sector = hover_data['points'][0]['hovertext']
#         date = hover_data['points'][0]['x']
#         df = MERGED_DF.copy()
#         df['Year'] = pd.to_datetime(df['Date']).dt.year
#         if sector:
#             df = df[df['Sector'] == sector]
#         if date:
#             year = pd.to_datetime(date).year
#             df = df[df['Year'] == year]
#         return px.histogram(
#             df,
#             x="Symbol",
#             y="Currentprice",
#             histfunc="avg",
#             color="Sector",
#             title=f"Average Current Price by Symbol ({year})"
#         )

#     @app.callback(
#         Output('hover_graph_scatter', 'figure'),
#         Input('merged_stock_graph', 'hoverData')
#     )
#     def update_hover_graph_scatter(hover_data):
#         sector = hover_data['points'][0]['hovertext']
#         date = hover_data['points'][0]['x']
#         df = MERGED_DF.copy()
#         df['Year'] = pd.to_datetime(df['Date']).dt.year
#         if sector:
#             df = df[df['Sector'] == sector]
#         if date:
#             date = pd.to_datetime(date).year
#             df = df[df['Year'] == date]
#         df = df.groupby('Symbol', as_index=False).agg({'Marketcap': 'mean', 'Close': 'max'})
#         return px.scatter(
#             df,
#             x="Marketcap",
#             y="Close",
#             color="Symbol",
#             size="Marketcap",
#             title=f"Avg Market Cap vs Max Close Price<br>{sector}"
#         )

#     @app.callback(
#         Output('s&p500_graph', 'figure'),
#         Input('monthly_forcast', 'value')
#     )
#     def create_snp500_graph(forecast_window):
#         df = INDEX_DF.copy()
#         df['Date'] = pd.to_datetime(df['Date'])
#         data = df[df['Date'] >= pd.Timestamp('2020-01-01')]
#         data = data.set_index('Date')
#         monthly_data = data.resample('ME').mean()
#         forecast = get_arima_model(monthly_data, forecast_window)
#         last_date = monthly_data.index[-1]
#         forecast_dates = pd.date_range(
#             start=last_date,
#             periods=forecast_window,
#             freq='ME'
#         )
#         # total_data = df.set_index('Date')
#         # monthly_total_data = total_data.resample('ME').mean()
#         # fc = pd.DataFrame(forecast)
#         fig = go.Figure()
#         fig.add_traces(go.Scatter(
#             x=monthly_data.index,
#             y=monthly_data['S&P500'],
#             mode='lines',
#             name='Observed',
#             line=dict(color='blue', width=2)
#         ))
#         fig.add_trace(go.Scatter(
#             x=forecast_dates,
#             y=forecast,
#             mode='lines',
#             name='Forecast',
#             line=dict(color='red', width=2)
#         ))
#         fig.update_layout(
#             title='ARIMA Forecast for S&P 500 Price Level',
#             xaxis_title='Date (Monthly)',
#             yaxis_title='S&P 500 Average Value',
#             legend=dict(x=0.02, y=0.98)
#         )
#         return fig

#     @app.callback(
#         Output('return_volatility', 'figure'),
#         Input('date_picker_range_volatility', 'start_date'),
#         Input('date_picker_range_volatility', 'end_date'),
#     )
#     def create_returns_volatility_graph(start_date, end_date):
#         df = get_volatility_returns()
#         if start_date and end_date:
#             df = df.loc[start_date:end_date]
#         fig = go.Figure()
#         fig.add_traces(go.Scatter(
#             x=df.index,
#             y=df['returns'],
#             mode='lines',
#             name='Returns',
#             line=dict(color='blue', width=2)
#         ))
#         fig.add_trace(go.Scatter(
#             x=df.index,
#             y=df['volatility'],
#             mode='lines',
#             name='Volatility',
#             line=dict(color='red', width=2)
#         ))
#         fig.update_layout(
#             title='Returns and Volatility for S&P 500',
#             xaxis_title='Date (Daily)',
#             yaxis_title='S&P500 Value',
#             legend=dict(x=0.02, y=0.98)
#         )
#         return fig

#     @app.callback(
#         Output('components_graph', 'figure'),
#         Input('date_picker_range_components', 'start_date'),
#         Input('date_picker_range_components', 'end_date')
#     )
#     def create_returns_volatility_graph(start_date, end_date):
#         contributions = get_stock_components()
        
#         if start_date and end_date:
#             start_date = pd.to_datetime(start_date)
#             end_date = pd.to_datetime(end_date)
#             contributions = contributions[contributions['Date'].between(start_date, end_date)]
#         fig = px.line(
#             data_frame=contributions,
#             x='Date',
#             y='Contribution',
#             color='Sector',
#             title='Contribution to Daily Returns of S&P500 by Sector'
#         )
#         return fig