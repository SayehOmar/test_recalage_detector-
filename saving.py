import geopandas as gpd
import os

def save_results(
    flagged_gdf,
    difference_points_gdf,
    misaligned_segments_path,
    difference_points_path,
    buffered_new_segments_path, # New segments buffer path
    buffered_old_segments_path, # Old segments buffer path
    buffered_new_segments_gdf, # New segments buffer gdf
    buffered_old_segments_gdf, # old segments buffer gdf
    new_vertex_points_path, # New vertex path
    old_vertex_points_path, # Old vertex path
    new_vertex_points_gdf, # New Vertex GDF
    old_vertex_points_gdf # Old Vertex GDF
):
    """Saves flagged segments, difference points, and segment buffers."""
    try:
        # Save flagged segments
        flagged_gdf.to_file(misaligned_segments_path)
        print(f"✅ Misaligned segments saved to '{misaligned_segments_path}'!")

        # Save difference points
        difference_points_gdf.to_file(difference_points_path)
        print(f"✅ Flagged points saved to {difference_points_path}")

        # Save buffered new segments
        if buffered_new_segments_gdf is not None and not buffered_new_segments_gdf.empty:
            buffered_new_segments_gdf.to_file(buffered_new_segments_path)
            print(f"✅ Buffered new segments saved to '{buffered_new_segments_path}'!")

        # Save buffered old segments
        if buffered_old_segments_gdf is not None and not buffered_old_segments_gdf.empty:
            buffered_old_segments_gdf.to_file(buffered_old_segments_path)
            print(f"✅ Buffered old segments saved to '{buffered_old_segments_path}'!")
            
            # Save new vertex points
        if new_vertex_points_gdf is not None and not new_vertex_points_gdf.empty:
            new_vertex_points_gdf.to_file(new_vertex_points_path)
            print(f"✅ New vertex points saved to '{new_vertex_points_path}'!")

        # Save old vertex points
        if old_vertex_points_gdf is not None and not old_vertex_points_gdf.empty:
            old_vertex_points_gdf.to_file(old_vertex_points_path)
            print(f"✅ Old vertex points saved to '{old_vertex_points_path}'!")

    except Exception as e:
        print(f"Error saving shapefiles: {e}")