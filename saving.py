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

    except Exception as e:
        print(f"Error saving shapefiles: {e}")