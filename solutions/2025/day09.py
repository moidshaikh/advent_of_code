import logging
import os
import sys
from copy import deepcopy

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
from common import setup_logging

logger = setup_logging(logging.INFO)


def parse(raw_data: str) -> list[list[int]]:
    # returns [[x1, y1], [x2, y2]]
    # example [[7, 1], [11, 1], ...]
    return [list(map(int, x.split(","))) for x in raw_data.splitlines()]


def get_rectangle_size(p1, p2) -> int:
    x1, x2 = p1
    y1, y2 = p2
    length = abs(y1 - x1) + 1
    breadth = abs(y2 - x2) + 1
    # logger.info(f"{length=} {breadth=}")
    return length * breadth


def solution1(data: list[list[int]]) -> int:
    # for largest rectangle, we can find largest rectangle by 2 points,
    # iterate twice to get all points, save it against those point in largest_rectangle
    largest_rect = {}
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            # logger.info(data[i], data[j])
            largest_rect[(i, j)] = get_rectangle_size(data[i], data[j])
    # logger.info(f"{largest_rect=}")
    return max(largest_rect.values())


def print_grid(grid: list[list[str]]):
    """Helper function to print the grid."""
    logger.info("\n".join("".join(row) for row in grid))


def create_grid_with_coordinates(original_coordinates, offset):

    ## PART 1: Getting correct offset
    # Calculate the necessary grid dimensions with offsets on all sides
    max_x = max(x for x, y in original_coordinates) + offset
    max_y = max(y for x, y in original_coordinates) + offset

    # Initialize the grid with dots
    grid_width = max_x + offset + 1  # Total width includes left and right offsets
    grid_height = max_y + offset + 1  # Total height includes top and bottom offsets
    logger.info(f"{grid_width=}, {grid_height=}")

    grid = [["." for _ in range(grid_width)] for _ in range(grid_height)]

    new_positions = []
    ## PART 1.B: adding red lights
    for x, y in original_coordinates:
        # Adjust coordinates by the offset
        new_x: int = x + offset
        new_y: int = y + offset
        # Place '#' in the grid
        grid[new_y][new_x] = "#"
        # Store new coordinates
        new_positions.append((new_x, new_y))
    logger.info(f"new positions: {new_positions}")

    logger.info(f"Adding red lights...")
    print_grid(grid)

    new_grid = deepcopy(grid)

    ## PART 2: Adding green lines between red lights
    def fill_line(p1: tuple[int, int], p2: tuple[int, int]):
        # Helper function to add green lights between reds
        x1, y1 = p1
        x2, y2 = p2
        smaller, larger = 0, 0
        same_x = 1 if x1 == x2 else 0
        same_y = 1 if y1 == y2 else 0
        if same_y:
            # logger.info(f"same x for: {p1},{p2}")
            smaller = min(x1, x2)
            larger = max(x1, x2)
        if same_x:
            # logger.info(f"same y for: {p1},{p2}")
            smaller = min(y1, y2)
            larger = max(y1, y2)
        # logger.info("- - - - - - - - - - - - - - - - - - - - ")
        # logger.info(f"{smaller=}, {larger=}")
        for i in range(smaller + 1, larger):
            try:
                if same_y:
                    # logger.info(f"{i},{y1}", end=" ")
                    new_grid[y1][i] = "X"
                if same_x:
                    # logger.info(f"{x1},{i}", end=" ")
                    new_grid[i][x1] = "X"
            except:
                logger.info(f"-----green fill failed for {i},{x1},{y1}")
        # logger.info(f"green values for {p1},{p2} at: ")

    i = 0
    for p1, p2 in [
        (x, y) for x, y in zip(new_positions, new_positions[1:] + [new_positions[0]])
    ]:
        i += 1
        fill_line(p1, p2)
    logger.info(f"fill lines called {i} times.")
    logger.info("adding green lines")
    logger.info("-----------\n\n\n")

    ### PART3: filling in green points between the created shape.

    # print_grid(new_grid)
    return new_positions, new_grid


