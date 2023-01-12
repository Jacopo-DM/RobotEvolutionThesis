#!/usr/bin/env python3

"""
Author:     as, jl. jmdm 
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

Functions for LAG genotypes for a modular robot CPG brain.
"""

# Standard libraries
import math
from random import Random

# Revolve
from revolve2.actor_controllers.cpg import Cpg, CpgNetworkStructure
from revolve2.core.modular_robot import Body, Brain
from revolve2.core.modular_robot.brains import BrainCpgNetworkStatic

# Local libraries
from ..genotype import Genotype
from ..random import random as random_brain_genotype


def random(grid_size: int, rng: Random) -> Genotype:
    """
    Create a random LAG genotype.

    Parameters
    ----------
    grid_size : int
        The length of (one side of) the genotype (grid).
    rng : Random
        Random number generator.
    """

    return random_brain_genotype(grid_size=grid_size, rng=rng)


def develop(genotype: Genotype, body: Body) -> Brain:
    """
    Develop a LAG genotype into a brain.

    Parameters
    ----------
    genotype : Genotype
        The genotype to develop.
    body : Body
        The body to develop the brain for.

    Returns
    -------
    Brain
        The developed robot controller.
    """
    # Find the active hinges
    hinges = body.find_active_hinges()
    cpgs = [Cpg(i) for i, _ in enumerate(hinges)]
    cpg_structure = CpgNetworkStructure(cpgs, set())

    # Extract the parameters from the genotype
    weights = genotype.genotype
    grid_size = genotype.grid_size
    params = []
    for hinge in hinges:
        try:
            pos = body.grid_position(hinge)
            params.append(
                weights[int(pos[0] + pos[1] * grid_size + grid_size**2 / 2)]
            )
        except IndexError as e:
            print(body.grid_position(hinge))
            print(weights)
            raise e
    # Initialize the CPGs
    initial_state = cpg_structure.make_uniform_state(
        value=0.5 * math.pi / 2.0,
    )
    weight_matrix = cpg_structure.make_connection_weights_matrix_from_params(
        params=params,
    )
    dof_ranges = cpg_structure.make_uniform_dof_ranges(1.0)

    return BrainCpgNetworkStatic(
        initial_state=initial_state,
        num_output_neurons=cpg_structure.num_cpgs,
        weight_matrix=weight_matrix,
        dof_ranges=dof_ranges,
    )
