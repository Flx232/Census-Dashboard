from load_data import run
import pandas as pd

AMALGAMATED_DATA = run()

def get_valid_gdp_yr(df):
    if 'gdp' in df:
        return df.dropna(subset=['gdp'])
    return df

def get_map_countries_data():
    df = AMALGAMATED_DATA[['alpha2', 'alpha3', 'country_name', 'gdp', 'yr']]
    # df = df.dropna(subset=['gdp'])
    return df

def limit_map_countries_gdp_yr():
    df = get_map_countries_data()
    return get_valid_gdp_yr(df)

def format_gdp(value):
    abs_v = abs(value)
    if abs_v == 0:
        return 'NAN'
    if abs_v >= 1e12:
        return f"{value / 1e12:.1f} Trillion"
    if abs_v >= 1e9:
        return f"{value / 1e9:.1f} Billion"
    if abs_v >= 1e6:
        return f"{value / 1e6:.1f} Million"
    if abs_v >= 1e3:
        return f"{value / 1e3:.1f} Thousand"
    return f"{value:.0f}"

def get_country_data(key, value):
    df = AMALGAMATED_DATA[AMALGAMATED_DATA[key] == value]
    return df