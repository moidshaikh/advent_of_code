import logging
import os
import sys
from collections import deque
from functools import cache

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
from common import setup_logging

logger = setup_logging(logging.WARN)


def parse(raw_data: str) -> list[list[str]]:
    return [list(x) for x in raw_data.split("\n")]


def find_S_position(grid: list[list[str]]) -> tuple[int, int]:
    rows, cols = len(grid), len(grid[0])
    loc: tuple[int, int] = (-1, -1)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "S":
                loc = (r, c)
    logger.info(f"`S` position for grid found at: {loc}")
    return loc


def solution1(data: list[list[str]]) -> int:
    start_loc: tuple[int, int] = find_S_position(data)
    # initialize dequeue for bfs.
    queue: deque = deque([(start_loc[0] + 1, start_loc[1])])
    splitters_loc = set()
    while queue:
        r, c = queue.popleft()
        # current
        curr_r = r
        while curr_r < len(data):
            # check if column is inbounds
            if not (0 <= c < len(data[0])):
                break
            cell = data[curr_r][c]
            if cell == "^":
                # we got a splitter
                if (curr_r, c) not in splitters_loc:
                    splitters_loc.add((curr_r, c))
                    # beam split
                    queue.append((curr_r, c - 1))
                    queue.append((curr_r, c + 1))
                break  # beam will always stop at splitter
            # if its '.', we keep moving down
            curr_r += 1
    total: int = len(splitters_loc)
    logger.info(f"Solution1 result: {total}")
    return total


def solution2(data: list[list[str]]) -> int:
    rows, cols = len(data), len(data[0])
    start_loc: tuple[int, int] = find_S_position(data)
    logger.info(f"{start_loc=}")

    @cache
    def get_timelines(r, c):
        # Base Case 1: Out of bounds (Hit side wall)
        # A timeline that goes out of bounds is considered a complete timeline that exited.
        logger.info(f"get_timelines called for: {r},{c}")
        if not (0 <= c < cols):
            return 1
        # Base Case 2: Hit bottom
        if r == rows:
            return 1
        # Check the cell type at the current position
        cell: str = data[r][c]
        if cell == ".":
            # empty space, continue straight down
            return get_timelines(r + 1, c)
        elif cell == "^":
            # found Splitter, timeline splits into 2 paths
            return get_timelines(r + 1, c - 1) + get_timelines(r + 1, c + 1)
        # 'S' is only the starting point
        elif cell == "S":
            return get_timelines(r + 1, c)
        return 0

    # The result is the number of timelines starting just below 'S'
    # The start is effectively at (start_r + 1, start_c)
    result: int = get_timelines(start_loc[0] + 1, start_loc[1])
    logger.info(f"Solution2 : {result=}")
    return result


test_data: str = """.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
..............."""


@pytest.fixture
def input_data() -> str:
    return test_data


@pytest.mark.parametrize(
    "expected, solution",
    [
        (21, solution1),
        (40, solution2),
    ],
)
def test_solutions(input_data, expected, solution):
    result = solution(parse(input_data))
    assert result == expected, f"Expected {expected}, got {result}"
