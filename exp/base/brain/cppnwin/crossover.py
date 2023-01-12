#!/usr/bin/env python3

"""
Author:     as, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Multineat
import multineat

# Local libraries
from .genotype import Genotype


def crossover(
    parent1: Genotype,
    parent2: Genotype,
    multineat_params: multineat.Parameters,  # type: ignore # STUB
    rng: multineat.RNG,  # type: ignore # STUB
    mate_average: bool,
    interspecies_crossover: bool,
) -> Genotype:
    """Perform crossover between two CPPNWIN genotypes.

    Parameters
    ----------
    parent1 : Genotype
        The first parent. (remains unchanged)
    parent2 : Genotype
        The second parent. (remains unchanged)
    multineat_params : multineat.Parameters
        Multineat parameters. See Multineat library.
    rng : multineat.RNG
        Random number generator.
    mate_average : bool
        Whether to use average mating (connections between the parents are averaged) or not (connections chosen from one of the parents). See NEAT algorithm.
    interspecies_crossover : bool
        Whether to use interspecies crossover. TODO description. Choose `False` if you don't know what this means. See Multineat library algorithm.

    Returns
    -------
    Genotype
        The result of crossover.
    """
    new_genotype = parent1.genotype.MateWithConstraints(
        parent2.genotype,
        mate_average,
        interspecies_crossover,
        rng,
        multineat_params,
    )
    return Genotype(new_genotype)
