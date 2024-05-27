import geopandas as gpd
import CensusReporterMetadata as crm
import matplotlib.pyplot as plt

# Read the shapefile downloaded from BBBike
roadsGDF = gpd.read_file("planet_-121.794_38.519_7403f8a8-shp/shape/roads.shp")

# Extract only cycleways from the data (Does not include amenities)
# https://wiki.openstreetmap.org/wiki/Bicycle#:~:text=OSM%20distinguishes%20between%20cycle%20lanes,grass%20verges%2C%20trees%2C%20etc.
cycleways = roadsGDF[roadsGDF['type'] == 'cycleway']

# Get the place shapefile from censusreporter.org and extract the place boundary
davis = gpd.read_file("acs2022_5yr_B02001_15000US061130106051_race_davis/acs2022_5yr_B02001_15000US061130106051.shp")
justPlace = crm.easyBoundary(davis)
justPlaceSimple = justPlace[["geoid", "geometry"]]

# Spatial join the cycleways linestrings with the place boundary polygon
sjoined = gpd.sjoin(left_df=cycleways, right_df=justPlaceSimple, how="inner", predicate="intersects")

# Get the block group geometries with centroids in the place
davisBlockGroups = crm.easyCentroidJoin(davis) # davis = block group boundaries

# Plot the data
crm.plotBoundaryOnData(justPlaceSimple, sjoined, title="Designated bicycle infrastructure in Davis")
plt.show()

## debug
# cycleways.to_csv("test_cycleways_raw.csv", index=False, mode='w')
# sjoined.to_csv("test_cycleways.csv", index=False, mode='w')