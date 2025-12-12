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
            # print(data[i], data[j])
            largest_rect[(i, j)] = get_rectangle_size(data[i], data[j])
    # logger.info(f"{largest_rect=}")
    return max(largest_rect.values())


def print_grid(grid: list[list[str]]):
    """Helper function to print the grid."""
    print("\n".join("".join(row) for row in grid))


def create_grid_with_coordinates(original_coordinates, offset):
    # Calculate the necessary grid dimensions with offsets on all sides
    max_x = max(x for x, y in original_coordinates) + offset
    max_y = max(y for x, y in original_coordinates) + offset

    # Initialize the grid with dots
    grid_width = max_x + offset + 1  # Total width includes left and right offsets
    grid_height = max_y + offset + 1  # Total height includes top and bottom offsets

    grid = [["." for _ in range(grid_width)] for _ in range(grid_height)]

    new_positions = []
    for x, y in original_coordinates:
        # Adjust coordinates by the offset
        new_x: int = x + offset
        new_y: int = y + offset
        # Place '#' in the grid
        grid[new_y][new_x] = "#"
        # Store new coordinates
        new_positions.append((new_x, new_y))
    print_grid(grid)
    new_grid = fill_greens(grid, new_positions)
    # print_grid(new_grid)
    return new_positions, new_grid


def fill_greens(grid: list[list[str]], positions):
    rows, cols = len(grid), len(grid[0])
    print(f"{rows=}, {cols=}")
    new_grid = deepcopy(grid)

    for x, y in positions:
        print("\n---------\n", x, y, end="-------------------: \n")
        # go down until
        for i in range(x, rows):
            print("down: ")
            print(f"{i},{y}", end=" ")
        # go right
        print("\n")
        for j in range(y, cols):
            print("right:")
            print(f"{x},{j}", end=" ")

    return [[]]


def solution2(data: list[list[int]]) -> int:
    """
    Optimized solution using Coordinate Compression and 2D Prefix Sum.
    """
    # data = [[1,1], [0,1],[0,0],[1,0]]
    logger.info(f"{data=}")

    for i in range(3):
        new_data, grid = create_grid_with_coordinates(data, i)
        logger.info(f"offset {i}: \n{new_data=}\n")
        print_grid(grid)
        print("\n")
    return 0


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
