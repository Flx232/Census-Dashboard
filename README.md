# Midterm
## Interest:
- Countries that skew young, middle-age, or older
- Population increase or decrease (country, region)
- Fertility rates (country, region)
- Infant mortality rates (country, region)
- Births (country, region)
- Deaths (country, region)
- Life expectancy at birth (country, region)
- Net international migrants (country, region)
- GDP Per capita (country, region)
## Data Analysis
- Delimiter = '|'
- Header starts with '#'
## Hypotheses
- There is a direct correlation between number of Births, life expectancy at birth and GDP
- Migrants do not increase fertility rates nor improve population trend
- Countries that skew young have lower GDP
- Country skews middle_age and older as age of births increase
## Plan
### Evaluating Data
- First understand the rows in idb5yr file
- Create a simple text file reader that will process the text file and output csv file.
- Find way to Decipher GeoID
  - Seems W140000WO is a fixed prefix with the last two being the Country code
  - Create mapping with all country codes to country names
- Understand the usage of IDB5yr, IDBsingleyear and gdp in an exploratory notebook
- Think of ways how we can reshape the table to only contain useful information
- Plot visualizations that would further help us understand what is needed for visualization
- Estimated Time: 5 Hours
### Creating Schema and Database
- Look at the columns in the datasets we plan to use
- Bunch columns based on similarities
- Create small tables containing these specific columns
- Slowly create relations between these tables
  - Add many to many tables if needed
- Confirm final output with a third party
- Create database in postgres server
- Estimated Time 5 Hours
### ETL Pipeline
- Refer to previous projects for creating ETL pipeline
- Conduct exploratory transformations in the notebook
- Implement these transformations 
- Create pytest for every transformation and the ETL pipeline
- Estimated Time 8 Hours
### SQL Queries extraction
- Do mock sql retrieval queries
- This is to prepare for extracting data for generating visualizations 
- Estimated Time 2-3 Hours
### Generating Visualizations
- Refer to previous projects for creating visualizations
- Refer to previous callback (Hover data, etc for more interesting data visualizations)
- Refer to exploratory notebook
- Utilize tested SQL queries
- Estimated Time 8 Hours
  

Total Hours Required: 28-29 hours at least