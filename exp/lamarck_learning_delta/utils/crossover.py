#!/usr/bin/env python3

"""
Author:     as, jl, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
from random import Random

# Genotypes
from body.cppnwin import crossover as body_crossover
from brain.lag import crossover as brain_crossover

# Local libraries
from .genotype import Genotype
from .helpers import make_multineat_params, multineat_rng_from_random

# Global constants
_MULTINEAT_PARAMS = make_multineat_params()


def crossover(parent1: Genotype, parent2: Genotype, rng: Random) -> Genotype:
    """Crossover two genotypes.

    Parameters
    ----------
    parent1 : Genotype
        First parent.
    parent2 : Genotype
        Second parent.
    rng : Random
        Random number generator.

    Returns
    -------
    Genotype
        The result of crossover.
    """
    multineat_rng = multineat_rng_from_random(rng=rng)

    body = body_crossover(
        parent1=parent1.body,
        parent2=parent2.body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
        mate_average=False,
        interspecies_crossover=False,
    )

    brain = brain_crossover(
        parent1=parent1.brain, parent2=parent2.brain, rng=rng, crossover_prob=0.5
    )

    return Genotype(body=body, brain=brain)
