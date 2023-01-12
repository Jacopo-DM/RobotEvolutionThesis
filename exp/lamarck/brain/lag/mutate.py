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


def mutate(
    genotype: Genotype,
    rng: Random,
    bound: float,
    mutate_prob: float,
) -> Genotype:
    """
    Mutate a LAG genotype. (random uniform mutation)

    Parameters
    ----------
    genotype : Genotype
        The genotype to mutate. (remains unchanged)
    rng : multineat.RNG
        Random number generator.
    bound : float
        The mutation bound.
    mutate_prob : float
        The mutation probability.

    Returns
    -------
    Genotype
        The result of mutation. (mutated copy)
    """

    individual = np.ones(genotype.genotype.shape) * 0.5
    for i in range(individual.shape[0]):
        if rng.uniform(0, 1) < mutate_prob:
            individual[i] = genotype.genotype[i] + rng.uniform(-bound, bound)

    return Genotype(individual, genotype.grid_size)
