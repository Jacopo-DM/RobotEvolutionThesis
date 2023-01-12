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

# Local libraries
try:
    from .genotype import Genotype
    from .item import Item
except ImportError:
    from genotype import Genotype  # type: ignore # FIXME stubs and multiple imports
    from item import Item  # type: ignore # FIXME stubs and multiple imports


@dataclass
class Phenotype:
    """Phenotype for the knapsack problem."""

    genotype: Genotype
    max_weight: float
    solution: List[bool]
    items: List[Item]
    total_weight: float
    total_value: float

    def __init__(
        self, rng: Random, genotype: Genotype, items: List[Item], max_weight: float
    ) -> None:
        """Initialize a phenotype."""

        # Store the genotype and the maximum weight
        self.genotype = genotype
        self.max_weight = max_weight

        # Synthesise the phenotype into a valid solution
        self.rng = rng
        self.synthesise(items)

        # Update the total weight and total value
        self.total_weight = self.get_total_weight()
        self.total_value = self.get_total_value()

    def get_total_weight(self) -> float:
        """Get the total weight of the phenotype."""
        return float(sum([item.weight for item in self.items]))

    def get_total_value(self) -> float:
        """Get the total value of the phenotype."""
        return float(sum([item.value for item in self.items]))

    def synthesise(self, items: List[Item]) -> None:
        """Synthesise the phenotype into a valid solution."""

        # Get the number of items
        num_of_items = len(self.genotype.items)

        # Generate random list of indices, only for items that are in the genotype
        indices = [i for i in range(0, num_of_items) if self.genotype.items[i] is True]
        self.rng.shuffle(indices)

        # Create the solution
        self.solution = [False for _ in range(0, num_of_items)]

        # Add items to the solution until the total weight is greater than the max weight
        total_weight = 0.0
        for index in indices:
            # Add the item to the solution if it does not exceed the max weight
            if total_weight + items[index].weight <= self.max_weight:
                self.solution[index] = True
                total_weight += items[index].weight

            # Stop if the total weight exceeds the max weight
            if total_weight >= self.max_weight:
                break

        # Get items from solution
        self.items = [items[i] for i in range(0, num_of_items) if self.solution[i]]


def _test() -> None:
    """Test the Phenotype class."""

    # Test synthesise
    rng = Random()
    items = [
        Item(1.0, 1.0),
        Item(2.0, 2.0),
        Item(3.0, 3.0),
        Item(4.0, 4.0),
        Item(5.0, 5.0),
    ]
    genotype = Genotype([True, True, True, True, True])
    phenotype = Phenotype(rng=rng, genotype=genotype, items=items, max_weight=10.0)
    print(f"geno: {phenotype.genotype}")
    print(f"pheno: {phenotype.solution}")

    # Test get_total_weight and get_total_value
    print(f"total_weight: {phenotype.get_total_weight()}")
    print(f"total_value: {phenotype.get_total_value()}")


if __name__ == "__main__":
    _test()
