from shapely.geometry import LineString, Point
import geopandas as gpd
import math

def check_modifications(segment, old_fibro, modification_tolerance, distance_tolerance):
    """
    Checks if segments of a line have been modified compared to old_fibro line segments.
    """
    segment_coords = list(segment.coords)

    for _, old_row in old_fibro.iterrows():
        old_line = old_row.geometry
        old_coords = list(old_line.coords)

        # Check if the number of segments is the same
        if len(segment_coords) - 1 != len(old_coords) - 1:
            continue  # Skip if segment counts don't match

        for i in range(len(segment_coords) - 1):
            segment_part = LineString([Point(segment_coords[i]), Point(segment_coords[i + 1])])
            old_segment_part = LineString([Point(old_coords[i]), Point(old_coords[i + 1])])

            # Check for intersection (shape modification)
            if segment_part.intersects(old_segment_part.buffer(modification_tolerance)):
                return "Modified"

            # Check for distance (parallel line displacement)
            distance = segment_part.distance(old_segment_part)
            if distance > distance_tolerance:
                # Check if the lines are mostly parallel to prevent false positives
                if is_mostly_parallel(segment_part, old_segment_part):
                    return "Modified"

    return "New Segment"

def is_mostly_parallel(line1, line2, angle_tolerance=15):
    """Checks if two lines are mostly parallel within an angle tolerance."""
    angle1 = calculate_line_angle(line1)
    angle2 = calculate_line_angle(line2)
    angle_diff = abs(angle1 - angle2)
    return min(angle_diff, 180 - angle_diff) <= angle_tolerance

def calculate_line_angle(line):
    """Calculates the angle of a line in degrees."""
    coords = list(line.coords)
    if len(coords) < 2:
        return 0  # Handle degenerate cases
    dx = coords[-1][0] - coords[0][0]
    dy = coords[-1][1] - coords[0][1]
    return math.degrees(math.atan2(dy, dx))