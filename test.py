import geopandas as gpd
from shapely.geometry import LineString, Polygon

# Load the fiber and cadastre shapefiles
fiber_gdf = gpd.read_file("shp/fibro_line.shp")
cadastre_gdf = gpd.read_file("shp/new_cadaster.shp")

# Set a buffer distance (meters)
threshold = 0.5  # Adjust as needed

# Buffer the cadastre to create a tolerance zone
buffered_cadastre = cadastre_gdf.copy()
buffered_cadastre["geometry"] = cadastre_gdf.geometry.buffer(threshold)

# Find fiber segments that **do not** intersect the buffer
misaligned_fiber = fiber_gdf[
    ~fiber_gdf.geometry.intersects(buffered_cadastre.unary_union)
]

# Save misaligned fiber segments to a new shapefile
misaligned_fiber.to_file("misaligned_fiber.shp")

print(f"✅ Detected {len(misaligned_fiber)} misaligned fiber segments!")
print("📁 Misaligned fiber saved to 'misaligned_fiber.shp'")
