import logging
import os
import sys
from copy import deepcopy
from functools import cache
from typing import Hashable, List, Tuple  # Using typing for clarity

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
from common import setup_logging

logger = setup_logging(logging.INFO)


def parse(raw_data: str) -> list[list[int]]:
    # returns [[x1, y1], [x2, y2]]
    # example [[7, 1], [11, 1], ...]
    return [list(map(int, x.split(","))) for x in raw_data.splitlines()]


def get_rectangle_size(p1: list[int], p2: list[int]) -> int:
    """
    Calculates the area of a rectangle defined by two opposite corner tile coordinates (p1 and p2).

    The calculation is *inclusive*, meaning it counts all unit tiles from the start coordinate
    up to and including the end coordinate in both the X and Y dimensions.

    Args:
        p1 (list[int] | tuple[int, int]): The coordinates [x1, y1] of the first corner tile.
        p2 (list[int] | tuple[int, int]): The coordinates [x2, y2] of the second corner tile.

    Returns:
        int: The total number of unit tiles contained within the rectangle (Area).
    """
    # Assume p1 = [x1, y1] and p2 = [x2, y2] are passed correctly.
    x1, y1 = p1
    x2, y2 = p2

    # Calculate the side lengths. For unit tiles, the length includes the start and end tiles.
    # E.g., from X=5 to X=7 (5, 6, 7) is a length of 3, not 7 - 5 = 2.
    # Therefore, we must add 1 to the absolute difference of the coordinates.
    length = abs(x1 - x2) + 1  # Width (X-dimension)
    breadth = abs(y1 - y2) + 1  # Height (Y-dimension)

    # Calculate the total area (number of tiles)
    return length * breadth


def solution1(data: list[list[int]]) -> int:
    largest_rect = {}
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            largest_rect[(i, j)] = get_rectangle_size(data[i], data[j])
    return max(largest_rect.values())


def solution2(data) -> int:
    @cache
    def point_in_poly(x: int, y: int) -> bool:
        """
        Determines if a given point (x, y) is inside or on the boundary of the polygon
        defined by 'points'[(1,2),(3,4)]

        This implementation uses the Ray Casting (or Crossing Number) algorithm for the
        interior check and explicitly checks the boundary for inclusive containment.

        Args:
            x (int): The x-coordinate of the point to check.
            y (int): The y-coordinate of the point to check.
            `points` list[list[int]]: A tuple of (x, y) tuples defining the polygon vertices
                                        in sequential order (clockwise or counter-clockwise).

        Returns:
            bool: True if the point is inside or on the boundary, False otherwise.
        """
        inside = False
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
            if (
                x == x1 == x2
                and min(y1, y2) <= y <= max(y1, y2)
                or y == y1 == y2
                and min(x1, x2) <= x <= max(x1, x2)
            ):
                return True
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside

        return inside

    def edge_intersects_rect(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
        """
        Checks if a polygon edge segment strictly intersects the interior of a rectangle.

        This function is crucial for ensuring no part of the polygon boundary cuts through
        the interior of a candidate rectangle, which would invalidate the rectangle.

        Args:
            x1, y1 (int): Start point of the polygon edge segment.
            x2, y2 (int): End point of the polygon edge segment.
            rx1, ry1 (int): Minimum x and y coordinates of the rectangle (inclusive boundary).
            rx2, ry2 (int): Maximum x and y coordinates of the rectangle (inclusive boundary).
                            It is assumed that rx1 <= rx2 and ry1 <= ry2 (i.e., they are sorted).

        Returns:
            bool: True if the edge intersects the strict interior of the rectangle, False otherwise.
        """
        # 1. Handle Horizontal Polygon Edges
        if y1 == y2:
            # Check if the horizontal edge's y-coordinate is STRICTLY between the rectangle's y-bounds.
            # This means the edge must pass through the vertical extent of the interior.
            if ry1 < y1 < ry2:
                # Check for overlap in the X dimension.
                if max(x1, x2) > rx1 and min(x1, x2) < rx2:
                    return True
        # 2. Handle Vertical Polygon Edges
        else:  # Assumes the polygon is made of only vertical and horizontal segments (x1 == x2).
            # Check if the vertical edge's x-coordinate is STRICTLY between the rectangle's x-bounds.
            # This means the edge must pass through the horizontal extent of the interior.
            if rx1 < x1 < rx2:
                # Check for overlap in the Y dimension.
                ey_min, ey_max = min(y1, y2), max(y1, y2)
                # The edge intersects if its maximum y is greater than the rectangle's minimum y,
                # AND its minimum y is less than the rectangle's maximum y.
                if ey_max > ry1 and ey_min < ry2:
                    return True
        return False

    def square_valid(x1: int, x2: int, y1: int, y2: int) -> bool:
        """
        Checks if the rectangle defined by two red tiles (x1, y1) and (x2, y2)
        is entirely contained within the red/green filled area (the polygon boundary + interior).

        The validation requires three conditions to be met for the rectangle to be valid:
        1. All four corners must be within the filled area.
        2. No polygon edge must intersect the interior of the rectangle.
        3. (Conceptual Check Missing Below): An interior point must be inside the polygon
           to distinguish contained rectangles from external ones.

        Args:
            x1, y1 (int): Coordinates of the first red tile corner.
            x2, y2 (int): Coordinates of the second red tile corner.
            points (List[Tuple[int, int]]): The ordered list of polygon vertices.

        Returns:
            bool: True if the entire rectangle is valid (only contains red or green tiles),
                  False otherwise.
        """
        # Ensure coordinates are sorted to define the rectangle bounds (min/max)
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        # --- 1. Check Corner Validity ---
        for x, y in [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]:
            if not point_in_poly(x, y):
                return False
        # --- 2. Check for Edge Intersections ---
        for (ex1, ey1), (ex2, ey2) in zip(points, points[1:] + points[:1]):
            if edge_intersects_rect(ex1, ey1, ex2, ey2, x1, y1, x2, y2):
                return False
        return True

    points = data
    max_area = 0
    for i, (x1, y1) in enumerate(points):
        for j, (x2, y2) in enumerate(points):
            if i < j:
                current_area = (abs(x1 - x2) + 1) * (abs(y1 - y2) + 1)
                if current_area > max_area and square_valid(x1, x2, y1, y2):
                    max_area = current_area
    return max_area


test_data: str = """7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
"""


# For ipython -
def get_test_data() -> str:
    return test_data


@pytest.fixture
def input_data() -> str:
    return test_data


@pytest.mark.parametrize(
    "expected, solution",
    [
        (50, solution1),
        # (0, solution2),
        (24, solution2),
    ],
)
def test_solutions(input_data, expected, solution):
    result = solution(parse(input_data))
    assert result == expected, f"Expected {expected}, got {result}"
