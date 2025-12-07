import logging
import os
import sys
from functools import reduce

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)
from common import setup_logging

logger = setup_logging(logging.WARNING)


def parse(raw_data: str) -> list[str]:
    return raw_data.split("\n")


def solution1(data: list[str]) -> int:
    nums: list[list[int]] = []
    for line in data:
        if line == data[-1]:
            break
        clean = line.split()
        clean = list(map(int, clean))
        nums.append(clean)
    logger.info(f"{nums=}")
    operators: list[str] = data[-1].split()
    logger.info(f"{operators=}")
    total: int = 0
    for i in range(len(operators)):
        op = operators[i]
        target = [x[i] for x in nums]
        if op == "+":
            total += sum(target)
        elif op == "*":
            total += reduce(lambda x, y: x * y, target)
        logger.info(f"{total=}")
    return total


def get_problem_groups(data: list[str]) -> list[dict[str, list[str]]]:
    """
    Splits the grid into blocks based on empty columns and returns a list
    of dictionaries containing the operator and the rows for that block.
    """
    # 1. Pad all lines to the same length
    max_len = max(len(line) for line in data)
    padded_data = [line.ljust(max_len) for line in data]

    # 2. Identify indices of empty columns (separators)
    # zip(*padded_data) transposes rows to columns
    cols = list(zip(*padded_data))
    empty_col_indices = [i for i, col in enumerate(cols) if all(c == " " for c in col)]

    # Add start (0) and end (max_len) to indices to help slicing
    # We want ranges between separators
    boundaries = [-1] + empty_col_indices + [max_len]

    problem_groups = []

    # 3. Iterate through boundaries to slice blocks
    for k in range(len(boundaries) - 1):
        start = boundaries[k] + 1
        end = boundaries[k + 1]

        # Skip if start >= end (consecutive spaces)
        if start >= end:
            continue

        # Extract the rectangular block for this section
        block_rows = [row[start:end] for row in padded_data]

        # 4. Extract operator and number rows
        # The operator is in the last row of the block
        operator_row = block_rows[-1].strip()
        if not operator_row:
            continue  # Skip if purely empty block

        # The operator is usually the single non-space char in the last row
        operator = operator_row.strip()

        # The numbers are in all rows except the last one
        number_rows = block_rows[:-1]

        problem_groups.append({operator: number_rows})

    return problem_groups


def get_right_to_left(rows: list[str]) -> list[int]:
    """
    Reads a block of rows right-to-left.
    Col i (from right) -> construct number top-to-bottom.
    """
    ans: list[int] = []
    if not rows:
        return ans

    # Max length is the width of the block
    max_width = len(rows[0])

    # Iterate from 1 (rightmost character) to max_width
    for i in range(1, max_width + 1):
        # Construct the number string by picking the -i th character from every row
        # rows is ['  1', ' 24', '356']
        # i=1 -> '1', '4', '6' -> "146" (Wait, logic check below)

        col_chars = []
        for row in rows:
            if len(row) >= i:
                col_chars.append(row[-i])

        num_str = "".join(col_chars).strip()

        if num_str:
            ans.append(int(num_str))

    return ans


def solution2(data: list[str]) -> int:
    problem_groups = get_problem_groups(data)

    total_sum = 0

    logger.info(f"Found {len(problem_groups)} problem blocks.")
    logger.info(f"{problem_groups=}")

    for group in problem_groups:
        for operator, rows in group.items():
            # rows are passed to get_right_to_left
            # e.g., rows = [' 64', ' 23', '314'] (Rightmost block)
            results = get_right_to_left(rows)

            logger.info(f"Operator: {operator}, Rows: {rows}, Operands: {results}")

            if operator == "+":
                total_sum += sum(results)
            elif operator == "*":
                product = 1
                for num in results:
                    product *= num
                total_sum += product

    return total_sum


test_data: str = """\
123 328  51 64 
 45 64  387 23 
  6 98  215 314
*   +   *   +  """


@pytest.fixture
def input_data() -> str:
    return test_data


@pytest.mark.parametrize(
    "expected, solution",
    [
        # (4277556, solution1),
        (3263827, solution2),
    ],
)
def test_solutions(input_data, expected, solution):
    result = solution(parse(input_data))
    assert result == expected, f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    "input_list, expected_output",
    [
        (["64 ", "23 ", "314"], [4, 431, 623]),
        ([" 51", "387", "215"], [175, 581, 32]),
        (["328", "64 ", "98 "], [8, 248, 369]),
        (["123", " 45", "  6"], [356, 24, 1]),
        (["15", "23", " 4"], [534, 12]),
        (["97  ", "511 ", "743 ", "3239"], [9, 133, 7142, 9573]),
    ],
)
def test_get_right_to_left(input_list, expected_output):
    assert get_right_to_left(input_list) == expected_output


@pytest.mark.parametrize(
    "input_lines, expected_length, expected_first_op, expected_first_rows",
    [
        # Case 1: Single block (no spaces)
        (["12", "34", "+ "], 1, "+", ["12", "34"]),
        # Case 2: Two blocks separated by one space
        # Note: Input is padded automatically by the function, but providing aligned strings helps clarity
        (["1 2", "3 4", "+ *"], 2, "+", ["1", "3"]),
        # Case 3: Uneven line lengths (function should pad them)
        (
            ["1 2", "3", "+ *"],  # Missing chars here
            2,
            "+",
            ["1", "3"],  # "3" becomes "3 " after padding, then sliced to "3"
        ),
    ],
)
def test_get_problem_groups(
    input_lines, expected_length, expected_first_op, expected_first_rows
):
    groups = get_problem_groups(input_lines)

    # Check we found the right number of blocks
    assert len(groups) == expected_length

    # Check the first block's content
    first_group = groups[0]
    # The key should be the operator
    assert expected_first_op in first_group
    # The value should be the rows of numbers
    assert first_group[expected_first_op] == expected_first_rows
