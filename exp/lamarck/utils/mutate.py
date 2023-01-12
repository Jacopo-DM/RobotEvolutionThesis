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

# Multineat
import multineat

# Genotypes
from body.cppnwin import mutate as body_mutate
from brain.lag import mutate as brain_mutate

# Local libraries
from .genotype import Genotype
from .helpers import make_multineat_params, multineat_rng_from_random

# Global constants
_MULTINEAT_PARAMS = make_multineat_params()


def mutate(
    genotype: Genotype,
    innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: Random,
) -> Genotype:
    """Mutate a genotype.

    Parameters
    ----------
    genotype : Genotype
        Genotype to mutate.
    innov_db_body : multineat.InnovationDatabase
        Innovation database for the body.
    rng : Random
        Random number generator.


    """
    multineat_rng = multineat_rng_from_random(rng=rng)

    body = body_mutate(
        genotype=genotype.body,
        innov_db=innov_db_body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
    )

    brain = brain_mutate(genotype=genotype.brain, rng=rng, bound=1, mutate_prob=0.8)

    return Genotype(body=body, brain=brain)
