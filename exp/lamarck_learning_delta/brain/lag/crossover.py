#!/usr/bin/env python3

"""
Author:     as, jl. jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
from random import Random

# Third-party libraries
import numpy as np

# Local libraries
from .genotype import Genotype


def crossover(
    parent1: Genotype,
    parent2: Genotype,
    rng: Random,
    crossover_prob: float,
) -> Genotype:
    """Perform uniform crossover between two LAG genotypes.

    Parameters
    ----------
    parent1 : Genotype
        The first parent. (remains unchanged)
    parent2 : Genotype
        The second parent. (remains unchanged)
    rng : multineat.RNG
        Random number generator.
    crossover_prob : float
        The probability of crossover.

    Returns
    -------
    Genotype
        The result of crossover.
    """

    genotype = np.ones(parent1.genotype.shape[0]) * 0.5
    for i in range(genotype.shape[0]):
        if rng.uniform(0, 1) < crossover_prob:
            genotype[i] = parent1.genotype[i]
        else:
            genotype[i] = parent2.genotype[i]

    return Genotype(genotype, parent1.grid_size)
