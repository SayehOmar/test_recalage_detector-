import geopandas as gpd
from shapely.geometry import LineString, Point
from tqdm import tqdm
import pandas as pd
from alignment_check import check_alignment , find_nearest_geometry
from modification_check import check_modifications

def process_lines(
    fibro_line,
    old_fibro_line,
    new_cadaster,
    old_cadaster,
    tolerance,
    min_overlap,
    modification_tolerance,
    distance_tolerance,
    segment_buffer_distance=0.25,
    point_distance_tolerance=0.5
):
    """Processes lines, flags misalignments, and creates segment buffers."""

    flagged_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    difference_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    buffered_new_segments_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=fibro_line.crs)
    buffered_old_segments_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=fibro_line.crs)
    new_vertex_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    old_vertex_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)

    print("DEBUG - Before loop start")

    for index, row in tqdm(
        fibro_line.iterrows(), total=fibro_line.shape[0], desc="Processing lines"
    ):
        line = row.geometry
        coords = list(line.coords)
        old_line = old_fibro_line.iloc[index].geometry
        old_coords = list(old_line.coords)

        if len(coords) - 1 != len(old_coords) - 1:
            continue

        for i in range(len(coords) - 1):
            segment = LineString([Point(coords[i]), Point(coords[i + 1])])
            old_segment = LineString([Point(old_coords[i]), Point(old_coords[i + 1])])

            alignment_status = check_alignment(
                segment, new_cadaster, old_segment, old_cadaster, distance_tolerance
            )
            modification_status = check_modifications(
                segment, old_fibro_line, modification_tolerance, distance_tolerance
            )

            midpoint = segment.centroid
            within_cadaster_buffer = False
            for poly in new_cadaster.geometry:
                if poly.buffer(0.5).contains(midpoint):
                    within_cadaster_buffer = True
                    break

            # Create buffers for segments
            buffered_new_segment = segment.buffer(segment_buffer_distance)
            buffered_old_segment = old_segment.buffer(segment_buffer_distance)
            buffered_new_segments_gdf = pd.concat([buffered_new_segments_gdf, gpd.GeoDataFrame({"geometry": [buffered_new_segment]}, crs=fibro_line.crs)], ignore_index=True)
            buffered_old_segments_gdf = pd.concat([buffered_old_segments_gdf, gpd.GeoDataFrame({"geometry": [buffered_old_segment]}, crs=fibro_line.crs)], ignore_index=True)

            '''
            # Check for buffer overlap
            if not buffered_new_segment.intersects(buffered_old_segment):
                buffer_mismatch_status = "Buffer Mismatch"
                temp_df = gpd.GeoDataFrame(
                    {"geometry": [segment], "status": [buffer_mismatch_status]}, crs=fibro_line.crs
                )
                flagged_gdf = pd.concat([flagged_gdf, temp_df], ignore_index=True)
                difference_points_gdf = pd.concat(
                    [difference_points_gdf, gpd.GeoDataFrame({"geometry": [midpoint], "status": [buffer_mismatch_status]}, crs=fibro_line.crs)],
                    ignore_index=True,
                )

            elif not within_cadaster_buffer:
                if alignment_status == "Misaligned" or modification_status in ["Modified", "New Segment"]:
                    status = f"{alignment_status}, {modification_status}"
                    flagged_by = "Alignment/Modification Check"
                    temp_df = gpd.GeoDataFrame(
                        {"geometry": [segment], "status": [status], "flagged_by": [flagged_by]}, crs=fibro_line.crs
                    )
                    flagged_gdf = pd.concat([flagged_gdf, temp_df], ignore_index=True)
                    difference_points_gdf = pd.concat(
                        [difference_points_gdf, gpd.GeoDataFrame({"geometry": [midpoint], "status": [f"{alignment_status}, {modification_status}"],}, crs=fibro_line.crs)],
                        ignore_index=True,
                    )
                '''

           # Create vertex points with attributes
        for i in range(len(coords)):
            new_point = Point(coords[i])
            old_point = Point(old_coords[i])

            vertex_type = "middle"
            if i == 0:
                vertex_type = "start"
            elif i == len(coords) - 1:
                vertex_type = "end"

            new_vertex_points_gdf = pd.concat([new_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [new_point], "line_index": [index], "vertex_type": [vertex_type]}, crs=fibro_line.crs)], ignore_index=True)
            old_vertex_points_gdf = pd.concat([old_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [old_point], "line_index": [index], "vertex_type": [vertex_type]}, crs=fibro_line.crs)], ignore_index=True)

        # Calculate distances and flag segments
        for i in range(len(coords) - 1):
            segment = LineString([Point(coords[i]), Point(coords[i + 1])])
            old_segment = LineString([Point(old_coords[i]), Point(old_coords[i + 1])])

            new_point1 = Point(coords[i])
            new_point2 = Point(coords[i + 1])
            old_point1 = Point(old_coords[i])
            old_point2 = Point(old_coords[i + 1])

            nearest_cadaster_line_new_1 = find_nearest_geometry(new_point1, new_cadaster.boundary)
            nearest_cadaster_line_new_2 = find_nearest_geometry(new_point2, new_cadaster.boundary)
            nearest_cadaster_line_old_1 = find_nearest_geometry(old_point1, new_cadaster.boundary)
            nearest_cadaster_line_old_2 = find_nearest_geometry(old_point2, new_cadaster.boundary)

            if nearest_cadaster_line_new_1 and nearest_cadaster_line_new_2 and nearest_cadaster_line_old_1 and nearest_cadaster_line_old_2:
                dist_new_1 = new_point1.distance(nearest_cadaster_line_new_1)
                dist_new_2 = new_point2.distance(nearest_cadaster_line_new_2)
                dist_old_1 = old_point1.distance(nearest_cadaster_line_old_1)
                dist_old_2 = old_point2.distance(nearest_cadaster_line_old_2)

                distance_diff_1 = abs(dist_new_1 - dist_old_1)
                distance_diff_2 = abs(dist_new_2 - dist_old_2)

                if distance_diff_1 > point_distance_tolerance or distance_diff_2 > point_distance_tolerance:
                    temp_df = gpd.GeoDataFrame({
                        "geometry": [segment],
                        "status": "Point Mismatch",
                        "dist_diff_1": distance_diff_1,
                        "dist_diff_2": distance_diff_2,
                        "dist_new_1": dist_new_1,
                        "dist_old_1": dist_old_1,
                        "dist_new_2": dist_new_2,
                        "dist_old_2": dist_old_2
                    }, crs=fibro_line.crs)
                    flagged_gdf = pd.concat([flagged_gdf, temp_df], ignore_index=True)
                    difference_points_gdf = pd.concat([difference_points_gdf, gpd.GeoDataFrame({"geometry": [segment.centroid], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)

    print("Returning results from process_lines.")
    print(flagged_gdf.empty, difference_points_gdf.empty, buffered_new_segments_gdf.empty, buffered_old_segments_gdf.empty, new_vertex_points_gdf.empty, old_vertex_points_gdf.empty)

    return flagged_gdf, difference_points_gdf, buffered_new_segments_gdf, buffered_old_segments_gdf, new_vertex_points_gdf, old_vertex_points_gdf