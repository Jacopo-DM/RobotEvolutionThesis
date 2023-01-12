#!/usr/bin/env python3

"""
Author:     as, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Future libraries
import multineat

# Local libraries
from .genotype import Genotype


def mutate(
    genotype: Genotype,
    multineat_params: multineat.Parameters,  # type: ignore # STUB
    innov_db: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: multineat.RNG,  # type: ignore # STUB
) -> Genotype:
    """
    Mutate a CPPNWIN genotype.

    Parameters
    ----------
    genotype : Genotype
        The genotype to mutate. (remains unchanged)
    multineat_params : multineat.Parameters
        Multineat parameters. See Multineat library.
    innov_db : multineat.InnovationDatabase
        Multineat innovation database. See Multineat library.
    rng : multineat.RNG
        Random number generator.

    Returns
    -------
    Genotype
        The result of mutation. (mutated copy)
    """
    new_genotype = genotype.genotype.MutateWithConstraints(
        False,
        multineat.SearchMode.BLENDED,  # type: ignore # STUB
        innov_db,
        multineat_params,
        rng,
    )
    return Genotype(new_genotype)
