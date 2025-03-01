def save_results(
    flagged_gdf, difference_points_gdf, misaligned_segments_path, difference_points_path
):
    """Saves the flagged segments and difference points to shapefiles."""
    try:
        flagged_gdf.to_file(misaligned_segments_path)
        difference_points_gdf.to_file(difference_points_path)
        print(f"✅ Misaligned segments saved to '{misaligned_segments_path}'!")
        print(f"✅ Flagged points saved to {difference_points_path}")
    except Exception as e:
        print(f"Error saving shapefile: {e}")
