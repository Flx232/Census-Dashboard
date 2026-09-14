# Visualization Midterm Report
## Data Source
1.  US Census International Database | U.S. Census Bureau (2025) Population Division https://www.census.gov/programs-surveys/international-programs/about/idb.html
    1.  Date of access: 9/7/2026
2.  World Bank Group GDP dataset | World Bank Group (2026-07-13) World Development Indicators https://data.worldbank.org/indicator/NY.GDP.MKTP.CD
    1.  Date of access: 9/8/2026
3.  Country Codes Alpha2 and Alpha3 | tadast https://gist.github.com/tadast (Dec 12, 202) Countries codes and coordinates [displays name of country, their alpha2 code, alpha3 code, numeric code, longitude and latitude], https://gist.github.com/tadast/8827699
    1.  Date of access: 9/8/2026

## Visualizations
1. US Census International Database Visualization: 
   1. A scatter plot with a drop down and a year slider that allows the user to choose the year and a  quantitative data to display a scatter plot with the size based on the quantitative data. This also satisfies the filter and sort requirements as I am filtering the data and sorting the data simultaneously through this scatter plot
2. World Bank Group GDP dataset:
   1. A histogram that aims to show share of each country in cumulative gdp per year.
3. Country Codes Alpha2 and Alpha3:
   1. This dataset does not have any clear quantitative values, with the only numerical values being latitude average and longitude average for each country. Therefore, I can only use this data in tandem with other datasets. Therefore, I bin the latitudes around 30 degrees north and label countries that fall in that category as north and the rest as south. My original goal is to only select countries in the economic global north, but I was not sure how I can adequately apply that without manually checking every latitude. Therefore I just set a harsh customized limit not based on the equator due to the heavy land imbalance between the northern and southern hemisphere. I created a histogram that aims to show sum of all gdp in each sphere, north and south, across a range of years that the user can select. This helps show the change of wealth distribution between north and south.