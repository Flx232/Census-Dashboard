import os

from dynaconf import Dynaconf
from etl import CountryETLProcessor, CountryYrETLProcessor, CountryYrIDB5YrETLProcessor, GDPDataETLProcessor, AgeDataETLProcessor, Transformer
from sqlalchemy import create_engine, text

os.chdir(os.path.dirname(__file__))


def run():
    idb5yr_csv = "idb5yr.csv"
    cc_cn_csv = "countries_codes_and_coordinates.csv"
    gdp_csv = "API_NY.GDP.MKTP.CD_DS2_en_csv_v2_329227.csv"

    def build_engine():
        settings = Dynaconf(envvar_prefix="DB", load_dotenv=True)
        return create_engine(settings.ENGINE_URL, echo=False)

    def create_full_path(file_name):
        return ('/').join(["data", file_name])

    engine = build_engine()

    transformer = Transformer()
    print("Starting Data processing...")
    with engine.connect() as conn:
        print("Populating country table...")
        country_processor = CountryETLProcessor(
            conn,
            [create_full_path(cc_cn_csv),
            create_full_path(idb5yr_csv)],
            transformer,
        )
        country_processor.process()

        print("Populating country_yr table...")
        country_yr_processor = CountryYrETLProcessor(
            conn,
            [create_full_path(idb5yr_csv)],
            transformer,
        )
        country_yr_processor.process()

        print("Populating fertility_data table...")
        fert_processor = CountryYrIDB5YrETLProcessor(
            conn,
            [create_full_path(idb5yr_csv)],
            ['TFR', 'IMR', 'E0', 'BIRTHS'],
            transformer,
            'fertility_data'
        )
        fert_processor.process()

        print("Populating general_data table...")
        gen_processor = CountryYrIDB5YrETLProcessor(
            conn,
            [create_full_path(idb5yr_csv)],
            ['NIM', 'SEXRATIO', 'NATINCR', 'DEATHS', 'GR'],
            transformer,
            'general_data'
        )
        gen_processor.process()

        print("Populating pop_data table...")
        pop_processor = CountryYrIDB5YrETLProcessor(
            conn,
            [create_full_path(idb5yr_csv)],
            ['POP', 'POP_DENS'],
            transformer,
            'pop_data'
        )
        pop_processor.process()

        print("Populating gdp_data table...")
        gdp_processor = GDPDataETLProcessor(
            conn,
            [create_full_path(gdp_csv)],
            transformer
        )
        gdp_processor.process()

        print("Populating age_data table...")
        age_processor = AgeDataETLProcessor(
            conn,
            [create_full_path(idb5yr_csv)],
            transformer
        )
        age_processor.process()

        conn.commit()
        print("Finished processing data.")
    engine.dispose()


if __name__ == "__main__":
    run()