import pandas as pd


class Transformer:
    def remove_column(self, df, key):
        return df.drop(key, axis=1)

    def rename_column(self, df, keys, new_keys):
        if len(keys) != len(new_keys):
            print("Mismatched number of keys.")
            return df
        return df.rename(columns={keys[i]:new_keys[i] for i in range(len(keys))})

    def get_alpha2_from_geo_id(self, df):
        nation_code = df[df['GEO_ID'].str[0:3] == 'W14']
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

    # def extract_year(self, df, key='title', new_column='release_year'):
    #     df[new_column] = df[key].str.extract(r"\((\d{4})\)")
    #     return df

    # def fill_na(self, df, key, fill_value):
    #     df[key] = df[key].fillna(fill_value)
    #     return df

    # def clean_title(self, df, key='title'):
    #     df[key] = df[key].str.replace(r"\s*\((\d{4})\)", '', regex=True)
    #     return df

    # def convert_s_to_date(self, df, key, new_column):
    #     df[new_column] = pd.to_datetime(df[key], unit="s", yearfirst=True)
    #     return df

    # def split_string(self, df, key):
    #     return df[key].str.split('|')

    # def extract_genres(self, series):
    #     return pd.DataFrame({"name":series.explode().unique()})

    # def create_genres_dict(self, genres):
    #     return genres.set_index("name").to_dict()['genre_id']

    # def map_movie_genre(self, movies, genres_dict, series):
    #     movies['genres'] = series
    #     movie_genre = movies[['movie_id', 'genres']].explode(column='genres')
    #     movie_genre['genre_id'] = movie_genre['genres'].map(genres_dict)
    #     return movie_genre

    # def merge_tables(self, table1, table2, how, on):
    #     return table1.merge(table2, how=how, on=on)

class ETLProcessor:
    def __init__(
        self,
        cnx,
        csv_paths,
        transformer: Transformer,
    ):
        self._cnx = cnx
        self._transformer = transformer
        self._csv_paths = csv_paths
    
    def extract_csv(self):
        if len(self._csv_paths) == 1:
            return pd.read_csv(self._csv_paths[0])
        else:
            return (pd.read_csv(csv_path) for csv_path in self._csv_paths)

    def extract(self):
        df = self.extract_csv()[0]
        return df

    def load(self, df, table):
        df.to_sql(
            table, 
            self._cnx, 
            if_exists="append", 
            index=False, 
            schema="movielens"
        )

class CountryETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        super().__init__(cnx, csv_paths, transformer)

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
        super().__init__(cnx, csv_paths, transformer)

    def extract_genre_sql(self):
        sql = """select * from country;"""
        return pd.read_sql(sql, self._cnx)

    def extract(self):
        idb5yr = self.extract_csv()
        countries = self.extract_genre_sql()
        return countries, idb5yr

    def transform(self, countries, idb5yr):
        df = idb5yr[['YR', 'GEO_ID']]
        return self._transformer.clean_title(df)

    def process(self):
        movies, links = self.extract()
        df = self.transform(movies, links)
        self.load(df, 'movie')


class GenreETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        super().__init__(cnx, csv_paths, transformer)

    def extract(self):
        return self.extract_csv()

    def transform(self, df):
        genre_series = self._transformer.split_string(df, 'genres')
        return self._transformer.extract_genres(genre_series)

    def process(self):
        df = self.extract()
        df = self.transform(df)
        self.load(df, 'genre')


class MovieGenreETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        super().__init__(cnx, csv_paths, transformer)

    def extract_genre_sql(self):
        sql = """select * from genre;"""
        return pd.read_sql(sql, self._cnx)

    def extract(self):
        movies = self.extract_csv()
        genres = self.extract_genre_sql()
        return movies, genres

    def transform(self, movies, genres):
        movies = self._transformer.rename_column(movies, ['movieId'], ['movie_id'])
        series = self._transformer.split_string(movies, 'genres')
        genres_dict = self._transformer.create_genres_dict(genres)
        df = self._transformer.map_movie_genre(movies, genres_dict, series)
        return self._transformer.remove_column(df, 'genres')
    
    def process(self):
        movies, genres = self.extract()
        df = self.transform(movies, genres)
        self.load(df, 'movie_genre')


class  RatingETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        super().__init__(cnx, csv_paths, transformer)

    def extract(self):
        return self.extract_csv()

    def transform(self, df):
        df = self._transformer.convert_s_to_date(df, 'timestamp', 'rating_date')
        df = self._transformer.remove_column(df, "timestamp")
        return self._transformer.rename_column(df, ['userId', 'movieId'], ['user_id', 'movie_id'])

    def process(self):
        df = self.extract()
        df = self.transform(df)        
        self.load(df, 'movie_rating')


class  TagETLProcessor(ETLProcessor):
    def __init__(self, cnx, csv_paths, transformer):
        super().__init__(cnx, csv_paths, transformer)

    def extract(self):
        return self.extract_csv()

    def transform(self, df):
        df = self._transformer.convert_s_to_date(df, 'timestamp', 'tag_date')
        df = self._transformer.remove_column(df, "timestamp")
        return self._transformer.rename_column(df, ['userId', 'movieId'], ['user_id', 'movie_id'])

    def process(self):
        df = self.extract()
        df = self.transform(df)
        self.load(df, 'tag')