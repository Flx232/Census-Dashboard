import pandas as pd
import numpy as np

class Transformer:
    def remove_column(self, df, key):
        return df.drop(key, axis=1)

    def rename_column(self, df, keys, new_keys):
        if len(keys) != len(new_keys):
            print("Mismatched number of keys.")
            return df
        return df.rename(columns={keys[i]:new_keys[i] for i in range(len(keys))})

    def get_alpha2_from_geo_id(self, df):
        nation_code = df[df['GEO_ID'].str[0:3] == 'W14'].reset_index(drop=True)
        nation_code = nation_code.copy()
        nation_code['ALPHA2'] = nation_code['GEO_ID'].str[9:11]
        return nation_code

    def drop_dup(self, df):
        return df.drop_duplicates().reset_index(drop=True)

    def clean_cc_cn_data(self, cc_cn):
        cc_cn.replace(r'"', '', regex=True, inplace=True)
        cc_cn['Country'] = cc_cn['Country'].str.strip()
        cc_cn['Alpha-2 code'] = cc_cn['Alpha-2 code'].str.strip()
        cc_cn['Alpha-3 code'] = cc_cn['Alpha-3 code'].str.strip()
        return cc_cn

    def map_name_to_2_code(self, country_info, cc_cn):
        alpha2_country_map = cc_cn[['Alpha-2 code', 'Country']].set_index('Alpha-2 code')
        country_info['COUNTRY_NAME'] = country_info['ALPHA2'].map(alpha2_country_map.to_dict()['Country'])
        return country_info

    def map_3_code_to_name(self, country_info, cc_cn):
        country_alpha_3_map = cc_cn[['Country', 'Alpha-3 code']].set_index('Country')
        country_info['ALPHA3'] =country_info['COUNTRY_NAME'].map(country_alpha_3_map.to_dict()['Alpha-3 code'])
        return country_info

    def handle_palestine(self, df):
        df['COUNTRY_NAME'] = df['COUNTRY_NAME'].fillna('Palestinian Territory, Occupied')
        return df

    def convert_type(self, df, key, type):
        df[key] = df[key].astype(type)
        return df

    def map_id_to_alpha_2(self, country, country_info):
        alpha2_country_map = country[['country_id', 'alpha2']].set_index('alpha2')
        country_info['COUNTRY_ID'] = country_info['ALPHA2'].map(alpha2_country_map.to_dict()['country_id'])
        return country_info

    def merge_country_yr_df(self, country_yr, df):
        return df.merge(country_yr, on=['yr', 'country_id'], how='right')

    def melt_year(self, df):
        return pd.melt(df, id_vars=['Country Name', 'Country Code'], value_vars=[str(year) for year in range(1960, 2025)], var_name='YR', value_name='GDP').dropna()

    def map_id_to_alpha_3(self, country, country_info):
        alpha3_country_map = country[['country_id', 'alpha3']].set_index('alpha3')
        country_info['country_id'] = country_info['alpha3'].map(alpha3_country_map.to_dict()['country_id'])
        return country_info

    def drop_na(self, df, subset=None):
        if subset is None:
            return df.dropna()
        return df.dropna(subset=subset)


class ETLProcessor:
    def __init__(
        self,
        cnx,
        csv_paths,
        sql_queries,
        transformer: Transformer,
    ):
        self._cnx = cnx
        self._transformer = transformer
        self._csv_paths = csv_paths
        self._sql_queries = sql_queries
    
    def extract_csv(self):
        if len(self._csv_paths) == 1:
            return pd.read_csv(self._csv_paths[0])
        else:
            return (pd.read_csv(csv_path) for csv_path in self._csv_paths)

    def extract_sql(self):
        if self._sql_queries is None:
            return
        if len(self._sql_queries) == 1:
            return pd.read_sql(self._sql_queries[0], self._cnx)
        else:
            return [pd.read_sql(sql_query, self._cnx) for sql_query in self._sql_queries]


    def extract(self):
        df = self.extract_csv()[0]
        return df

    def load(self, df, table):
        df.to_sql(
            table, 
            self._cnx, 
            if_exists="append", 
            index=False, 
            schema="pop_census"
        )


class CountryETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        super().__init__(cnx, csv_paths, None, transformer)

    def extract(self):
        country_names, idb5yr = self.extract_csv()
        return country_names, idb5yr

    def transform(self, country_names, idb5yr):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = self._transformer.get_alpha2_from_geo_id(geo_code)
        country_info = self._transformer.drop_dup(country_info)
        country_names = self._transformer.clean_cc_cn_data(country_names)
        df = self._transformer.map_name_to_2_code(country_info, country_names)
        df = self._transformer.handle_palestine(df)
        df = self._transformer.map_3_code_to_name(df, country_names)
        df = self._transformer.remove_column(df, 'GEO_ID')
        df = self._transformer.rename_column(df, ['AREA_KM2'], ['AREA'])
        columns = df.columns
        df = self._transformer.rename_column(df, columns, [column.lower() for column in columns])
        df = self._transformer.convert_type(df, 'area', int)
        return df

    def process(self):
        country_names, idb5yr = self.extract()
        df = self.transform(country_names, idb5yr)
        self.load(df, 'country')


class CountryYrETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        self.sql_queries = ["select * from country;"]
        super().__init__(cnx, csv_paths, self.sql_queries, transformer)

    def extract(self):
        idb5yr = self.extract_csv()
        countries = self.extract_sql()
        return countries, idb5yr

    def transform(self, countries, idb5yr):
        idb5yr = self._transformer.get_alpha2_from_geo_id(idb5yr)
        df = self._transformer.map_id_to_alpha_2(countries, idb5yr)
        df = df[['YR', 'COUNTRY_ID']]
        columns = df.columns
        df = self._transformer.rename_column(df, columns, [column.lower() for column in columns])
        return df

    def process(self):
        countries, idb5yr = self.extract()
        df = self.transform(countries, idb5yr)
        self.load(df, 'country_yr')


class CountryYrIDB5YrETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, columns, transformer, table):
        self.sql_queries = [
            "select * from country;",
            "select * from country_yr;"
        ]
        super().__init__(cnx, csv_paths, self.sql_queries, transformer)
        self._columns = columns
        self._table = table

    def extract(self):
        idb5yr = self.extract_csv()
        country, country_yr = self.extract_sql()
        return country, country_yr, idb5yr

    def transform(self, country, country_yr, idb5yr):
        df = self._transformer.get_alpha2_from_geo_id(idb5yr)
        df = self._transformer.map_id_to_alpha_2(country, df)
        df = self._transformer.rename_column(df, ['YR', 'COUNTRY_ID'], ['yr', 'country_id'])
        df = self._transformer.merge_country_yr_df(country_yr, df)
        df = self._transformer.drop_dup(df)
        self._columns.append('country_yr_id')
        df = df[self._columns]
        columns = df.columns
        df = self._transformer.rename_column(df, columns, [column.lower() for column in columns])
        # df = self._transformer.drop_na(df)
        return df

    def process(self):
        country, country_yr, idb5yr = self.extract()
        df = self.transform(country, country_yr, idb5yr)
        self.load(df, self._table)


class GDPDataETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        self.sql_queries = [
            """select * from country;""",
            """select * from country_yr;"""
        ]
        super().__init__(cnx, csv_paths, self.sql_queries, transformer)

    def extract(self):
        gdp = self.extract_csv()
        country, country_yr = self.extract_sql()
        return country, country_yr, gdp

    def transform(self, country, country_yr, gdp):
        df = self._transformer.melt_year(gdp)
        df = self._transformer.rename_column(df, ['YR', 'Country Code'], ['yr', 'alpha3'])
        df = self._transformer.map_id_to_alpha_3(country, df)
        df = self._transformer.convert_type(df, 'yr', int)
        df = self._transformer.merge_country_yr_df(country_yr, df)
        df = self._transformer.drop_dup(df)
        df = self._transformer.drop_na(df)
        df = df[['country_yr_id', 'GDP']]
        columns = df.columns
        df = self._transformer.rename_column(df, columns, [column.lower() for column in columns])
        return df

    def process(self):
        country, country_yr, gdp = self.extract()
        df = self.transform(country, country_yr, gdp)
        self.load(df, 'gdp_data')


class AgeDataETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        self.sql_queries = [
            """select * from country;""",
            """select * from country_yr;"""
        ]
        super().__init__(cnx, csv_paths, self.sql_queries, transformer)

    def extract(self):
        idb5yr = self.extract_csv()
        country, country_yr = self.extract_sql()
        return country, country_yr, idb5yr

    def transform(self, country, country_yr, idb5yr):
        df = self._transformer.get_alpha2_from_geo_id(idb5yr)
        df = self._transformer.map_id_to_alpha_2(country, df)
        df = self._transformer.rename_column(df, ['YR', 'COUNTRY_ID'], ['yr', 'country_id'])
        df['POP_YOUNG'] = df[['POP0_4', 'POP5_9', 'POP10_14', 'POP15_19', 'POP20_24', 'POP25_29']].sum(axis=1)
        df['POP_MIDDLE'] = df[['POP30_34', 'POP35_39', 'POP40_44', 'POP45_49', 'POP50_54', 'POP55_59']].sum(axis=1)
        df['POP_OLD'] = df[['POP60_64', 'POP65_69', 'POP70_74', 'POP75_79', 'POP80_84', 'POP85_89', 'POP90_94', 'POP95_99', 'POP100_']].sum(axis=1)
        df['BIRTHS_YOUNG'] = df[['BIRTHS15_19', 'BIRTHS20_24', 'BIRTHS25_29']].sum(axis=1)
        df['BIRTHS_MIDDLE'] = df[['BIRTHS30_34', 'BIRTHS35_39', 'BIRTHS40_44', 'BIRTHS45_49']].sum(axis=1)
        df = self._transformer.merge_country_yr_df(country_yr, df)
        df = self._transformer.drop_dup(df)
        columns = ['country_yr_id', 'POP_YOUNG', 'POP_MIDDLE', 'POP_OLD', 'BIRTHS_YOUNG', 'BIRTHS_MIDDLE']
        df = df[columns]
        # df = df.replace(0, np.nan)
        df = self._transformer.rename_column(df, columns, [column.lower() for column in columns])
        return df

    def process(self):
        country, country_yr, idb5yr = self.extract()
        df = self.transform(country, country_yr, idb5yr)
        self.load(df, 'age_data')