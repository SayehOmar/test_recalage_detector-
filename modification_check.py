from shapely.geometry import LineString, Point


def check_modifications(segment, old_fibro, modification_tolerance):
    """Checks if a segment has been modified compared to old_fibro lines."""
    for _, old_row in old_fibro.iterrows():
        old_line = old_row.geometry
        old_coords = list(old_line.coords)
        for j in range(len(old_coords) - 1):
            old_segment = LineString([Point(old_coords[j]), Point(old_coords[j + 1])])

            if segment.intersects(old_segment.buffer(modification_tolerance)):
                return "Modified"

    return "New Segment"
