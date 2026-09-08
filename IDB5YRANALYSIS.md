# idb5yr
## Columns
- YR: Year of recording
- GEO_ID: Unique ID of geographic location
- AREA_KM2: Area of geographic location
- ASFR (AGE-RANGE): Age specific fertility rate
- BIRTHS: Total Number of Live Births
  - BIRTHS (AGE-RANGE): Births to females age range
- CBR: Crude birth rate: Live births per 1,000 midyear population
- CDR: Crude death rate: Deaths per 1,000 midyear population
- DEATHS: Deaths, both sexes: Number of deaths during the year
- DEPND: Dependency ratio, Ratio of population age 0-14 and 65+ to population age 15-64, multiplied by 100
  - DEPND0_14: Youth dependency ratio
  - DEPND65_: Old age dependency ratio
- E0: Life expectancy at birth, both sexes: Average number of years newborns would live if the year's age-specific mortality rates remained constant
  - E0_F: Life expectancy at birth, females. Average number of years newborn females would live if the year's age-specific mortality rates remained constant
  - E0_M: Life expectancy at birth, males. Average number of years newborn males would live if the year's age-specific mortality rates remained constant
- MR0: Mortality. Number of deaths per 1k live births
  - FMR0_4: before reaching age 5
  - MMR0_4
  - FMR1_4: between exact ages of 1 to 4
- POP: population at midyear
  - POP (Age Range)
  - FPOP: Female population at midyear
    - FPOP (Age Range): Female population at midyear age range
  - MPOP: Male population at midyear
    - MPOP (Age Range): Male population at midyear age range
- GR: Annual Growth Rate. Change in the population from births, deaths, and net migration, divided by the population at midyear, and multiplied by 100
- GRR: Gross reproduction rate, Average number of daughters females would have by age 49 if the year's age-specific fertility rates and sex-ratio at birth remained constant
- IMR: Infant mortality rate, both sexes. Number of deaths before reaching age 1 per 1,000 live births
  - IMR_F
  - IMR_M
- MEDAGE: Median age, both sexes. The age at which half of the population is older and half is younger
  - MEDAGE_F
  - MEDAGE_M
- NMR: Net migration rate. Difference between the number of immigrants entering and emigrants leaving a country in a year, per 1,000 midyear population
- POP_DENS: Population density, Population per square kilometer
- RNI: Rate of natural increase. Difference between births and deaths, divided by the population at midyear and multiplied by 100
- SRB: Sex ratio at birth. Males per females born among live births
- TFR: Total fertility rate. Average number of children females would have by age 49 if the year's age-specific fertility rates remained constant
- NIM: Net international migrants, both sexes. Difference between the number of immigrants entering and emigrants leaving a country in a year
- NATINCR: Natural Increase. The difference between births and deaths
- SEXRATIO: Sex ratio of the population. Ratio of males to females in the population at midyear
  

Source: https://api.census.gov/data/timeseries/idb/5year/variables.html