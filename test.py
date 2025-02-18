import geopandas as gpd
from shapely.geometry import LineString, Point
import pandas as pd

# Load shapefiles
fibro_line = gpd.read_file("shp/fibro_line.shp")  # Fiber optic line
new_cadaster = gpd.read_file("shp/new_cadaster.shp")  # Cadastre boundaries

# Prepare an empty GeoDataFrame for misaligned segments
misaligned_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)


# Function to check alignment with a margin of error
def check_alignment(segment, cadaster, tolerance=0.5):
    full_contained = False
    partial_intersect = False

    for poly in cadaster.geometry:
        # Apply buffer to the polygon for the tolerance zone
        buffered_poly = poly.buffer(tolerance)

        # Check if the entire segment is within the buffered polygon
        if buffered_poly.contains(segment):
            full_contained = True

        # Check if the segment intersects the buffered polygon (partial alignment)
        elif buffered_poly.intersects(segment):
            partial_intersect = True

    if full_contained:
        return "Correct"
    elif partial_intersect:
        return "Partial"
    else:
        return "Misaligned"


# Process each line feature
for _, row in fibro_line.iterrows():
    line = row.geometry

    # Convert line to individual segments (vertex to vertex)
    coords = list(line.coords)
    for i in range(len(coords) - 1):
        segment = LineString([Point(coords[i]), Point(coords[i + 1])])
        status = check_alignment(segment, new_cadaster)

        if status == "Misaligned":
            # Create a new DataFrame for the misaligned segment
            temp_df = gpd.GeoDataFrame(
                {"geometry": [segment], "status": [status]}, crs=fibro_line.crs
            )

            # Use pd.concat() to combine the GeoDataFrames
            misaligned_gdf = pd.concat([misaligned_gdf, temp_df], ignore_index=True)

# Save misaligned segments to a new file
misaligned_gdf.to_file("misaligned_segments.shp")

print("✅ Misaligned segments saved to 'misaligned_segments.shp'!")
