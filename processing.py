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
    tolerance,
    min_overlap,
    modification_tolerance,
):
    """Processes each line feature and flags misaligned/modified segments."""
    flagged_gdf = gpd.GeoDataFrame(columns=["geometry", "status"], crs=fibro_line.crs)
    difference_points_gdf = gpd.GeoDataFrame(
        columns=["geometry", "status"], crs=fibro_line.crs
    )

    for _, row in tqdm(
        fibro_line.iterrows(), total=fibro_line.shape[0], desc="Processing lines"
    ):
        line = row.geometry
        coords = list(line.coords)

        for i in range(len(coords) - 1):
            segment = LineString([Point(coords[i]), Point(coords[i + 1])])

            alignment_status = check_alignment(
                segment, new_cadaster, tolerance, min_overlap
            )
            modification_status = check_modifications(
                segment, old_fibro_line, modification_tolerance
            )

            midpoint = segment.centroid
            within_cadaster_buffer = False
            for poly in new_cadaster.geometry:
                if poly.buffer(0.5).contains(midpoint):
                    within_cadaster_buffer = True
                    break

            if not within_cadaster_buffer:
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

    return flagged_gdf, difference_points_gdf
