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
    segment_buffer_distance=0.25,
    point_distance_tolerance=0.5 
    
):
    print(f"fibro_line length: {len(fibro_line)}")
    print(f"old_fibro_line length: {len(old_fibro_line)}")
    print(f"fibro_line indices: {fibro_line.index.tolist()}")
    print(f"old_fibro_line indices: {old_fibro_line.index.tolist()}")

    
     
    """Processes lines, flags misalignments, and creates segment buffers."""
    
    flagged_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    difference_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    buffered_new_segments_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=fibro_line.crs)
    buffered_old_segments_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=fibro_line.crs)
    new_vertex_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs) # New Vertex Points
    old_vertex_points_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs) # Old Vertex Points
    
    
    print("DEBUG - Before loop start")

    for index, row in tqdm(
        fibro_line.iterrows(), total=fibro_line.shape[0], desc="Processing lines"
    ):
        
        line = row.geometry
        print(f"DEBUG - Processing line {index}")
        coords = list(line.coords)
        old_line = old_fibro_line.iloc[index].geometry
        old_coords = list(old_line.coords)

        if len(coords) - 1 != len(old_coords) - 1:
            continue
        line_flagged = False

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

            # Check distance between corresponding points and add to vertex_points_gdf
            if i < len(coords) - 1:
                new_point1 = Point(coords[i])
                new_point2 = Point(coords[i + 1])
                old_point1 = Point(old_coords[i])
                old_point2 = Point(old_coords[i + 1])

                if new_point1.distance(old_point1) > point_distance_tolerance:
                    new_vertex_points_gdf = pd.concat([new_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [new_point1], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                    old_vertex_points_gdf = pd.concat([old_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [old_point1], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                    line_flagged = True # Flag the whole line
                if new_point2.distance(old_point2) > point_distance_tolerance:
                    new_vertex_points_gdf = pd.concat([new_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [new_point2], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                    old_vertex_points_gdf = pd.concat([old_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [old_point2], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                    line_flagged = True # Flag the whole line

            if line_flagged: # Flag the whole line if any point mismatch
                line_gdf = gpd.GeoDataFrame({"geometry": [line], "status": "Line Point Mismatch"}, crs=fibro_line.crs)
                flagged_gdf = pd.concat([flagged_gdf, line_gdf], ignore_index=True)
                line_midpoint = line.centroid
                difference_points_gdf = pd.concat([difference_points_gdf, gpd.GeoDataFrame({"geometry":[line_midpoint], "status":"Line Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
            else :
                pass


                # Check distance between corresponding points and add to vertex_points_gdf
                
                if i < len(coords) - 1:
                    
                    new_point1 = Point(coords[i])
                    new_point2 = Point(coords[i + 1])
                    old_point1 = Point(old_coords[i])
                    old_point2 = Point(old_coords[i + 1])
                    

                    if new_point1.distance(old_point1) > point_distance_tolerance:
                        new_vertex_points_gdf = pd.concat([new_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [new_point1], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                        old_vertex_points_gdf = pd.concat([old_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [old_point1], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                    if new_point2.distance(old_point2) > point_distance_tolerance:
                        new_vertex_points_gdf = pd.concat([new_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [new_point2], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                        old_vertex_points_gdf = pd.concat([old_vertex_points_gdf, gpd.GeoDataFrame({"geometry": [old_point2], "status": "Point Mismatch"}, crs=fibro_line.crs)], ignore_index=True)
                
        print("Returning results from process_lines.")
        
        print(flagged_gdf.empty, difference_points_gdf.empty, buffered_new_segments_gdf.empty, buffered_old_segments_gdf.empty, new_vertex_points_gdf.empty, old_vertex_points_gdf.empty)
        '''
        print("DEBUG - About to return from process_lines()")
        print("DEBUG - flagged_gdf:", flagged_gdf)
        print("DEBUG - difference_points_gdf:", difference_points_gdf)
        print("DEBUG - buffered_new_segments_gdf:", buffered_new_segments_gdf)
        print("DEBUG - buffered_old_segments_gdf:", buffered_old_segments_gdf)
        print("DEBUG - new_vertex_points_gdf:", new_vertex_points_gdf)
        print("DEBUG - old_vertex_points_gdf:", old_vertex_points_gdf)
        '''    
        return flagged_gdf, difference_points_gdf, buffered_new_segments_gdf, buffered_old_segments_gdf,new_vertex_points_gdf,old_vertex_points_gdf # Return both vertex GDFs

    