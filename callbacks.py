from dash import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from data_process import get_map_countries_data, format_gdp, get_country_data, bin_lat, AMALGAMATED_DATA, limit_map_countries_gdp_yr

def get_map_click_data(click_data, point_key, key):
    value = click_data['points'][0][point_key]
    country_data = get_country_data(key, value)
    return country_data

def get_country_name(df):
    return df['country_name'].unique()[0]

def handle_palestine(click_data, df, avg_keys=[]):
    alpha3 = click_data['points'][0]['location']
    if alpha3 == 'PSE':
        df = df.groupby('yr').sum(min_count=1).reset_index()
        for key in avg_keys:
            df[key] = df[key]/2
    return df

def get_callbacks(app):
    @app.callback(
        Output('map-dashboard', 'figure'),
        Input('year-slider', 'value')
    )
    def create_map(year):
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
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=40, b=0),
            title='GDP per Country')
        fig.update_geos(
            projection_type='natural earth',
            domain=dict(x=[0, 1], y=[0, 1]),
        )
        return fig

    def upper_limit_year(df, column_table, key):
        country_data = df.dropna(subset = [key])
        max_year = country_data['yr'].max()
        return column_table[column_table['yr'] <= max_year]

    def lower_limit_year(df, column_table, key):
        country_data = df.replace(0, np.nan)
        country_data = country_data.dropna(subset = [key])
        min_year = max(country_data['yr'].min(), column_table['yr'].min())
        return column_table[column_table['yr'] >= min_year]

    @app.callback(
        Output('selected-country', 'data'),
        Input('map-dashboard', 'clickData')
    )
    def store_alpha3(click_data):
        if click_data is None:
            return 'USA'
        return click_data['points'][0]['location']

    @app.callback(
        Output('gdp-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        prevent_initial_call=True
    )
    def create_country_gdp_line(click_data):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        gdp_country_data = country_data[['gdp', 'births', 'e0', 'yr']]
        gdp_country_data = handle_palestine(click_data, gdp_country_data, ['gdp', 'e0'])
        # gdp_country_data.dropna(inplace=True)
        gdp_country_data = upper_limit_year(country_data, gdp_country_data, 'gdp')
        gdp_country_data = lower_limit_year(country_data, gdp_country_data, 'gdp')
        full_years = range(
            int(gdp_country_data['yr'].min()),
            int(gdp_country_data['yr'].max()) + 1,
        )
        gdp_country_data = (
            gdp_country_data
            .set_index('yr')
            .reindex(full_years)
            .rename_axis('yr')
            .reset_index()
        )
        fig = px.line(
            gdp_country_data,
            x = 'yr',
            y = 'gdp',
            title = f'GDP vs Time (year)<br>{country_name}',
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

    @app.callback(
        Output('births-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        prevent_initial_call=True
    )
    def create_country_birth_line(click_data):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        births_country_data = country_data[['births', 'yr']]
        births_country_data.dropna(inplace=True)
        births_country_data = handle_palestine(click_data, births_country_data)
        # births_country_data = limit_year(country_data, births_country_data)
        births_country_data = lower_limit_year(country_data, births_country_data, 'births')
        full_years = range(
            int(births_country_data['yr'].min()),
            int(births_country_data['yr'].max()) + 1,
        )
        births_country_data = (
            births_country_data
            .set_index('yr')
            .reindex(full_years)
            .rename_axis('yr')
            .reset_index()
        )
        fig = px.line(
            births_country_data,
            x = 'yr',
            y = 'births',
            title = f'Births vs Time (year)<br>{country_name}'
        )
        fig.update_traces(connectgaps=False)
        return fig

    @app.callback(
        Output('pop-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        prevent_initial_call=True
    )
    def create_country_birth_line(click_data):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        pop_country_data = country_data[['pop', 'yr']]
        pop_country_data.dropna(inplace=True)
        pop_country_data = handle_palestine(click_data, pop_country_data)
        # births_country_data = limit_year(country_data, births_country_data)
        pop_country_data = lower_limit_year(country_data, pop_country_data, 'births')
        full_years = range(
            int(pop_country_data['yr'].min()),
            int(pop_country_data['yr'].max()) + 1,
        )
        pop_country_data = (
            pop_country_data
            .set_index('yr')
            .reindex(full_years)
            .rename_axis('yr')
            .reset_index()
        )
        fig = px.line(
            pop_country_data,
            x = 'yr',
            y = 'pop',
            title = f'Population vs Time (year)<br>{country_name}'
        )
        fig.update_traces(connectgaps=False)
        return fig

    @app.callback(
        Output('e0-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        prevent_initial_call=True
    )
    def create_country_e0_line(click_data):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        e0_country_data = country_data[['e0', 'yr']]
        e0_country_data = handle_palestine(click_data, e0_country_data, ['e0'])
        e0_country_data.dropna(inplace=True)
        # e0_country_data = limit_year(country_data, e0_country_data)
        return px.line(
            e0_country_data,
            x = 'yr',
            y = 'e0',
            title = f'Life expectancy at Birth vs Time (year)<br>{country_name}'
        )

    @app.callback(
        Output('pop-bar', 'figure'),
        Input('gdp-graph', 'clickData'),
        Input('selected-country', 'data')
    )
    def create_country_pop_histogram(click_data, alpha3):
        if click_data is None:
            gdp_map_data = limit_map_countries_gdp_yr()
            max_year = gdp_map_data['yr'].max()
            country_data = get_country_data('yr', max_year)
        else:
            country_data = get_map_click_data(click_data, 'x', 'yr')
        country_data = country_data[country_data['alpha3'] == alpha3]
        country_name = get_country_name(country_data)
        year = country_data['yr'].head(1).item()
        pop_country_data = country_data[['yr', 'pop_young', 'pop_middle', 'pop_old']]
        pop_country_data.dropna(inplace=True)
        pop_country_data = upper_limit_year(country_data, pop_country_data, 'gdp')
        pop_long = pop_country_data.melt(
            value_vars=['pop_young', 'pop_middle', 'pop_old'],
            var_name='age_group',
            value_name='population',
        )
        return px.bar(
            pop_long,
            x = 'age_group',
            y = 'population',
            title = f'Population Distribution by age<br>{country_name} ({year})'
        )

    @app.callback(
        Output('birth-age-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        Input('age-slider', 'value'),
        prevent_initial_call=True
    )
    def create_country_birth_age_line(click_data, year):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        births_data = country_data[['yr', 'births_young', 'births_middle']]
        births_data = handle_palestine(click_data, births_data)
        births_data = births_data.replace(0, np.nan)
        births_data = lower_limit_year(country_data, births_data, 'births_young')
        births_long = births_data.melt(
            id_vars='yr',
            value_vars=['births_young', 'births_middle'],
            var_name='age_group',
            value_name='births',
        )
        fig = px.line(
            births_long,
            x = 'yr',
            y = 'births',
            color='age_group',
            title = f'Woman\'s age when giving birth vs Time (year)<br>{country_name}'
        )
        vline_year = min(max(year, births_long['yr'].min()), births_long['yr'].max())
        fig.add_vline(x=vline_year, line_width=1, line_dash="dash", line_color="black")
        return fig

    @app.callback(
        Output('pop-age-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        Input('age-slider', 'value'),
        prevent_initial_call=True
    )
    def create_country_pop_age_line(click_data, year):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        pops_data = country_data[['yr', 'pop_young', 'pop_middle', 'pop_old']]
        pops_data = handle_palestine(click_data, pops_data)
        pops_data = pops_data.replace(0, np.nan)
        pops_data = lower_limit_year(country_data, pops_data, 'pop_young')
        full_years = range(
            int(pops_data['yr'].min()),
            int(pops_data['yr'].max()) + 1,
        )
        pops_data = (
            pops_data
            .set_index('yr')
            .reindex(full_years)
            .rename_axis('yr')
            .reset_index()
        )
        pops_long = pops_data.melt(
            id_vars='yr',
            value_vars=['pop_young', 'pop_middle', 'pop_old'],
            var_name='age_group',
            value_name='population',
        )
        fig = px.line(
            pops_long,
            x = 'yr',
            y = 'population',
            color='age_group',
            title = f'Population ages vs Time (year)<br>{country_name}'
        )
        vline_year = min(max(year, pops_data['yr'].min()), pops_data['yr'].max())
        fig.add_vline(x=vline_year, line_width=1, line_dash="dash", line_color="black")
        fig.update_traces(connectgaps=False)
        return fig

    @app.callback(
        Output('pop-increase-hist', 'figure'),
        Input('map-dashboard', 'clickData'),
        Input('date-slider', 'value'),
        prevent_initial_call=True
    )
    def create_country_pop_incr_hist(click_data, date_range):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        pop_incr_data = country_data[['yr', 'nim', 'natincr']]
        pop_incr_data = pop_incr_data[pop_incr_data['yr'].between(date_range[0], date_range[1])]
        pop_incr_data = handle_palestine(click_data, pop_incr_data)
        pop_incr_data = lower_limit_year(country_data, pop_incr_data, 'nim')
        full_years = range(
            int(pop_incr_data['yr'].min()),
            int(pop_incr_data['yr'].max()) + 1,
        )
        pop_incr_data = (
            pop_incr_data
            .set_index('yr')
            .reindex(full_years)
            .rename_axis('yr')
            .reset_index()
        )
        pops_long = pop_incr_data.melt(
            id_vars='yr',
            value_vars=['nim', 'natincr'],
            var_name='pop_increase_type',
            value_name='population',
        )
        fig = px.bar(
            pops_long,
            x = 'yr',
            y = 'population',
            color='pop_increase_type',
            title = f'Population Change vs Time (year)<br>{country_name}'
        )
        return fig

    @app.callback(
        Output('rate-graph', 'figure'),
        Input('map-dashboard', 'clickData'),
        Input('date-slider', 'value'),
        prevent_initial_call=True
    )
    def create_country_rate_line(click_data, date_range):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        rate_data = country_data[['yr', 'tfr', 'gr']]
        rate_data = handle_palestine(click_data, rate_data, ['tfr', 'gr'])
        rate_data = lower_limit_year(country_data, rate_data, 'tfr')
        rate_data = rate_data[rate_data['yr'].between(date_range[0], date_range[1])]
        full_years = range(
            int(rate_data['yr'].min()),
            int(rate_data['yr'].max()) + 1,
        )
        rate_data = (
            rate_data
            .set_index('yr')
            .reindex(full_years)
            .rename_axis('yr')
            .reset_index()
        )
        rate_long = rate_data.melt(
            id_vars='yr',
            value_vars=['tfr', 'gr'],
            var_name='pop_increase_type',
            value_name='population',
        )
        fig = px.line(
            rate_long,
            x = 'yr',
            y = 'population',
            color='pop_increase_type',
            title = f'Population Growth and Fertility Rate vs Time (year)<br>{country_name}'
        )
        return fig

    @app.callback(
        Output('date-slider', 'min'),
        Output('date-slider', 'max'),
        Output('date-slider', 'value'),
        Input('map-dashboard', 'clickData'),
        prevent_initial_call=True
    )
    def create_country_rate_line(click_data):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        rate_data = country_data[['yr', 'tfr', 'gr']]
        rate_data = rate_data.dropna()
        left_min, right_max = int(rate_data['yr'].min()), int(rate_data['yr'].max())
        return left_min, right_max, [left_min, right_max]

    @app.callback(
        Output('graphs', 'style'),
        Output('graphs', 'label'),
        Input('map-dashboard', 'clickData'),
        prevent_initial_call=True
    )
    def create_country_rate_line(click_data):
        if click_data is None:
            return None
        country_data = get_map_click_data(click_data, 'location', 'alpha3')
        country_name = get_country_name(country_data)
        return {}, f'{country_name} Graphs'

    @app.callback(
        Output('wealth-diff-world', 'figure'),
        Input('wealth-range-year-slider', 'value')
    )
    def create_wealth_diff_histo(years):
        country_info = bin_lat()
        df = AMALGAMATED_DATA[AMALGAMATED_DATA['yr'].between(years[0], years[1])]
        binned_df = df.merge(country_info, on='alpha2', how='inner')
        graph_df = binned_df[['yr', 'gdp', 'sphere']]
        return px.histogram(
            graph_df,
            x='yr',
            y='gdp',
            histfunc='sum',
            color = 'sphere',
            title='Collective sum of GDP vs Year<br>Between Countries above 30 degrees latitude (average) and countries below'
        )

    @app.callback(
        Output('gdp-cumulation', 'figure'),
        Input('wealth-range-year-slider', 'value')
    )
    def create_gdp_cumulation_hist(years):
        country_info = bin_lat()
        df = AMALGAMATED_DATA[AMALGAMATED_DATA['yr'].between(years[0], years[1])]
        binned_df = df.merge(country_info, on='alpha2', how='inner')
        graph_df = binned_df[['country_name', 'gdp', 'yr']]
        return px.histogram(
            graph_df,
            x='yr',
            y='gdp',
            histfunc='sum',
            color = 'country_name',
            title='Contribution to collective sum of GDP vs Year by each Country'
        )

    @app.callback(
        Output('scatter-world', 'figure'),
        Input('quant-dropdown', 'value'),
        Input('year-picker', 'value')
    )
    def create_gdp_cumulation_hist(quant_key, year):
        country_info = bin_lat()
        df = AMALGAMATED_DATA[AMALGAMATED_DATA['yr'] == year]
        binned_df = df.merge(country_info, on='alpha2', how='inner')
        graph_df = binned_df[['sphere', 'country_name', 'gdp', quant_key]]
        graph_df.dropna(subset=[quant_key], inplace=True)
        return px.scatter(
            graph_df,
            x='gdp',
            y=quant_key,
            size=quant_key,
            color = 'country_name',
            title=f'GDP vs {quant_key.capitalize()} ({year})',
        )