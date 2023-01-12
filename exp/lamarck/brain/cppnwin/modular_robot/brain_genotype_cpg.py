#!/usr/bin/env python3

"""
Author:     as, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

Functions for CPPNWIN genotypes for a modular robot CPG brain.
"""

# Multineat
import multineat

# Revolve
from revolve2.core.modular_robot import Body

# Local libraries
from ..genotype import Genotype
from ..random import random as base_random_v1
from .brain_cpg_network_neighbour import BrainCpgNetworkNeighbour


def random(
    innov_db: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: multineat.RNG,  # type: ignore # STUB
    multineat_params: multineat.Parameters,  # type: ignore # STUB
    output_activation_func: multineat.ActivationFunction,  # type: ignore # STUB
    num_initial_mutations: int,
) -> Genotype:
    """
    Create a CPPNWIN genotype for a modular robot CPG brain.

    Parameters
    ----------
    innov_db : multineat.InnovationDatabase
        Multineat innovation database. See Multineat library.
    rng : multineat.RNG
        Random number generator.
    multineat_params : multineat.Parameters
        Multineat parameters. See Multineat library.
    output_activation_func : multineat.ActivationFunction
        Activation function for output layer. See Multineat library.
    num_initial_mutations : int
        Number of mutations to apply to the network to create a random network.

    Returns
    -------
    Genotype
        The created genotype.
    """

    assert multineat_params.MutateOutputActivationFunction == False
    # other activation functions could work too, but this has been tested.
    # if you want another one, make sure it's output is between -1 and 1.
    assert output_activation_func == multineat.ActivationFunction.SIGNED_SINE  # type: ignore # STUB

    return base_random_v1(
        innov_db,
        rng,
        multineat_params,
        output_activation_func,
        7,  # bias(always 1), x1, y1, z1, x2, y2, z2
        1,  # weight
        num_initial_mutations,
    )


def develop(genotype: Genotype, body: Body) -> BrainCpgNetworkNeighbour:
    """
    Develop a CPPNWIN genotype into a `BrainCpgNetworkNeighbourV1` brain.

    It is important that the genotype was created using a compatible function.

    :param genotype: The genotype to create the brain from.
    :param body: # TODO This parameter is not used.
    :returns: The create brain.
    """
    return BrainCpgNetworkNeighbour(genotype.genotype)
