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


def random(
    innov_db: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: multineat.RNG,  # type: ignore # STUB
    multineat_params: multineat.Parameters,  # type: ignore # STUB
    output_activation_func: multineat.ActivationFunction,  # type: ignore # STUB
    num_inputs: int,
    num_outputs: int,
    num_initial_mutations: int,
) -> Genotype:
    """
    Create a random CPPNWIN genotype.

    A CPPNWIN network starts empty.
    A random network is created by mutating `num_initial_mutations` times.

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
    num_inputs : int
        Number of input nodes for the network.
    num_outputs : int
        Number of output nodes for the network.
    num_initial_mutations : int
        Number of mutations to apply to the network to create a random network.

    Returns
    -------
    Genotype
        The created genotype.
    """
    genotype = multineat.Genome(  # type: ignore # STUB
        0,  # ID
        num_inputs,
        0,  # n_hidden
        num_outputs,
        False,  # FS_NEAT
        output_activation_func,  # output activation type
        multineat.ActivationFunction.TANH,  # hidden activation type # type: ignore # STUB
        0,  # seed_type
        multineat_params,
        0,  # number of hidden layers
    )

    for _ in range(num_initial_mutations):
        genotype = genotype.MutateWithConstraints(
            False,
            multineat.SearchMode.BLENDED,  # type: ignore # STUB
            innov_db,
            multineat_params,
            rng,
        )

    return Genotype(genotype)
