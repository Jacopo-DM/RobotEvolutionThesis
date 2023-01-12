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

# MultiNEAT
import multineat

# Genotypes
from body.cppnwin.modular_robot.body_genotype import random as body_rnd
from brain.lag.modular_robot.brain_genotype_lag import random as brain_rnd

# Local libraries
from .genotype import Genotype
from .helpers import make_multineat_params, multineat_rng_from_random

# Global constants
_MULTINEAT_PARAMS = make_multineat_params()


def random(
    innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: Random,
    num_initial_mutations: int,
    brain_grid_size: int,
) -> Genotype:
    """Generate a random genotype, by generating a random string of booleans.

    Parameters
    ----------
    innov_db_body : multineat.InnovationDatabase
        Innovation database for the body.
    rng : Random
        Random number generator.
    num_initial_mutations : int
        Number of mutations to apply to the genotype.
    brain_grid_size : int
        Length of one side of the robot square grid. Used to determine the size of the brain.
    """
    multineat_rng = multineat_rng_from_random(rng=rng)

    body = body_rnd(
        innov_db=innov_db_body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
        output_activation_func=multineat.ActivationFunction.TANH,  # type: ignore # STUB
        num_initial_mutations=num_initial_mutations,
    )

    brain = brain_rnd(grid_size=brain_grid_size, rng=rng)

    return Genotype(body=body, brain=brain)
