import geopandas as gpd
import matplotlib.pyplot as plt

# Includes easy spatial join functions
import CensusReporterMetadata as crm

# Files downloaded from censusreporter.org
FILENAME = "acs2022_5yr_B02001_15000US061130106051_race_davis/acs2022_5yr_B02001_15000US061130106051.shp"
METADATA_PATH = "acs2022_5yr_B02001_15000US061130106051_race_davis/metadata.json"

# Load a data file
gdf = gpd.read_file(FILENAME)

# Extract only the block groups that have centroids within the boundary of the selected place on censusreporter.org
finalDF = crm.easyCentroidJoin(gdf)

# Extract only the summary row provided by censusreporter.org
justDavis = crm.easyBoundary(gdf)

# Replace census code column names with descriptive names provided in the metadata.json file (if desired)
# This can make your code and tables more human-readable, but may make it difficult to manipulate the data if column names are repeated
crm.replaceColumnNames(finalDF, METADATA_PATH)

# Create the plot of the cleaned block group data
finalDF.plot(figsize=(12,8), column="Total:", cmap="OrRd", legend=True)
plt.title("Population of Davis block groups")
plt.savefig("population.png")

# debug: create a plot of the cleaned block group data with the place boundary
# crm.plotBoundaryOnData(justDavis, finalDF, column="Total:", title="Population of Davis block groups")


