import geopandas as gpd
from shapely.geometry import LineString


def check_alignment(segment, cadaster, tolerance, min_overlap):
    """Checks if a segment is aligned with the cadaster."""
    buffered_cadaster = cadaster.geometry.buffer(tolerance)
    intersected = segment.intersects(buffered_cadaster)
    contained = segment.within(buffered_cadaster)

    if contained.any():
        return "Correct"
    elif intersected.any():
        intersection = segment.intersection(buffered_cadaster[intersected])

        if isinstance(intersection, gpd.GeoSeries):
            if not intersection.is_empty.any():
                return "Misaligned"
            intersection_length = intersection.length.sum()
        elif not intersection.is_empty:
            if intersection.geom_type == "MultiLineString":
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
