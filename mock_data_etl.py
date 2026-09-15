import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
def generate_idb5yr():
    idb5yr_df = pd.read_csv(os.path.join(DATA_DIR, 'idb5yr.csv'))
    country_id = idb5yr_df[idb5yr_df['GEO_ID'].str[:3] == 'W14'].sample(12, random_state = 100)
    region_id = idb5yr_df[idb5yr_df['GEO_ID'].str[:3] != 'W14'].sample(2, random_state = 100)
    dup_id = country_id['GEO_ID'].sample(1, random_state=100).iloc[0]
    dup_rows = country_id[country_id['GEO_ID'] == dup_id].sample(1, random_state=69)
    mock = pd.concat([country_id, region_id, dup_rows])
    return mock.sample(frac=1, random_state=60).reset_index(drop=True)

def generate_cc_cn():
    return pd.DataFrame({
        "Country": [
            "\"Cayman Islands\"", "\"Singapore\"", 
            "\"Palestinian Territory, Occupied\"", "\"Turkmenistan\"", 
            "\"Cape Verde\"", "\"Ukraine\"","\"Belgium\"", "\"Hong Kong\"",
            "\"Cuba\"", "\"Canada\"", "\"Sri Lanka\"", "\"Samoa\""],
        "Alpha-2 code": ["\"KY\"", "SG\"", "PS\"", "\"TM\"", "\"CV\"", "\"UA\"", "\"BE\"", "\"HK\"", "\"CU\"", "\"CA\"", "\"LK\"", "\"WS\""],
        "Alpha-3 code": ["\"CYM\"", "\"SGP\"", "\"PSE\"", "\"TKM\"", "\"CPV\"", "\"UKR\"", "\"BEL\"", "\"HKG\"", "\"CUB\"", "\"CAN\"", "\"LKA\"", "\"WSM\""],
        "Numeric code": ["136", "702", "275", "795", "132", "804", "56", "344", "192", "124", "144", "882"],
        "Latitude Average": ["19.5", "1.3667", "32", "40", "16", "49", "50.8333", "22.25", "21.5", "60", "7", "-13.5833"],
        "Longitude Average": ["-80.5", "103.8", "35.25", "60", "-24", "32", "4", "114.1667", "-80", "-95", "81", "-172.3333"],
    })

def generate_countries():
    return pd.DataFrame({
        "country_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "country_name": [
            "Cayman Islands", "Singapore", 
            "Palestinian Territory, Occupied", "Turkmenistan", 
            "Cape Verde", "Ukraine","Belgium", "Hong Kong",
            "Cuba", "Canada", "Sri Lanka", "Samoa"],
        "alpha2": ["KY", "SG", "XW", "TM", "CV", "UA", "BE", "HK", "CU", "CA", "LK", "WS"],
        "alpha3": ["CYM", "SGP", "PSE", "TKM", "CPV", "UKR", "BEL", "HKG", "CUB", "CAN", "LKA", "WSM"],
        "area": [264, 709, 5640, 469930, 4033, 579330, 30278, 1073, 109820, 9093507, 64630, 2821]
    })

def generate_country_yr():
    return pd.DataFrame({
        "country_yr_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        "country_id": [1, 2, 3, 4, 5, 6, 7, 6, 8, 9, 10, 11, 12],
        "yr": [1954, 2069, 2028, 2056, 1986, 1963, 2020, 1963, 1955, 2025, 1957, 2086, 2078]
    })

def generate_gdp():
    gdp_df = pd.read_csv(os.path.join(DATA_DIR, 'API_NY.GDP.MKTP.CD_DS2_en_csv_v2_329227.csv'))
    return gdp_df[gdp_df['Country Code'].isin(['BEL','CAN','CPV','CUB','CYM','HKG','LKA','PSE','SGP','TKM','UKR','WSM'])]
    