import geopandas as gpd
from shapely.geometry import LineString, Point
from tqdm import tqdm
import pandas as pd
from alignment_check import check_alignment
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
    segment_buffer_distance=0.5,
):
    """Processes lines, flags misalignments, and creates segment buffers."""
    flagged_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    difference_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    buffered_new_segments_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=fibro_line.crs)
    buffered_old_segments_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=fibro_line.crs)

    for _, row in tqdm(
        fibro_line.iterrows(), total=fibro_line.shape[0], desc="Processing lines"
    ):
        line = row.geometry
        coords = list(line.coords)
        old_line = old_fibro_line.iloc[row.name].geometry
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
                    temp_df = gpd.GeoDataFrame(
                        {"geometry": [segment], "status": [f"{alignment_status}, {modification_status}"],}, crs=fibro_line.crs
                    )
                    flagged_gdf = pd.concat([flagged_gdf, temp_df], ignore_index=True)
                    difference_points_gdf = pd.concat(
                        [difference_points_gdf, gpd.GeoDataFrame({"geometry": [midpoint], "status": [f"{alignment_status}, {modification_status}"],}, crs=fibro_line.crs)],
                        ignore_index=True,
                    )

    return flagged_gdf, difference_points_gdf, buffered_new_segments_gdf, buffered_old_segments_gdf