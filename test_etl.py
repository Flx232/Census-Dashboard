import pandas as pd
import numpy as np
import pytest
from unittest.mock import MagicMock
from etl import ETLProcessor, CountryETLProcessor, CountryYrETLProcessor, CountryYrIDB5YrETLProcessor, GDPDataETLProcessor, AgeDataETLProcessor
from etl import Transformer
from mock_data_etl import generate_idb5yr, generate_cc_cn, generate_countries, generate_country_yr, generate_gdp

@pytest.fixture
def idb5yr():
    return generate_idb5yr()

@pytest.fixture
def cc_cn():
    return generate_cc_cn()

@pytest.fixture
def countries():
    return generate_countries()

@pytest.fixture
def country_yr():
    return generate_country_yr()

@pytest.fixture
def gdp():
    return generate_gdp()

@pytest.fixture
def transformer():
    return Transformer()

def generate_etl_processor():
    processor = ETLProcessor(
        None,
        None,
        None,
        Transformer(),
    )
    processor.extract_csv = MagicMock(return_value=[generate_idb5yr()])
    return processor

def generate_country_etl_processor():
    processor = CountryETLProcessor(
        None,
        None,
        Transformer(),
    )
    processor.extract_csv = MagicMock(return_value=[generate_cc_cn(), generate_idb5yr()])
    return processor

def generate_country_yr_etl_processor():
    processor = CountryYrETLProcessor(
        None,
        None,
        Transformer(),
    )
    processor.extract_csv = MagicMock(return_value=[generate_idb5yr()])
    processor.extract_sql = MagicMock(return_value=generate_countries())
    return processor

def generate_country_yr_IDB5Yr_etl_processor():
    processor = CountryYrIDB5YrETLProcessor(
        None,
        None,
        ['NIM', 'SEXRATIO', 'NATINCR', 'DEATHS'],
        Transformer(),
        ''
    )
    processor.extract_csv = MagicMock(return_value=[generate_idb5yr()])
    processor.extract_sql = MagicMock(return_value=[generate_countries(), generate_country_yr()])
    return processor

def generate_gdp_etl_processor():
    processor = GDPDataETLProcessor(
        None,
        None,
        Transformer()
    )
    processor.extract_csv = MagicMock(return_value=[generate_gdp()])
    processor.extract_sql = MagicMock(return_value=[generate_countries(), generate_country_yr()])
    return processor

def generate_age_etl_processor():
    processor = AgeDataETLProcessor(
        None,
        None,
        Transformer()
    )
    processor.extract_csv = MagicMock(return_value=[generate_idb5yr()])
    processor.extract_sql = MagicMock(return_value=[generate_countries(), generate_country_yr()])
    return processor


