#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-09
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
from brain.cppnwin import mutate as brain_mutate

# Local libraries
from .genotype import Genotype
from .helpers import make_multineat_params, multineat_rng_from_random

# Global constants
_MULTINEAT_PARAMS = make_multineat_params()


def mutate(
    genotype: Genotype,
    innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
    innov_db_brain: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: Random,
) -> Genotype:
    """Mutate a genotype."""
    multineat_rng = multineat_rng_from_random(rng=rng)

    body = body_mutate(
        genotype=genotype.body,
        innov_db=innov_db_body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
    )

    brain = brain_mutate(
        genotype=genotype.brain,
        innov_db=innov_db_brain,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
    )

    return Genotype(body=body, brain=brain)
