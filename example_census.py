import geopandas as gpd
from mySecrets import USCensusAPI # This refers to a personal file "mySecrets.py" which contains a class USCensusAPI with an attribute "key" with my API key (Get a key: https://api.census.gov/data/key_signup.html)
from census import Census
from us import states
import pandas as pd
import CensusReporterMetadata as crm
# from pygris import block_groups
# from pygris import places

## Because censusreporter.org only has data from the most recent ACS5, other methods must be used to get data from previous years.

# https://pygis.io/docs/d_access_census.html
c = Census(USCensusAPI.key)

# Use censusreporter.org to download the easily parseable place data
gdf = gpd.read_file("acs2022_5yr_B02001_15000US061130106051_race_davis/acs2022_5yr_B02001_15000US061130106051.shp")

# The data from censusreporter.org includes all intersecting block groups/census tracts
# This is not necessarily representative of the place, so we will use a centroid join to clean the data
gdf_cleaned = crm.easyCentroidJoin(gdf)

# censusreporter.org and census api have two different geoid formats
gdf_cleaned['geoid'] = gdf_cleaned["geoid"].apply(crm.geo2fips_block) 

# I asked my mentor for the table codes and searched them on the variables list:
# https://api.census.gov/data/2020/acs/acs5/variables.hjn,m
# The dictionary format makes it extraordinarily easy to retrieve the variable names
variables = {"GEO_ID": "geoid",
             "B25045_003E": "Estimate!!Total:!!Owner occupied:!!No vehicle available",
             "B25045_007E":"Estimate!!Total:!!Owner occupied:!!1 or more vehicles available",
             "B25045_012E":"Estimate!!Total:!!Renter occupied:!!No available",
             "B25045_016E":"Estimate!!Total:!!Renter occupied:!!1 or more vehicles available",
             "B25001_001E": "Total Housing Units"
             }

# Reference: https://pypi.org/project/census/
# Fetch the desired data from the Census
yolo_census = c.acs5.state_county_blockgroup(fields = list(variables.keys()),
                                      state_fips = states.CA.fips,
                                      county_fips = "113",
                                      blockgroup = "*",
                                      year = 2020)

# Create a pandas DataFrame using the retrieved data
data_df = pd.DataFrame(yolo_census)

# Rename the GEO_ID column to geoid to match the data from censusreporter.org for easier merging
data_df.rename(columns={"GEO_ID": "geoid"}, inplace=True)

# The geoid's are not always in the same format, so this converts the geoid to just the FIPS code
data_df['geoid'] = data_df["geoid"].apply(crm.geo2fips_block)

# Merge the dataframes to get only data from the block groups in the desired place
davis_df = pd.merge(gdf_cleaned, data_df, how="left", on="geoid")

# Rename the column names with descriptive names for easier reading
# This function returns a list of the unused columns
# Drop the columns that are from the arbitrarily-chosen table on censusreporter.org and not on the variables list
unusedColumns = crm.replaceColumnNamesWithDict(davis_df, variables)
davis_df.drop(columns = unusedColumns, inplace=True)

# The cleaned data now only has the essential columns (geoid, name, geometry) and requested columns
# as well as only containing block groups/census tracts with centroids within the place boundary

# I want to do some math to get the data for my uses
davis_df["No vehicle available:"] = davis_df["Estimate!!Total:!!Owner occupied:!!No vehicle available"].add(
    davis_df["Estimate!!Total:!!Renter occupied:!!No available"])
davis_df["Total"] = davis_df["Estimate!!Total:!!Owner occupied:!!No vehicle available"].add(
    davis_df["Estimate!!Total:!!Renter occupied:!!No available"]
    ).add(
        davis_df["Estimate!!Total:!!Owner occupied:!!1 or more vehicles available"]
    ).add(
        davis_df["Estimate!!Total:!!Renter occupied:!!1 or more vehicles available"]
    )
davis_df["No vehicle %:"] = davis_df["No vehicle available:"] / davis_df["Total"] * 100

# Cross-referencing the number of housing units with a different table to affirm quality of data.
davis_df["Percentage households represented"] = davis_df["Total"] / davis_df["Total Housing Units"] * 100
all_represented_households = davis_df["Total"].sum() / davis_df["Total Housing Units"].sum() * 100
print(f"Percentage of represented households--Total: {all_represented_households}")

# Save the data in a CSV
davis_df.to_csv("census_get.csv", index=False, mode="w")

# Plot the desired column on a map
crm.plotBoundaryOnData(crm.easyBoundary(gdf), davis_df, column="No vehicle %:", title="Percentage of households without a vehicle")

## DEBUG
# data_df.to_csv("census_raw.csv", index=False,mode="w")
