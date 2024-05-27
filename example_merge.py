# to read and visualize spatial data
import geopandas as gpd

# to create plots
import matplotlib.pyplot as plt

# includes easy spatial join functions
import CensusReporterMetadata as crm

import pandas as pd

# files downloaded from censusreporter.org
FILENAME = "acs2022_5yr_B02001_15000US061130106051_race_davis/acs2022_5yr_B02001_15000US061130106051.shp"
METADATA_PATH = "acs2022_5yr_B02001_15000US061130106051_race_davis/metadata.json"

# load a data file
gdf = gpd.read_file(FILENAME)

# extract only the block groups that have centroids within the boundary of the selected place on censusreporter.org
finalDF = crm.easyCentroidJoin(gdf)

# extract only the summary row provided by censusreporter.org
justDavis = crm.easyBoundary(gdf)

### testing merging on the geoid using preexisting functions
# result: the functions written for block groups also works with census tracts
disabilityGDF = gpd.read_file("acs2022_5yr_B18101_14000US06113010605_disability_tracts/acs2022_5yr_B18101_14000US06113010605.shp")
disabilityGDF = crm.easyCentroidJoin(disabilityGDF)
crm.plotBoundaryOnData(justDavis, disabilityGDF, column="B18101029")

medianAgeGDF = gpd.read_file("acs2022_5yr_B01002_14000US06113010605_age_tracts/acs2022_5yr_B01002_14000US06113010605.shp")
medianAgeGDF = crm.easyCentroidJoin(medianAgeGDF)
 
merged = pd.merge(disabilityGDF, medianAgeGDF, how="left", on=["geoid", "geometry", "name"])
merged.to_csv("goober1.csv", index=False, mode="w")
# https://stackoverflow.com/questions/44327999/how-to-merge-multiple-dataframes