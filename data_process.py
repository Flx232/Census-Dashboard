from load_data import run
import pandas as pd
import os

os.chdir(os.path.dirname(__file__))

AMALGAMATED_DATA = run()
IDB_DF = pd.read_csv("data/idb5yr.csv")
COUNTRIES_DF = pd.read_csv("data/countries_codes_and_coordinates.csv")
GDP_DF = pd.read_csv("data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_329227.csv")

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

def bin_lat():
    df = COUNTRIES_DF[['Alpha-2 code', 'Latitude (average)']]
    df.replace(r'"', '', regex=True, inplace=True)
    df['Latitude (average)'] = df['Latitude (average)'].str.strip()
    df['alpha2'] = df['Alpha-2 code'].str.strip()
    bins = [-90, 30, 90]
    labels = ['North', 'South']
    df['Latitude (average)'] = df['Latitude (average)'].astype(float)
    df['sphere'] = pd.cut(df['Latitude (average)'], bins=bins, labels=labels, right=False)
    return df