class TestTransformer:
    def test_get_alpha2_from_geo_id(self, transformer, idb5yr):
        length = len(idb5yr)
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        num_columns = len(geo_code.columns)
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        assert len(country_info) == length-2
        assert len(country_info.columns) == num_columns+1
        assert country_info['GEO_ID'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
        assert country_info['AREA_KM2'].dtype == float
        assert country_info['ALPHA2'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
        assert len(country_info['ALPHA2'].head(1).item()) == 2

    def test_clean_cc_cn_data(self, transformer, cc_cn):
        length = len(cc_cn)
        num_columns = len(cc_cn.columns)
        df = transformer.clean_cc_cn_data(cc_cn)
        assert len(df) == length
        assert len(df.columns) == num_columns
        assert df['Alpha-2 code'].head(1).item() == 'KY'
        assert df['Alpha-3 code'].head(1).item() == 'CYM'
        assert df['Country'].head(1).item() == 'Cayman Islands'

    def test_map_name_to_2_code(self, transformer, idb5yr, cc_cn):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        country_names = transformer.clean_cc_cn_data(cc_cn)
        length = len(country_info)
        num_columns = len(country_info.columns)
        df = transformer.map_name_to_2_code(country_info, country_names)
        assert len(df) == length
        assert len(df.columns) == num_columns + 1
        assert df['COUNTRY_NAME'].dtype == pd.StringDtype(storage='python', na_value=np.nan)

    def test_handle_palestine(self, transformer, idb5yr, cc_cn):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        country_names = transformer.clean_cc_cn_data(cc_cn)
        df = transformer.map_name_to_2_code(country_info, country_names)
        length = len(country_info)
        num_columns = len(country_info.columns)
        df = transformer.handle_palestine(df)
        assert len(df) == length
        assert len(df.columns) == num_columns
        assert df['COUNTRY_NAME'].isna().any() == False

    def test_map_3_code_to_name(self, transformer, idb5yr, cc_cn):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        country_names = transformer.clean_cc_cn_data(cc_cn)
        df = transformer.map_name_to_2_code(country_info, country_names)
        df = transformer.handle_palestine(df)
        length = len(country_info)
        num_columns = len(country_info.columns)
        df = transformer.map_3_code_to_name(df, country_names)
        assert len(df) == length
        assert len(df.columns) == num_columns + 1
        assert df['ALPHA3'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
        assert len(df['ALPHA3'].head(1).item()) == 3

    def test_remove_column(self, transformer, idb5yr, cc_cn):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        country_names = transformer.clean_cc_cn_data(cc_cn)
        df = transformer.map_name_to_2_code(country_info, country_names)
        df = transformer.handle_palestine(df)
        df = transformer.map_3_code_to_name(df, country_names)
        length = len(df)
        num_columns = len(df.columns)
        df = transformer.remove_column(df, 'GEO_ID')
        assert len(df) == length
        assert len(df.columns) == num_columns-1

    def test_rename_column(self, transformer, idb5yr, cc_cn):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        country_names = transformer.clean_cc_cn_data(cc_cn)
        df = transformer.map_name_to_2_code(country_info, country_names)
        df = transformer.handle_palestine(df)
        df = transformer.map_3_code_to_name(df, country_names)
        df = transformer.remove_column(df, 'GEO_ID')
        length = len(df)
        num_columns = len(df.columns)
        df = transformer.rename_column(df, ['AREA_KM2'], ['AREA'])
        columns = df.columns
        df = transformer.rename_column(df, columns, [column.lower() for column in columns])
        assert len(df) == length
        assert len(df.columns) == num_columns
        assert (df.columns == ['area', 'alpha2', 'country_name', 'alpha3']).all() == True

    def test_convert_type(self, transformer, idb5yr, cc_cn):
        geo_code = idb5yr[['GEO_ID', 'AREA_KM2']]
        country_info = transformer.get_alpha2_from_geo_id(geo_code)
        country_names = transformer.clean_cc_cn_data(cc_cn)
        df = transformer.map_name_to_2_code(country_info, country_names)
        df = transformer.handle_palestine(df)
        df = transformer.map_3_code_to_name(df, country_names)
        df = transformer.remove_column(df, 'GEO_ID')
        df = transformer.rename_column(df, ['AREA_KM2'], ['AREA'])
        columns = df.columns
        df = transformer.rename_column(df, columns, [column.lower() for column in columns])
        df = transformer.convert_type(df, 'area', int)
        assert df['area'].dtype == int

    def test_map_id_to_alpha_2(self, transformer, countries, idb5yr):
        idb5yr = transformer.get_alpha2_from_geo_id(idb5yr)
        length = len(idb5yr)
        df = transformer.map_id_to_alpha_2(countries, idb5yr)
        assert len(df) == length
        assert 'COUNTRY_ID' in df.columns
        assert df['COUNTRY_ID'].dtype == int

    def test_merge_country_yr_df(self, transformer, countries, country_yr, idb5yr):
        length = len(idb5yr)
        idb5yr = transformer.get_alpha2_from_geo_id(idb5yr)
        df = transformer.map_id_to_alpha_2(countries, idb5yr)
        df = transformer.rename_column(df, ['YR', 'COUNTRY_ID'], ['yr', 'country_id'])
        df = transformer.merge_country_yr_df(country_yr, df)
        assert len(df) == length
        assert 'country_id' in df.columns
        assert df['country_id'].dtype == int

    def test_drop_dup(self, transformer, countries, country_yr, idb5yr):
        length = len(idb5yr)
        idb5yr = transformer.get_alpha2_from_geo_id(idb5yr)
        df = transformer.map_id_to_alpha_2(countries, idb5yr)
        df = transformer.rename_column(df, ['YR', 'COUNTRY_ID'], ['yr', 'country_id'])
        df = transformer.merge_country_yr_df(country_yr, df)
        df = transformer.drop_dup(df)
        assert len(df) == length-2
    
    def test_drop_na(self, transformer, countries, country_yr, idb5yr):
        idb5yr = transformer.get_alpha2_from_geo_id(idb5yr)
        df = transformer.map_id_to_alpha_2(countries, idb5yr)
        df = transformer.rename_column(df, ['YR', 'COUNTRY_ID'], ['yr', 'country_id'])
        df = transformer.merge_country_yr_df(country_yr, df)
        df = transformer.drop_dup(df)
        df = transformer.drop_na(df)
        assert len(df) == 8

    def test_melt_year(self, transformer, gdp):
        df = transformer.melt_year(gdp)
        assert len(df.columns) == 4
        assert 'YR' in df.columns
        assert df['YR'].dtype == pd.StringDtype(storage='python', na_value=np.nan)

    def test_map_id_to_alpha_3(self, transformer, countries, gdp):
        df = transformer.melt_year(gdp)
        length = len(df)
        df = transformer.rename_column(df, ['YR', 'Country Code'], ['yr', 'alpha3'])
        df = transformer.map_id_to_alpha_3(countries, df)
        assert len(df) == length
        assert 'country_id' in df.columns
        assert df['country_id'].dtype == int


class TestETLProcessor:
    processor = generate_etl_processor()
    def test_extract(self):
        df = self.processor.extract()
        assert(len(df)) == 15


class TestCountryETLProcessor:
    processor = generate_country_etl_processor()
    def test_extract(self):
        country_names, idb5yr = self.processor.extract()
        assert len(country_names) == 12
        assert len(idb5yr) == 15

    def test_transform(self):
        country_names, idb5yr = self.processor.extract()
        df = self.processor.transform(country_names, idb5yr)
        assert len(df) == 12
        assert len(df.columns) == 4
        assert (df.columns == ['area', 'alpha2', 'country_name', 'alpha3']).all() == True
        assert df['area'].dtype == int
        assert df['alpha2'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
        assert df['country_name'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
        assert df['alpha3'].dtype == pd.StringDtype(storage='python', na_value=np.nan)


class TestCountryYrETLProcessor:
    processor = generate_country_yr_etl_processor()
    def test_extract(self):
        countries, idb5yr = self.processor.extract()
        assert len(countries) == 12
        assert len(idb5yr[0]) == 15

    def test_transform(self):
        countries, idb5yr = self.processor.extract()
        idb5yr = idb5yr[0]
        df = self.processor.transform(countries, idb5yr)
        assert len(df) == 13
        assert len(df.columns) == 2
        assert (df.columns == ['yr', 'country_id']).all() == True
        assert df['yr'].dtype == int
        assert df['country_id'].dtype == int


class TestCountryYrIDB5YrETLProcessor:
    processor = generate_country_yr_IDB5Yr_etl_processor()
    def test_extract(self):
        country, country_yr, idb5yr = self.processor.extract()
        assert len(country) == 12
        assert len(idb5yr[0]) == 15
        assert len(country_yr) == 13

    def test_transform(self):
        country, country_yr, idb5yr = self.processor.extract()
        idb5yr = idb5yr[0]
        df = self.processor.transform(country, country_yr, idb5yr)
        assert len(df) == 8
        assert len(df.columns) == 5
        assert (df.columns == ['nim', 'sexratio', 'natincr', 'deaths', 'country_yr_id']).all() == True
        assert df['country_yr_id'].dtype == int
        assert df['nim'].dtype == float
        assert df['deaths'].dtype == float
        assert df['natincr'].dtype == float
        assert df['sexratio'].dtype == float


class TestGDPDataETLProcessor:
    processor = generate_gdp_etl_processor()
    def test_extract(self):
        country, country_yr, gdp = self.processor.extract()
        assert len(country) == 12
        assert len(gdp[0]) == 12
        assert len(country_yr) == 13

    def test_transform(self):
        country, country_yr, gdp = self.processor.extract()
        gdp = gdp[0]
        df = self.processor.transform(country, country_yr, gdp)
        assert len(df) == 2
        assert len(df.columns) == 2
        assert (df.columns == ['country_yr_id', 'gdp']).all() == True
        assert df['country_yr_id'].dtype == int
        assert df['gdp'].dtype == float

class TestAgeDataETLProcessor:
    processor = generate_age_etl_processor()
    def test_extract(self):
        country, country_yr, idb5yr = self.processor.extract()
        assert len(country) == 12
        assert len(idb5yr[0]) == 15
        assert len(country_yr) == 13

    def test_transform(self):
        country, country_yr, idb5yr = self.processor.extract()
        idb5yr = idb5yr[0]
        df = self.processor.transform(country, country_yr, idb5yr)
        assert len(df) == 13
        assert len(df.columns) == 6
        assert (df.columns == ['country_yr_id', 'pop_young', 'pop_middle', 'pop_old', 'births_young', 'births_middle']).all() == True
        assert df['country_yr_id'].dtype == int
        assert df['pop_young'].dtype == float
        assert df['pop_middle'].dtype == float
        assert df['pop_old'].dtype == float
        assert df['births_young'].dtype == float
        assert df['births_middle'].dtype == float