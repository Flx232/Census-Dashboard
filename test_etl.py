import pandas as pd
import numpy as np
import pytest
from unittest.mock import MagicMock
from etl import ETLProcessor, CountryETLProcessor
from etl import Transformer
from mock_data_etl import generate_idb5yr, generate_cc_cn

@pytest.fixture
def idb5yr():
    return generate_idb5yr()

@pytest.fixture
def cc_cn():
    return generate_cc_cn()

@pytest.fixture
def transformer():
    return Transformer()

def generate_etl_processor():
    processor = ETLProcessor(
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

# def generate_movie_etl_processor():
#     processor = MovieETLProcessor(
#         None,
#         None,
#         Transformer(),
#     )
#     processor.extract_csv = MagicMock(return_value=[generate_movies_csv(), generate_links_csv()])
#     return processor

# def generate_genre_etl_processor():
#     processor = GenreETLProcessor(
#         None,
#         None,
#         Transformer(),
#     )
#     processor.extract_csv = MagicMock(return_value=[generate_movies_csv()])
#     return processor

# def generate_movie_genre_etl_processor():
#     processor = MovieGenreETLProcessor(
#         None,
#         None,
#         Transformer(),
#     )
#     processor.extract_csv = MagicMock(return_value=[generate_movies_csv()])
#     processor.extract_genre_sql = MagicMock(return_value=generate_genre_sql())
#     return processor

# def generate_rating_etl_processor():
#     processor = RatingETLProcessor(
#         None,
#         "",
#         Transformer(),
#     )
#     processor.extract_csv = MagicMock(return_value=[generate_ratings_csv()])
#     return processor

# def generate_tag_etl_processor():
#     processor = TagETLProcessor(
#         None,
#         "",
#         Transformer(),
#     )
#     processor.extract_csv = MagicMock(return_value=[generate_tags_csv()])
#     return processor

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

    # def test_fill_na(self):
    #     df = self.transformer.merge_tables(self.movies, self.links, "inner", "movieId")
    #     df = self.transformer.remove_column(df, "genres")
    #     df = self.transformer.rename_column(df, ['movieId', 'imdbId', 'tmdbId'], ['movie_id', 'imdb_id', 'tmdb_id'])
    #     df = self.transformer.extract_year(df, 'title', 'release_year')
    #     length = len(df)
    #     num_columns = len(df.columns)
    #     assert df['release_year'].isna().any() == True
    #     df = self.transformer.fill_na(df, 'release_year', '0000')
    #     assert df['release_year'].isna().any() == False
    #     assert len(df) == length
    #     assert len(df.columns) == num_columns

    # def test_convert_type(self):
    #     df = self.transformer.merge_tables(self.movies, self.links, "inner", "movieId")
    #     df = self.transformer.remove_column(df, "genres")
    #     df = self.transformer.rename_column(df, ['movieId', 'imdbId', 'tmdbId'], ['movie_id', 'imdb_id', 'tmdb_id'])
    #     df = self.transformer.extract_year(df, 'title', 'release_year')
    #     df = self.transformer.fill_na(df, 'release_year', '0000')
    #     df = self.transformer.convert_type(df, 'release_year', 'int')
    #     assert df['release_year'].dtype == int

    # def test_clean_title(self):
    #     df = self.transformer.merge_tables(self.movies, self.links, "inner", "movieId")
    #     df = self.transformer.remove_column(df, "genres")
    #     df = self.transformer.rename_column(df, ['movieId', 'imdbId', 'tmdbId'], ['movie_id', 'imdb_id', 'tmdb_id'])
    #     df = self.transformer.extract_year(df, 'title', 'release_year')
    #     df = self.transformer.fill_na(df, 'release_year', '0000')
    #     df = self.transformer.convert_type(df, 'release_year', 'int')
    #     df = self.transformer.clean_title(df)
    #     assert df['title'].head(1).item() == 'Toy Story'

    # def test_split_string(self):
    #     series = self.transformer.split_string(self.movies, 'genres')
    #     assert series.dtype == list

    # def test_extract_genres(self):
    #     series = self.transformer.split_string(self.movies, 'genres')
    #     df = self.transformer.extract_genres(series)
    #     assert len(df) == len(self.genres)
    #     assert len(df['name']) == len(self.genres['name'])

    # def test_get_genre_dict(self):
    #     genres_dict = self.transformer.create_genres_dict(self.genres)
    #     assert type(genres_dict) == dict
    #     assert len(genres_dict) == 10

    # def test_map_movie_genre(self):
    #     movie = self.transformer.rename_column(self.movies, ['movieId'], ['movie_id'])
    #     length = len(self.transformer.split_string(self.movies, 'genres').explode())
    #     series = self.transformer.split_string(movie, 'genres')
    #     genres_dict = self.transformer.create_genres_dict(self.genres)
    #     df = self.transformer.map_movie_genre(movie, genres_dict, series)
    #     df = self.transformer.remove_column(df, 'genres')
    #     assert len(df) == length
    #     assert len(df.columns) == 2
    #     assert (df.columns == ['movie_id', 'genre_id']).all() == True
    #     assert df['genre_id'].dtype == int
    #     assert df['movie_id'].dtype == int

    # def test_convert_s_to_date(self):
    #     num_columns = len(self.ratings.columns)
    #     length = len(self.ratings)
    #     df = self.transformer.convert_s_to_date(self.ratings, 'timestamp', 'rating_date')
    #     assert df['rating_date'].dtype == 'datetime64[s]'
    #     assert len(df.columns) == num_columns+1
    #     assert len(df) == length


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


# class TestMovieETLProcessor:
#     processor = generate_movie_etl_processor()
#     def test_extract(self):
#         movies, links = self.processor.extract()
#         assert len(movies) == 10
#         assert len(links) == 10

#     def test_transform(self):
#         movies, links = self.processor.extract()
#         df = self.processor.transform(movies, links)
#         assert len(df) == 10
#         assert len(df.columns) == 5
#         assert (df.columns == ['movie_id', 'title', 'imdb_id', 'tmdb_id', 'release_year']).all() == True
#         assert df['movie_id'].dtype == int
#         assert df['title'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
#         assert df['release_year'].dtype == int
#         assert df['imdb_id'].dtype == int
#         assert df['tmdb_id'].dtype == float


# class TestGenreETLProcessor:
#     processor = generate_genre_etl_processor()
#     def test_extract(self):
#         df = self.processor.extract()[0]
#         assert len(df) == 10

#     def test_transform(self):
#         df = self.processor.extract()[0]
#         df = self.processor.transform(df)
#         assert len(df) == 10
#         assert len(df.columns) == 1
#         assert (df.columns == ['name']).all() == True
#         assert df['name'].dtype == pd.StringDtype(storage='python', na_value=np.nan)


# class TestMovieGenreETLProcessor:
#     processor = generate_movie_genre_etl_processor()
#     def test_extract(self):
#         movies, genres = self.processor.extract()
#         assert len(movies[0]) == 10
#         assert len(genres) == 10

#     def test_transform(self):
#         movies, genres = self.processor.extract()
#         df = self.processor.transform(movies[0], genres)
#         assert len(df) == 25
#         assert len(df.columns) == 2
#         assert (df.columns == ['movie_id', 'genre_id']).all() == True
#         assert df['movie_id'].dtype == int
#         assert df['genre_id'].dtype == int

# class TestRatingETLProcessor:
#     processor = generate_rating_etl_processor()
#     def test_extract(self):
#         df = self.processor.extract()[0]
#         assert len(df) == 7

#     def test_transform(self):
#         df = self.processor.extract()[0]
#         df = self.processor.transform(df)
#         assert len(df) == 7
#         assert len(df.columns) == 4
#         assert (df.columns == ['user_id', 'movie_id', 'rating', 'rating_date']).all() == True
#         assert df['user_id'].dtype == int
#         assert df['movie_id'].dtype == int
#         assert df['rating'].dtype == float
#         assert df['rating_date'].dtype == 'datetime64[s]'

# class TestTagETLProcessor:
#     processor = generate_tag_etl_processor()
#     def test_extract(self):
#         df = self.processor.extract()[0]
#         assert len(df) == 8

#     def test_transform(self):
#         df = self.processor.extract()[0]
#         df = self.processor.transform(df)
#         assert len(df) == 8
#         assert len(df.columns) == 4
#         assert (df.columns == ['user_id', 'movie_id', 'tag', 'tag_date']).all() == True
#         assert df['user_id'].dtype == int
#         assert df['movie_id'].dtype == int
#         assert df['tag'].dtype == pd.StringDtype(storage='python', na_value=np.nan)
#         assert df['tag_date'].dtype == 'datetime64[s]'