### PART3: filling in green points between the created shape.
def fill_enclosed_spaces(grid):
    rows = len(grid)
    cols = len(grid[0])
    grid = [list(row) for row in grid]  # Convert strings to lists for mutability

    # Directions for moving up, down, left, right
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Flood fill from the borders
    def flood_fill(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != ".":
            return
        grid[r][c] = "F"  # Mark the area that cannot be filled
        for dr, dc in directions:
            flood_fill(r + dr, c + dc)

    # Fill from the borders
    for i in range(rows):
        if grid[i][0] == ".":
            flood_fill(i, 0)
        if grid[i][cols - 1] == ".":
            flood_fill(i, cols - 1)
    for j in range(cols):
        if grid[0][j] == ".":
            flood_fill(0, j)
        if grid[rows - 1][j] == ".":
            flood_fill(rows - 1, j)

    # Convert remaining '.' to 'X'
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == ".":
                grid[i][j] = "X"  # Fill enclosed spaces
            elif grid[i][j] == "F":
                grid[i][j] = "."  # Restore unfilled areas back to '.'

    return [list(row) for row in grid]


def get_min_max(x1: int, y1: int, x2: int, y2: int) -> tuple[int, ...]:
    min_x = x1 if x1 < x2 else x2
    min_y = y1 if y1 < y2 else y2

    max_x = x1 if x1 > x2 else x2
    max_y = y1 if y1 > y2 else y2

    logger.info(f"({x1},{x2}) ({y1},{y2}): {min_x}, {max_x}, {min_y}, {max_y}")

    return min_x, max_x, min_y, max_y


def check_valid(
    x1: int, y1: int, x2: int, y2: int, grid_data: list[list[str]]
) -> tuple[bool, int]:
    """
    Checks if the rectangle defined by (x1, y1) and (x2, y2) consists only of '#' or 'X' tiles.
    The check is inclusive of the corner tiles.
    """
    rows = len(grid_data)
    cols = len(grid_data[0])

    # Determine the inclusive boundaries
    min_x = min(x1, x2)
    max_x = max(x1, x2)
    min_y = min(y1, y2)
    max_y = max(y1, y2)

    # Check for invalid tiles ('.')
    for y in range(min_y, max_y + 1):  # +1 to include max_y
        for x in range(min_x, max_x + 1):  # +1 to include max_x
            # Guard against accessing outside the grid (should not happen if offset is sufficient)
            if y < 0 or y >= rows or x < 0 or x >= cols:
                # This path indicates a flaw in grid sizing/offset, but we treat it as invalid rectangle
                return False, 0

            if grid_data[y][x] == ".":
                return False, 0

    # Calculate the inclusive area
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    area = width * height

    return True, area


def solution2(data: list[list[int]]) -> int:
    """
    Fixed solution for the brute-force grid approach.
    """
    # 1. Prepare the full grid (Red boundary + Green fill)
    # Using offset=1 based on your original code
    new_positions, grid = create_grid_with_coordinates(data, 1)
    new_grid = fill_enclosed_spaces(grid)

    # print_grid(new_grid) # The grid is now ready

    max_area = 0
    N = len(new_positions)

    # 2. Iterate through ALL pairs of red tiles (p_i, p_j) to check for valid rectangles
    for i in range(N):
        for j in range(
            i + 1, N
        ):  # Start j from i+1 to avoid (p_i, p_i) and redundant pairs (p_j, p_i)
            p1 = new_positions[i]
            p2 = new_positions[j]

            x1, y1 = p1
            x2, y2 = p2

            # The two red tiles must be opposite corners, meaning they must define
            # a width and height greater than 0.
            if x1 == x2 or y1 == y2:
                # Rectangles with zero width or height are not what is intended for max area
                # Although they might be technically valid, they are not the maximum.
                continue

            # Check the rectangle formed by the opposite corners p1 and p2
            is_valid, area = check_valid(x1, y1, x2, y2, new_grid)

            if is_valid:
                max_area = max(max_area, area)

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


## testing helper functions


@pytest.mark.parametrize(
    "p1, p2, exp",
    [
        # Sample input
        ([2, 5], [9, 7], 24),
        ([2, 7], [9, 5], 24),
        ([9, 7], [2, 5], 24),
    ],
)
def test_distance_between_two_points(p1, p2, exp):
    result = get_rectangle_size(p1, p2)
    assert result == exp, f"Expected {exp}, got {result}"


"""
...............
...............
.......x.......
...............
...............
...............
...............
...............
...............
.....x.........
...............
...............
...............
...............
...............
...............

"""
