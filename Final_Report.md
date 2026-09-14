# Final Midterm Report
## Data Source
1.  US Census International Database | U.S. Census Bureau (2025) Population Division https://www.census.gov/programs-surveys/international-programs/about/idb.html
    1.  Date of access: 9/7/2026
2.  World Bank Group GDP dataset | World Bank Group (2026-07-13) World Development Indicators https://data.worldbank.org/indicator/NY.GDP.MKTP.CD
    1.  Date of access: 9/8/2026
3.  Country Codes Alpha2 and Alpha3 | tadast https://gist.github.com/tadast (Dec 12, 202) Countries codes and coordinates [displays name of country, their alpha2 code, alpha3 code, numeric code, longitude and latitude], https://gist.github.com/tadast/8827699
    1.  Date of access: 9/8/2026

## Note
Young Population: 0-29
Middle Population: 30-59
Old Population: 59-100+
Young Births: 15-29
Middle Births: 30-49

## Discovery
1. There is a correlation between GDP and age distribution of population. As GDP increases (country graphs, GDP vs Time), the population distribution skews more towards middle age and older (Population Distribution by age histogram). We can see this trend by comparing historical GDP population numbers to see how these population distributions shift overtime. At year 2024, countries such as the US and China have their young population slowly decrease overtime. We also see a direct negative correlation between increase of gdp and the number of births (Births vs Time). Countries such as the US, Mexico, and China saw their number of births decrease. Cases where this is not necessarily the case are countries that have been sanctioned, Venezuela, Cuba, or have been at war, Ukraine.
2. The decrease of young population can be mitigated through the introduction of immigrants (Population increase vs Time bar chart). If we look at the country France for example, starting 2000, their young population starts declining as the number of births hit its lowest point in 1994 (Births vs Time line chart). However, with the increase of immigrants starting in 1998 (Population Increase vs Time), we can see the distribution of young population to actually increase, possibly due to these migrants having children or having an influx of young migrants (19-29) immigrating into the country. We can see that allowing migrants to immigrate to the country has a positive impact on population distribution (Population age distribution) when we compare the same graphs with Japan. In Japan's case, their young population has been on the decline. 
3. The increase in migration for countries in the EU, such as France, Germany, Sweden and Italy, has shown to have a positive impact on total fertility rates (Population Growth and Fertility rate vs Time) and number of births (Births vs Time). Meanwhile, countries that do not have a positive net immigration rate, such as China, Japan and Indonesia, have been shown to have decreasing total fertility rates. We can even see in the population chart that the influx of migration staved off the population decline for Germany, France and Sweden. If these countries did not have a constant flow of migrants, they would have faced a faster decline in population (Population vs Time). We can see what happens to countries that do not take in migrants, such as Poland. Poland's population trend seems to start to fall at around year 2021, but sharply increased in 2022 due to a large influx of Ukrainians due to the Russian-Ukrainian war. However, outside of that outlier, Poland's net immigrant flow and population growth has been around 0 or negative. We can even see that Poland's total fertility rate has decreased overtime from 2 to 1.3.
4. Finally, there is a positive correlation between lower GDP and countries that heavily skewed young. The year we will be looking at each country will be 2024 for consistency sake. By taking a sample of 10 countries not located in Europe, Australia and North America whose GDP (Map Dashboard) falls below 1.04 T dollars, we can visibly see that these low GDP countries heavily skew young (Population age distribution). If we look at the much richer countries, such as the US, Japan and France, we see that these countries are heavily skewed middle age (Population age distribution). Not only that, the total fertility rate for the poorer countries is significantly higher than wealthier countries. Right now, this is high correlation, not causation. There are many factors as to why poorer countries have a higher fertility rate than richer countries.

## Visualization Explanation
1. Map Dashboard: An interactive map that allows the user to see gdp disparity for every country that has a recorded gdp. Allows the user to see past gdp to see how countries grow or shrink in gdp. Heavily inspired by the world Bank's GDP map. https://data.worldbank.org/indicator/NY.GDP.MKTP.CD
2. GDP vs Time (Year) Country Name: Shows the overall gdp growth over years. The purpose of this graph is to give a visualization to the user of gdp trend, rather than have the user manually imagine the growth of gdp based on color changes on the map
3. Population Distribution by age: Shows the population distribution at the year clicked on by the user. The purpose is to give an idea of what the population makeup is like at that year to give some additional context for the GDP and the direction of the country
4. Births vs Time: Shows the number of births over years for a specific country. Can be used in tandem with the GDP graph to show correlation between GDP and Births, higher GDP often times lead to decreased births and lower fertility.
5. Population vs Time: Shows the number of populations over years for a specific country. Important to visualize impact fertility rate and migration had on population trends to determine whether migration has an impact on population trends.
6. Life Expectancy of Births vs Time: Shows the number of infants over years for a specific country. Used to show how increase in GDP has a positive correlation with life expectancy of infants.
7. Woman's age when giving birth vs time: Shows the general trend of young and middle age new mothers over the years for a specific country. Used to show how changes in when women decide to have their first child change population distributions to skew middle age and older.
8. Population ages vs Time: Shows the general trend of age population distribution over years for a specific country. Used with Woman's Age when giving birth to show how women having later births shifts the age of the general population as a whole to be older.
9. Population Change vs Time: Shows the change in migration and natural population changes in a specific country over time. Used to show migration trends with respect to the natural population trend to show the impact of migration. Used with the population vs time graph and the population growth and fertility rate vs time graph to show whether migration has an impact on fertility rates or population trends.

## Conclusions
From the findings, 3 of my hypothesis has evidence that supports them and 1 of my hypothesis has evidence that runs contrary to it.

First, we must provide a disclaimer. GDP does not provide much meaning by itself. It alone is a flawed measurement that tells nothing about the economic situation of the country, what they produce, or what policy they enacted.

We cannot make any actual decisions based on this finding since there is not enough information to make any conclusive decision. However, with regards to population, there has been multiple evidence in european countries that shows allowing migration helps prevent a situation where the distribution heavily skews the old population while maintaining population replacement levels.

Regarding those, who from these visualizations, gather that we must force women to give birth at ages 15-29, the data itself does not show whether these births were from the same person. We also should not force people to do an action against their will. Those who believe the answer is reducing GDP to increase the number of births, again this thinking is inane and ignores any underlying conditions that may cause people to decide to have less children.

## Feedback
All three people interviewed for feedback stated the rough draft for the plotly website was satisfactory. They all had no complaints.