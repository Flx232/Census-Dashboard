import os
import pandas as pd
from dynaconf import Dynaconf
from sqlalchemy import create_engine

os.chdir(os.path.dirname(__file__))

def run():

    def build_engine():
        settings = Dynaconf(envvar_prefix="DB", load_dotenv=True)
        return create_engine(settings.ENGINE_URL, echo=False)

    engine = build_engine()

    print("Retrieving Data from database...")
    with engine.connect() as conn:
        sql_query = """
            select alpha2, alpha3, area, 
            country_name, yr, tfr, imr, e0,
            births, nim, sexratio, natincr, deaths,
            gdp, pop, pop_dens, pop_young, pop_middle,
            pop_old, births_young, births_middle
            from country c 
            inner join country_yr cy 
            on c.country_id = cy.country_id 
            left join fertility_data fd
            on cy.country_yr_id = fd.country_yr_id
            left join general_data gd
            on cy.country_yr_id = gd.country_yr_id
            left join gdp_data gdpd
            on cy.country_yr_id = gdpd.country_yr_id
            left join pop_data pd
            on cy.country_yr_id = pd.country_yr_id
            left join age_data ad
            on cy.country_yr_id = ad.country_yr_id;
        """
        general_data = pd.read_sql(sql_query, conn)
        print("Finished retrieval of data.")
    engine.dispose()
    return general_data