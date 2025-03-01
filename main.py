from geometry_loading import load_geodata
from processing import process_lines
from saving import save_results

if __name__ == "__main__":
    fibro_line_path = "shp/fibro_line.shp"
    old_fibro_line_path = "shp/old.shp"
    new_cadaster_path = "shp/new_cadaster.shp"
    misaligned_segments_path = "misaligned_segments/misaligned_segments.shp"
    difference_points_path = "misaligned_segments/difference_points.shp"
    utm_crs = "EPSG:32632"
    tolerance = 0.5
    min_overlap = 0.5
    modification_tolerance = 1

    fibro_line, old_fibro_line, new_cadaster = load_geodata(
        fibro_line_path, old_fibro_line_path, new_cadaster_path, utm_crs
    )

    if fibro_line is not None:
        flagged_gdf, difference_points_gdf = process_lines(
            fibro_line,
            old_fibro_line,
            new_cadaster,
            tolerance,
            min_overlap,
            modification_tolerance,
        )
        save_results(
            flagged_gdf,
            difference_points_gdf,
            misaligned_segments_path,
            difference_points_path,
        )
