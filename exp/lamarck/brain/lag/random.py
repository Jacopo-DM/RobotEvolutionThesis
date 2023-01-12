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


def random(
    grid_size: int,
    rng: Random,
) -> Genotype:
    """
    Create a random LAG genotype.

    Parameters
    ----------
    grid_size : int
        The length of (one side of) the genotype (grid).
    rng : Random
        Random number generator. TODO rng is currently not numpy, but this would be very convenient
    """
    # HACK this ensures (at least) that the np_rng is bounded to the rng
    np.random.seed(rng.randint(0, 2**32))

    # Generate a random genotype
    nprng = np.random.Generator(np.random.PCG64(rng.randint(0, 2**63)))
    params = nprng.standard_normal(grid_size**2)
    return Genotype(params, grid_size=grid_size)
