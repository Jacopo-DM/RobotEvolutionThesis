#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
from dataclasses import dataclass
from random import Random
from typing import List


@dataclass
class Item:
    """Item for the knapsack problem."""

    weight: float
    value: float


def random_items(
    rng: Random, num_of_items: int, low_range: int, high_range: int
) -> List[Item]:
    """Generate a list of random items."""

    # Generate a list of random items
    items = []
    for _ in range(0, num_of_items):
        weight = rng.randrange(low_range, high_range)  # could be uniform
        value = rng.randrange(low_range, high_range)  # could be uniform
        items.append(Item(weight, value))
    return items


def _test() -> None:
    """Test the Item class."""

    # Test the Item class
    item = Item(value=1, weight=2)
    print(f"item: {item}")

    # Test the random_items function
    items = random_items(rng=Random(), num_of_items=3, low_range=1, high_range=10)
    print(f"items: {items}")
    print(f"len(items): {len(items)}")


if __name__ == "__main__":
    _test()
