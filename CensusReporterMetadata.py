import json
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

## Replace column codes with descriptive names in place
    # gdf: GeoDataFrame built using either a shapefile or geojson from censusreporter.org
    # filepath: relative path to the required metadata.json file from censusreporter.org
def replaceColumnNamesWithMetadata(gdf, filepath):
    f = open(filepath, "r")
    metadata = json.load(f)
    for i in range(len(gdf.columns) - 1):
        col = gdf.columns[i]
        table = col[0:6]
        try:
            if (col[-1] == 'e'):
                    colCode = col[0:len(col) - 1]
                    colName = metadata["tables"][table]["columns"][colCode]["name"]
                    gdf.rename(columns={col:f"{colName} Error"}, inplace=True)
            else:
                colName = metadata["tables"][table]["columns"][col]["name"]
                gdf.rename(columns={col:colName}, inplace=True)
        except:
            continue

## Replace column codes with descriptive names in place
    # gdf: GeoDataFrame
    # dict: a Python Dictionary with keys as the census variable codes and values as descriptive names        
def replaceColumnNamesWithDict(gdf, dict):
    unusedColumns = []
    for i in range(len(gdf.columns)):
        col = gdf.columns[i]
        try:
            colName = dict[col]
            gdf.rename(columns={col:colName}, inplace=True)
        except:
            if col != "geoid" and col != "geometry" and col != "name":
                unusedColumns.append(col)
            continue
    return unusedColumns

## Creates a new GeoDataFrame with the centroids of the original geometries
    # This function has been mostly taken from: https://gis.stackexchange.com/questions/216788/convert-polygon-feature-centroid-to-points-using-python
    # gdf: GeoDataFrame. If using a file from censusreporter.org, do not include the summary row (last row)
    # returns: a new GeoDataFrame with columns "geoid" and "geometry"
def makeCentroidGDF(gdf):
    
    # copy poly to new GeoDataFrame
    points = gdf.copy()
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html#geopandas.GeoDataFrame.to_crs
    points = points.to_crs(4326)
    # change the geometry
    points.geometry = points['geometry'].centroid
    # same crs
    ## points.to_file(f'{newFileName}.shp')
    myCols = points[["geoid", "geometry"]]
    return myCols

## Plot the boundary of the place on top of the block group or census tract map.
    # Saves figures to the same folder as the python program file
def plotBoundaryOnData(boundarygdf, datagdf, column=None, cmap=None, title=None):
    fig, ax = plt.subplots()
    cmap = "OrRd" if cmap == None else cmap
    if (column):
         datagdf.plot(column=column, cmap=cmap, legend=True, ax=ax)
    else: # If no specified data column, just plot the geometries
         datagdf.plot(color="tomato", ax=ax)
    boundarygdf.boundary.plot(ax=ax, color="black")

    # formatting
    ax.axis('off')
    plt.title(label=title, fontsize=20, pad=70, wrap=True)
    fig.set_figwidth(12)
    fig.set_figheight(8)

    # show and save figure
    plt.show()
    fig.savefig(f"{title}.png" if title else "figure.png")

## Get the summary row from a GeoDataFrame made from a file downloaded from censusreporter.org
    # returns: GeoDataFrame with a single row. The geometry column will contain the boundary of the place, if used with a file from censusreporter.org
def easyBoundary(gdf):
    indices = []
    for i in range(len(gdf.index) - 1):
        indices.append(i)
    justPlace = gdf.copy()
    justPlace.drop(index=indices, inplace=True)
    
    return justPlace

def easyCentroidJoin(gdf):
    gdfWithoutSummaryRow = gdf.drop(len(gdf.index) - 1)

    centroids = makeCentroidGDF(gdfWithoutSummaryRow) # get df of centroids that does not include the summary row
    justPlace = easyBoundary(gdf)
    justPlaceSimple = justPlace[["geoid", "geometry"]]
    # Spatial join the geometry of the place with the centroids of the block groups
    sjoined = gpd.sjoin(left_df=justPlaceSimple, right_df=centroids, how="left", predicate="intersects")

    # Extract the geoid's of the desired block groups
    correctBlockGroups = sjoined['geoid_right']
    correctBlockGroups.rename("geoid", inplace=True)

    # Merge data to extract only the data for the desired block groups
    finalDF = pd.merge(correctBlockGroups, gdf, how='left', on="geoid")
    finalDF = gpd.GeoDataFrame( # https://geopandas.org/en/stable/gallery/create_geopandas_from_pandas.html
        finalDF, geometry=finalDF.geometry, crs="4326"
    )

    # Save the data
    finalDF.to_csv("centroid_join.csv", index=False, mode='w')

    return finalDF

def geo2fips_block(x):
    return x[len(x) - 12:]

def geo2fips_tract(x):
    return x[len(x) - 11:]