from geometry_loading import load_geodata
from processing import process_lines
from saving import save_results

if __name__ == "__main__":
    fibro_line_path = "shp/fibro_line.shp"
    old_fibro_line_path = "shp/old.shp"
    new_cadaster_path = "shp/new_cadaster.shp"
    misaligned_segments_path = "misaligned_segments/misaligned_segments.shp"
    difference_points_path = "misaligned_segments/difference_points.shp"
    buffered_new_segments_path = "misaligned_segments/new_buffered_segments.shp"
    buffered_old_segments_path = "misaligned_segments/old_buffered_segments.shp"
    old_cadaster_path = "shp/batiment.shp"

    utm_crs = "EPSG:32632"
    tolerance = 0.5
    min_overlap = 0.5
    modification_tolerance = 1
    distance_tolerance = 0.25

    fibro_line, old_fibro_line, new_cadaster, old_cadaster = load_geodata(
        fibro_line_path, old_fibro_line_path, new_cadaster_path, utm_crs, old_cadaster_path
    )

    if fibro_line is not None:
        flagged_gdf, difference_points_gdf, buffered_new_segments_gdf, buffered_old_segments_gdf = process_lines( # Correct unpacking
            fibro_line,
            old_fibro_line,
            new_cadaster,
            old_cadaster,
            tolerance,
            min_overlap,
            modification_tolerance,
            distance_tolerance,
        )

        save_results( # Correct save_results call
            flagged_gdf,
            difference_points_gdf,
            misaligned_segments_path,
            difference_points_path,
            buffered_new_segments_path,
            buffered_old_segments_path,
            buffered_new_segments_gdf,
            buffered_old_segments_gdf,
        )