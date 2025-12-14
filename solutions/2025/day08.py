import logging
import os
import sys
from collections import defaultdict
from math import prod

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
from common import setup_logging

logger = setup_logging(logging.INFO)


def parse(raw_data: str) -> list[str]:
    return [x for x in raw_data.split("\n") if len(x) > 0]


def squared_distance_between_two_points(p1: list[int], p2: list[int]) -> int:
    dist: int = 0
    for i in range(len(p1)):
        dist += (p1[i] - p2[i]) ** 2
    return dist


def find_set(parent, v):
    if v == parent[v]:
        return v
    parent[v] = find_set(parent, parent[v])
    return parent[v]


def union_sets(parent, a, b):
    a = find_set(parent, a)
    b = find_set(parent, b)
    if a != b:
        parent[b] = a


def union_by_rank(parent, rank, x, y):
    px, py = find_set(parent, x), find_set(parent, y)
    if px == py:
        return False  # already in same circuit
    if rank[px] < rank[py]:
        px, py = py, px
    parent[py] = px
    if rank[px] == rank[py]:
        rank[px] += 1
    return True


def solution1(data: list[str]) -> int:
    # data here is cleaned data from parse func above
    # Distance between 2 points in 3 dimensions:
    points = []
    for line in data:
        x, y, z = map(int, line.split(","))
        points.append((x, y, z))
    # print(f"{points=}")

    distances = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            p1 = points[i]
            p2 = points[j]
            distances.append((squared_distance_between_two_points(p1, p2), p1, p2))
    # distances => [distance, p1, p2] => [distance: int, [x1,x2,x3]: p1, [y1,y2,y3]:p2]
    # print(f"{distances[2]=}")

    # Now we use Union Find with : union, find_set: https://cp-algorithms.com/data_structures/disjoint_set_union.html

    # Make Set:
    # parent = {i: i for i in points}
    parent = {i: i for i in points}
    # print(f"{parent}")

    WIRE_COUNT: int = 10 if len(points) < 21 else 1000

    for d, p1, p2 in sorted(distances)[:WIRE_COUNT]:
        union_sets(parent, p1, p2)
    # print(f"{parent=}")

    sizes = defaultdict(int)

    for p in points:
        # print(f"{p=}")
        sizes[find_set(parent, p)] += 1
    sizes_val_sorted = sorted(sizes.values(), reverse=True)
    # print(f"{sizes_val_sorted=}")
    return prod(sizes_val_sorted[:3])


def solution2(data: list[str]) -> int:
    # 1. Parse points (store as a list of tuples)
    points = []
    for line in data:
        x, y, z = map(int, line.split(","))
        points.append((x, y, z))

    n = len(points)

    # 2. Initialize DSU structure
    parent = list(range(n))
    size = [1] * n  # Used for union by size optimization

    # Helper function for Find with path compression (internal)
    def find_set(v):
        if v == parent[v]:
            return v
        parent[v] = find_set(parent[v])
        return parent[v]

    # Helper function for Union by Size (internal)
    # Returns True if a union occurred, False otherwise
    def union_sets(a, b):
        root_a = find_set(a)
        root_b = find_set(b)

        if root_a != root_b:
            # Union by Size: attach smaller tree to root of larger tree
            if size[root_a] < size[root_b]:
                root_a, root_b = root_b, root_a

            parent[root_b] = root_a
            size[root_a] += size[root_b]
            return True  # Successful union
        return False

    # 3. Calculate all pairwise distances (edges)
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            p1 = points[i]
            p2 = points[j]
            # Store (squared_distance, index_i, index_j)
            distances.append((squared_distance_between_two_points(p1, p2), i, j))

    # 4. Sort edges by distance
    distances.sort(key=lambda x: x[0])

    # 5. Process edges until only one circuit remains

    # Total successful connections needed is N - 1
    successful_connections_needed = n - 1
    connections_made = 0

    # Variables to store the indices of the last connected pair
    last_i, last_j = None, None

    for dist, i, j in distances:
        if connections_made >= successful_connections_needed:
            break

        # Attempt to unite the circuits of i and j
        if union_sets(i, j):
            connections_made += 1
            last_i, last_j = (
                i,
                j,
            )  # This edge is the 'last' successful connection so far

    # 6. Calculate the final result

    # The last edge (last_i, last_j) is the one that completed the MST (N-1 connections).
    # We need the X-coordinates of points[last_i] and points[last_j].
    # Points are stored as (X, Y, Z), so X is at index 0.

    if last_i is not None and last_j is not None:
        x_coord_i = points[last_i][0]
        x_coord_j = points[last_j][0]
        result = x_coord_i * x_coord_j
        return result
    else:
        # This case should not happen if N > 0
        return 0


test_data: str = """162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689"""


# for ipython
def get_sample_input() -> str:
    return test_data


@pytest.fixture
def input_data() -> str:
    return test_data


@pytest.mark.parametrize(
    "expected, solution",
    [
        (40, solution1),
        (25272, solution2),
    ],
)
def test_solutions(input_data, expected, solution):
    result = solution(parse(input_data))
    assert result == expected, f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    "p1, p2, exp",
    [
        # Test with typical points in 3D space
        ([162, 817, 812], [57, 618, 57], 620651),
        # Test with two identical points (should return 0)
        ([0, 0, 0], [0, 0, 0], 0),
        # Test with points in different quadrants
        ([3, 6, 8], [-1, -2, -3], 201),
        # Test with points at the origin and another point
        ([0, 0, 0], [3, 4, 0], 25),
        # Test with points having negative coordinates
        ([-3, -4, -5], [-1, -2, -3], 12),
        # Test with points very close together
        ([1.000001, 1.000002, 1.000003], [1, 1, 1], 1.3999999999916978e-11),
        # Test with points that will create larger distances
        ([10, 20, 30], [40, 50, 60], 2700),
        # Extreme values
        ([1e9, 1e9, 1e9], [2e9, 2e9, 2e9], 3e18),
    ],
)
def test_distance_between_two_points(p1, p2, exp):
    result = squared_distance_between_two_points(p1, p2)
    assert result == exp, f"Expected {exp}, got {result}"
