import geopandas as gpd
from shapely.geometry import LineString, Point
import pandas as pd
from shapely.ops import transform
from tqdm import tqdm

# Load shapefiles
try:
    fibro_line = gpd.read_file("shp/fibro_line.shp")
    old_fibro_line = gpd.read_file("shp/old.shp")
    new_cadaster = gpd.read_file("shp/new_cadaster.shp")
except FileNotFoundError:
    print("Error: One or more shapefiles not found.")
    exit()

# Ensure all files have the same CRS


utm_crs = "EPSG:32632"  # Replace with YOUR UTM zone's EPSG code!

new_cadaster = new_cadaster.to_crs(utm_crs)
fibro_line = fibro_line.to_crs(utm_crs)
old_fibro_line = old_fibro_line.to_crs(utm_crs)

# Prepare an empty GeoDataFrame for flagged segments
flagged_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
# Create a GeoDataFrame to store the difference points
difference_points_gdf = gpd.GeoDataFrame(
    columns=["geometry", "status"], crs=fibro_line.crs
)  # Same CRS as fibro_line


def check_alignment(segment, cadaster, tolerance=0.5, min_overlap=0.5):
    buffered_cadaster = cadaster.geometry.buffer(tolerance)
    intersected = segment.intersects(buffered_cadaster)
    contained = segment.within(buffered_cadaster)

    if contained.any():  # Correctly use .any()
        return "Correct"
    elif intersected.any():  # Correctly use .any()
        intersection = segment.intersection(buffered_cadaster[intersected])

        # Handle the case where intersection is a GeoSeries
        if isinstance(intersection, gpd.GeoSeries):
            if (
                not intersection.is_empty.any()
            ):  # Check if there's any intersection at all
                return "Misaligned"  # No intersection
            intersection_length = (
                intersection.length.sum()
            )  # Sum of lengths if multiple intersections
        elif not intersection.is_empty:  # Check if there's any intersection at all
            if (
                intersection.geom_type == "MultiLineString"
            ):  # Correctly check geom_type of a single geometry
                intersection_length = sum(line.length for line in intersection.geoms)
            elif intersection.geom_type == "LineString":
                intersection_length = intersection.length
            else:
                intersection_length = 0
        else:
            return "Misaligned"

        if segment.length > 0:
            overlap_ratio = intersection_length / segment.length
        else:
            overlap_ratio = 0

        if overlap_ratio >= min_overlap:
            return "Partial"
        else:
            return "Misaligned"
    else:
        return "Misaligned"


def check_modifications(segment, old_fibro, tolerance=0.5):
    """Checks if a segment has been modified compared to old_fibro lines."""

    for _, old_row in old_fibro.iterrows():  # Iterate through old fibro lines
        old_line = old_row.geometry
        old_coords = list(old_line.coords)
        for j in range(len(old_coords) - 1):  # Iterate through old fibro segments
            old_segment = LineString([Point(old_coords[j]), Point(old_coords[j + 1])])

            if segment.intersects(old_segment.buffer(tolerance)):  # Check for overlap
                return "Modified"  # Overlapping segment found

    return "New Segment"  # No overlapping segment found


# Process each line feature with progress bar
for _, row in tqdm(
    fibro_line.iterrows(), total=fibro_line.shape[0], desc="Processing lines"
):
    line = row.geometry
    coords = list(line.coords)

    for i in range(len(coords) - 1):
        segment = LineString([Point(coords[i]), Point(coords[i + 1])])

        alignment_status = check_alignment(
            segment, new_cadaster, tolerance=0.5, min_overlap=0.5
        )  # Example values
        modification_status = check_modifications(
            segment, old_fibro_line, tolerance=1
        )  # Example values

        # Check if segment's midpoint is within 0.5m of any cadaster polygon
        midpoint = segment.centroid
        within_cadaster_buffer = False
        for poly in new_cadaster.geometry:
            if poly.buffer(0.5).contains(midpoint):
                within_cadaster_buffer = True
                break  # Exit loop once a containing polygon is found

        # ***KEY CHANGE: Check buffer BEFORE flagging***
        if not within_cadaster_buffer:  # Only proceed if NOT within buffer
            if alignment_status == "Misaligned" or modification_status in [
                "Modified",
                "New Segment",
            ]:
                temp_df = gpd.GeoDataFrame(
                    {
                        "geometry": [segment],
                        "status": [f"{alignment_status}, {modification_status}"],
                    },
                    crs=fibro_line.crs,
                )

                flagged_gdf = pd.concat([flagged_gdf, temp_df], ignore_index=True)

                # Add difference point (at segment midpoint)
                difference_points_gdf = pd.concat(
                    [
                        difference_points_gdf,
                        gpd.GeoDataFrame(
                            {
                                "geometry": [midpoint],
                                "status": [
                                    f"{alignment_status}, {modification_status}"
                                ],
                            },
                            crs=fibro_line.crs,
                        ),
                    ],
                    ignore_index=True,
                )


try:
    flagged_gdf.to_file("misaligned_segments/misaligned_segments.shp")
    difference_points_gdf.to_file(
        "misaligned_segments/difference_points.shp"
    )  # Save difference points!

    print("✅ Misaligned segments saved to 'misaligned_segments.shp'!")
    print("✅ Flagged points saved to misaligned_segments/difference_points.shp ")
except Exception as e:
    print(f"Error saving shapefile: {e}")
