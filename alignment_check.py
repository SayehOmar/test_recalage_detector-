import geopandas as gpd
from shapely.geometry import LineString, Point

def check_alignment(segment, cadaster, old_segment, old_cadaster, distance_tolerance):
    """
    Checks if the distance between a segment and cadaster matches the distance
    between an old segment and old cadaster within a tolerance.

    Args:
        segment (shapely.geometry.LineString): The new line segment.
        cadaster (gpd.GeoDataFrame): The new cadaster GeoDataFrame.
        old_segment (shapely.geometry.LineString): The old line segment.
        old_cadaster (gpd.GeoDataFrame): The old cadaster GeoDataFrame.
        distance_tolerance (float): Maximum allowed difference in distances.

    Returns:
        str: "Aligned" or "Misaligned" based on distance comparison.
    """

    # Find the nearest geometry in the cadaster and old_cadaster
    nearest_cadaster_geom = find_nearest_geometry(segment, cadaster)
    nearest_old_cadaster_geom = find_nearest_geometry(old_segment, old_cadaster)

    # Calculate distances
    if nearest_cadaster_geom and nearest_old_cadaster_geom:
        distance_new = segment.distance(nearest_cadaster_geom)
        distance_old = old_segment.distance(nearest_old_cadaster_geom)

        # Compare distances
        if abs(distance_new - distance_old) > distance_tolerance:
            return "Misaligned"
        else:
            return "Aligned"
    else:
        return "Misaligned" # Return misaligned if a nearest geometry is not found

def find_nearest_geometry(segment, cadaster):
    """Finds the nearest geometry in a GeoDataFrame to a given segment."""
    nearest_geom = None
    min_distance = float('inf')

    for geom in cadaster.geometry:
        distance = segment.distance(geom)
        if distance < min_distance:
            min_distance = distance
            nearest_geom = geom

    return nearest_geom



def create_buffered_lines(fibro_line_path, old_fibro_line_path, buffer_distance=1.0, target_crs="EPSG:32632"): #added target_crs
    """Creates buffered GeoDataFrames from fibro line shapefiles."""
    try:
        fibro_line = gpd.read_file(fibro_line_path).to_crs(target_crs) #reprojected
        old_fibro_line = gpd.read_file(old_fibro_line_path).to_crs(target_crs) #reprojected

        buffered_fibro = fibro_line.copy()
        buffered_fibro['geometry'] = buffered_fibro['geometry'].buffer(buffer_distance)

        buffered_old_fibro = old_fibro_line.copy()
        buffered_old_fibro['geometry'] = buffered_old_fibro['geometry'].buffer(buffer_distance)

        return buffered_fibro, buffered_old_fibro

    except Exception as e:
        print(f"Error creating buffered lines: {e}")
        return None, None