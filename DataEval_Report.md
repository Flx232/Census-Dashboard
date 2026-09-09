# Data Exploration Report
## IDBsingleyear vs IDB5yr
There is no difference between the two data files. Best to use IDB5yr wide table. It is much easier to convert this table into a schema. Additionally, it has more information than the IDBSingle Year.

## General Report
After much fanagling around with the GDP dataset, ultimately decided not to use it.

Will consider other data to extract from the idb5yr to visualize

Conducted data separation into multiple dataframes
- Have not found any way to meaningfully split the data as they all depend on two unique values (YR, GEO_ID)

Experimented with getting alpha2 code and country name from the geo_id

Found there are region specific for a country and a national geo id for the same country. Decide to only get rows that have the national geo id to simply data extraction

## Conclusion
Ultimately using only idb5yr csv as data
Divided idb5yr data into 5 different dataframes
Conducted minor visualization test. Successful. Have an idea on how to visualize it in plotly
Still unsure how to draw the database schema, have rough idea how the table should look and what datatype is necessary.
Have solid idea what transformations are required for the ETL pipeline.