from mySecrets import USCensusAPI # This refers to a personal file "mySecrets.py" which contains a class USCensusAPI with an attribute "key" with my API key (Get a key: https://api.census.gov/data/key_signup.html)
from census import Census
import pandas as pd

## Because censusreporter.org only has data from the most recent ACS5, other methods must be used to get data from previous years.

# https://pygis.io/docs/d_access_census.html
c = Census(USCensusAPI.key)

# https://nicolepaul.io/post/python-census/
dataset = c.acs5
tables = pd.DataFrame(dataset.tables(2020))
keyword = "housing units"
criteria = tables.description.str.contains(keyword.upper())
tables[criteria].to_csv("tables.csv", index=False, mode="w")