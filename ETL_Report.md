# ETL Midterm Report
## Data Source
1.  US Census International Database | U.S. Census Bureau (2025) Population Division https://www.census.gov/data-tools/demo/data/idb/dataset/idbzip.zip
    1.  Date of access: 9/7/2026
2.  World Bank Group GDP dataset | World Bank Group (2026-07-13) World Development Indicators https://data.worldbank.org/indicator/NY.GDP.MKTP.CD
    1.  Date of access: 9/8/2026
3.  Country Codes Alpha2 and Alpha3 | tadast https://gist.github.com/tadast (Dec 12, 202) Countries codes and coordinates [displays name of country, their alpha2 code, alpha3 code, numeric code, longitude and latitude], https://gist.github.com/tadast/8827699
    1.  Date of access: 9/8/2026

## Extraction
1. Data for US Census International Database was sourced from the dev10-midterm section. The data was downloaded through a provided zip file link. The format of the data itself was in txt file, which was translated into a csv file using a personally developed process_file python file.
   1. Read each line of the text file
   2. Strip line of white space
   3. Separate header from rest of data
   4. Split line by delimiter '|'
   5. Store as a list of dictionaries to allow for easy writing using csv DictWriter
2. World Bank Group GDP dataset was sourced from the World Bank Group. The data was downloaded using the provided csv link in the website. The format of the data itself was a csv file.
   1. Create an empty excel worksheet
   2. Open the csv file in power queries
   3. Remove the informational lines
   4. Set the row containing headers as the header of the dataset
   5. Save and load onto the worksheet
   6. Save the worksheet as a csv file
3. Country Codes and Coordinates was sourced from an open source gist discussion post. The format of the data is csv. The file was downloaded using th download button in the gist discussion post. No further processing of data was required

### Transformation IDB5yr US Census
1. GEO_ID in idb5yr contains both national geo_id and region specific geo_id. Must exclude region specific geo_id to focus on only national geo_id
2. GEO_ID in idb5yr contains alpha2 code at the last two characters. Must extract this alpha2 code
3. For specific databases, such as age aggregation database, collection of columns need to be aggregated to form 1 column.
4. No columns were removed as the plan was to create new columns from the existing columns, and then select specific columns as a new dataframe to pass into the database
5. Changed the name of AREA_KM to area and lower cased every non changed column in accordance to the database schema

## Transformation GDP World Bank Group (WBG)
1. The data consists of the country name, alpha3 code, the indicator, the indicator code and the years.
   1. The years itself contain the gdp of the country at that year.
2. Melt the data so that the format of the data matches with the IDB5yr by creating a yr column and a gdp column.
3. The only columns that are of interest is the country code, yr and gdp.

## Transformation Country codes and Coordinates
1. The data is used as is. The only purpose is to be used to map alpha2 codes in IDB5yr to the alpha3 codes in WBG GDP data.

## ETL Lifecycle (load)
Source|Columns|Schema
1. idb5yr, Country codes and coordinates|alpha2, alpha3, area, country name|country table
2. idb5yr, country table|yr|country_yr table
3. idb5yr, country table, country_yr table|tfr, imr, e0, births|fertility_data table
3. idb5yr, country table, country_yr table|nim, sexratio, natincr, deaths|general_data table
3. gdp csv, country table, country_yr table|gdp|gdp_data table
3. idb5yr, country table, country_yr table|pop, pop_dens|pop_data table
3. idb5yr, country table, country_yr table|pop_young, pop_middle, pop_old, births_young, births_middle|age_data table

pop_young: age 0-29
pop_middle: age 30-59
pop_old: age 60-100+

births_young: age 15-29
births_middle: age 30-49

Steps:
1 -> 2 -> 3 (interchangeable)