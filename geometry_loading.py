import geopandas as gpd


def load_geodata(fibro_line_path, old_fibro_line_path, new_cadaster_path, utm_crs,old_cadaster_path ):
    """Loads geodata from shapefiles and reprojects to the specified CRS."""
    try:
        old_cadaster=gpd.read_file(old_cadaster_path).to_crs(utm_crs) 
        fibro_line = gpd.read_file(fibro_line_path).to_crs(utm_crs)
        old_fibro_line = gpd.read_file(old_fibro_line_path).to_crs(utm_crs)
        new_cadaster = gpd.read_file(new_cadaster_path).to_crs(utm_crs)
        return fibro_line, old_fibro_line, new_cadaster,old_cadaster
    except FileNotFoundError as e:
        print(f"Error: Shapefile not found: {e}")
        return None, None, None
