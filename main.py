from geometry_loading import load_geodata
from processing import process_lines
from saving import save_results
from alignment_check import create_intersection_and_endpoint_points

if __name__ == "__main__":
    fibro_line_path = "shp/fibro_line.shp"
    old_fibro_line_path = "shp/old.shp"
    new_cadaster_path = "shp/new_cadaster.shp"
    misaligned_segments_path = "misaligned_segments/misaligned_segments.shp"
    difference_points_path = "misaligned_segments/difference_points.shp"
    buffered_new_segments_path = "misaligned_segments/new_buffered_segments.shp"
    buffered_old_segments_path = "misaligned_segments/old_buffered_segments.shp"
    old_cadaster_path = "shp/batiment.shp"
    new_vertex_points_path="misaligned_segments/new_vertex_pointss.shp"
    old_vertex_points_path="misaligned_segments/old_vertex_points.shp"
    new_intersection_points_path = "misaligned_segments/new_intersection_points.shp" # New intersection points path
    old_intersection_points_path = "misaligned_segments/old_intersection_points.shp" # Old intersection points path
    




    utm_crs = "EPSG:32632"
    tolerance = 0.5
    min_overlap = 0.5
    modification_tolerance = 1
    distance_tolerance = 0.25
    # Create intersection and endpoint points
    
    fibro_line, old_fibro_line, new_cadaster, old_cadaster = load_geodata(
        fibro_line_path, old_fibro_line_path, new_cadaster_path, utm_crs, old_cadaster_path
    )
    new_intersection_points_gdf = create_intersection_and_endpoint_points(fibro_line, new_cadaster)
    old_intersection_points_gdf = create_intersection_and_endpoint_points(old_fibro_line, old_cadaster)


    result = process_lines(
    fibro_line,
    old_fibro_line,
    new_cadaster,
    old_cadaster,
    tolerance,
    min_overlap,
    modification_tolerance,
    distance_tolerance,
    )

    print("process_lines() returned:", result)  # Debugging output

    if result is None:
         print("Error: process_lines() returned None. Check for issues inside the function.")
    exit()

    # Unpack only if result is not None
    flagged_gdf, difference_points_gdf, buffered_new_segments_gdf, buffered_old_segments_gdf, new_vertex_points_gdf, old_vertex_points_gdf = result




    if fibro_line is not None:
        print("fibro_line loaded:", len(fibro_line), "rows, CRS:", fibro_line.crs)
        print("old_fibro_line loaded:", len(old_fibro_line), "rows, CRS:", old_fibro_line.crs)
        print("new_cadaster loaded:", len(new_cadaster), "rows, CRS:", new_cadaster.crs)
        print("old_cadaster loaded:", len(old_cadaster), "rows, CRS:", old_cadaster.crs)
        flagged_gdf, difference_points_gdf, buffered_new_segments_gdf, buffered_old_segments_gdf,new_vertex_points_gdf, old_vertex_points_gdf = process_lines( # Correct unpacking
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
            new_vertex_points_path,
            old_vertex_points_path,
            new_vertex_points_gdf,
            old_vertex_points_gdf,
            new_intersection_points_path, # Add new intersection points path
            old_intersection_points_path, # Add old intersection points path
            new_intersection_points_gdf, # Add new intersection points GDF
            old_intersection_points_gdf # Add old intersection points GDF
        )