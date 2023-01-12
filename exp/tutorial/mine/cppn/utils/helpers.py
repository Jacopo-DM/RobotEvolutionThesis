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
from typing import List, Tuple

# MultiNEAT
import multineat  # type: ignore # STUB
from revolve2.actor_controller import ActorController

# Revolve2
from revolve2.core.modular_robot import ModularRobot
from revolve2.core.physics.running import ActorControl, EnvironmentController
from revolve2.genotypes.cppnwin import crossover_v1, mutate_v1
from revolve2.genotypes.cppnwin.modular_robot.body_genotype_v1 import (
    develop_v1 as body_develop,
)
from revolve2.genotypes.cppnwin.modular_robot.body_genotype_v1 import (
    random_v1 as body_random,
)
from revolve2.genotypes.cppnwin.modular_robot.brain_genotype_cpg_v1 import (
    develop_v1 as brain_develop,
)
from revolve2.genotypes.cppnwin.modular_robot.brain_genotype_cpg_v1 import (
    random_v1 as brain_random,
)

# Local libraries
try:
    from .genotype import Genotype
except ImportError:
    from genotype import Genotype  # type: ignore # STUB and multiple imports

# Global variables
FITNESS_TYPE = float


class EnvironmentActorController(EnvironmentController):

    actor_controller: ActorController

    def __init__(self, actor_controller: ActorController) -> None:
        """
        Initialize this object.

        Parameters
        ----------
        actor_controller : ActorController
            The actor controller to use for the single actor in the environment.
        """
        self.actor_controller = actor_controller

    def control(self, dt: float, actor_control: ActorControl) -> None:
        """
        Control the single actor in the environment using an ActorController.

        Parameters
        ----------
        dt : float
            Time since last call to this function.
        actor_control : ActorControl
            Object used to interface with the environment.
        """
        self.actor_controller.step(dt)
        actor_control.set_dof_targets(
            actor=0, targets=self.actor_controller.get_dof_targets()
        )


def _multineat_rng_from_random(rng: Random) -> multineat.RNG:  # type: ignore # STUB
    multineat_rng = multineat.RNG()  # type: ignore # STUB
    multineat_rng.Seed(rng.randint(a=0, b=2**31))
    return multineat_rng


def _make_multineat_params() -> multineat.Parameters:  # type: ignore # STUB
    # Create an instance of the multineat parameters object
    multineat_params = multineat.Parameters()  # type: ignore # STUB

    # Set probability of removing a link to 2%
    multineat_params.MutateRemLinkProb = 0.02
    # Set probability of creating a recurrent link to 0%
    multineat_params.RecurrentProb = 0.0
    # Set overall mutation rate to 15%
    multineat_params.OverallMutationRate = 0.15
    # Set probability of adding a link to 8%
    multineat_params.MutateAddLinkProb = 0.08
    # Set probability of adding a neuron to 1%
    multineat_params.MutateAddNeuronProb = 0.01
    # Set probability of mutating weights to 90%
    multineat_params.MutateWeightsProb = 0.90
    # Set maximum weight value to 8.0
    multineat_params.MaxWeight = 8.0
    # Set maximum power for weight mutations to 0.2
    multineat_params.WeightMutationMaxPower = 0.2
    # Set maximum power for weight replacement to 1.0
    multineat_params.WeightReplacementMaxPower = 1.0
    # Set probability of mutating activation parameter A to 0%
    multineat_params.MutateActivationAProb = 0.0
    # Set maximum power for activation A mutations to 0.5
    multineat_params.ActivationAMutationMaxPower = 0.5
    # Set minimum activation A value to 0.05
    multineat_params.MinActivationA = 0.05
    # Set maximum activation A value to 6.0
    multineat_params.MaxActivationA = 6.0
    # Set probability of mutating neuron activation type to 3%
    multineat_params.MutateNeuronActivationTypeProb = 0.03
    # Set probability of mutating output activation function to False (i.e., do not mutate output activation function)
    multineat_params.MutateOutputActivationFunction = False
    # Set probability of using signed sigmoid activation function to 0%
    multineat_params.ActivationFunction_SignedSigmoid_Prob = 0.0
    # Set probability of using unsigned sigmoid activation function to 0%
    multineat_params.ActivationFunction_UnsignedSigmoid_Prob = 0.0
    # Set probability of using tanh activation function to 1%
    multineat_params.ActivationFunction_Tanh_Prob = 1.0
    # Set probability of using tanh cubic activation function to 0%
    multineat_params.ActivationFunction_TanhCubic_Prob = 0.0
    # Set probability of using signed step activation function to 1%
    multineat_params.ActivationFunction_SignedStep_Prob = 1.0
    # Set probability of using unsigned step activation function to 0%
    multineat_params.ActivationFunction_UnsignedStep_Prob = 0.0
    # Set probability of using signed Gaussian activation function to 1%
    multineat_params.ActivationFunction_SignedGauss_Prob = 1.0
    # Set probability of using unsigned Gaussian activation function to 0%
    multineat_params.ActivationFunction_UnsignedGauss_Prob = 0.0
    # Set probability of using abs activation function to 0%
    multineat_params.ActivationFunction_Abs_Prob = 0.0
    # Set probability of using signed sine activation function to 1%
    multineat_params.ActivationFunction_SignedSine_Prob = 1.0
    # Set probability of using unsigned sine activation function to 0%
    multineat_params.ActivationFunction_UnsignedSine_Prob = 0.0
    # Set probability of using linear activation function to 1%
    multineat_params.ActivationFunction_Linear_Prob = 1.0
    # Set probability of mutating neuron traits to 0%
    multineat_params.MutateNeuronTraitsProb = 0.0
    # Set probability of mutating link traits to 0%
    multineat_params.MutateLinkTraitsProb = 0.0
    # Set flag for allowing loops to False
    multineat_params.AllowLoops = False

    return multineat_params


_MULTINEAT_PARAMS = _make_multineat_params()


def random_genotype(
    innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
    innov_db_brain: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: Random,
    num_initial_mutations: int,
) -> Genotype:
    """Generate a random genotype, by generating a random string of booleans."""
    multineat_rng = _multineat_rng_from_random(rng=rng)

    body = body_random(
        innov_db=innov_db_body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
        output_activation_func=multineat.ActivationFunction.TANH,  # type: ignore # STUB
        num_initial_mutations=num_initial_mutations,
    )

    brain = brain_random(
        innov_db=innov_db_brain,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
        output_activation_func=multineat.ActivationFunction.SIGNED_SINE,  # type: ignore # STUB
        num_initial_mutations=num_initial_mutations,
    )

    return Genotype(body=body, brain=brain)


def mutate(
    genotype: Genotype,
    innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
    innov_db_brain: multineat.InnovationDatabase,  # type: ignore # STUB
    rng: Random,
) -> Genotype:
    """Mutate a genotype."""
    multineat_rng = _multineat_rng_from_random(rng=rng)

    body = mutate_v1(
        genotype=genotype.body,
        innov_db=innov_db_body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
    )

    brain = mutate_v1(
        genotype=genotype.brain,
        innov_db=innov_db_brain,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
    )

    return Genotype(body=body, brain=brain)


def crossover(parent1: Genotype, parent2: Genotype, rng: Random) -> Genotype:
    """Crossover two genotypes."""
    multineat_rng = _multineat_rng_from_random(rng=rng)

    body = crossover_v1(
        parent1=parent1.body,
        parent2=parent2.body,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
        mate_average=False,
        interspecies_crossover=False,
    )

    brain = crossover_v1(
        parent1=parent1.brain,
        parent2=parent2.brain,
        rng=multineat_rng,
        multineat_params=_MULTINEAT_PARAMS,
        mate_average=False,
        interspecies_crossover=False,
    )

    return Genotype(body=body, brain=brain)


def develop(genotype: Genotype) -> ModularRobot:
    """Develop a genotype into a phenotype."""
    body = body_develop(genotype=genotype.body)
    brain = brain_develop(genotype=genotype.brain, body=body)
    return ModularRobot(body=body, brain=brain)


def select_survivors_tournament(
    rng: Random,
    old_fitnesses: List[FITNESS_TYPE],
    new_fitnesses: List[FITNESS_TYPE],
    num_survivors: int,
    tournament_size: int,
) -> Tuple[List[int], List[int]]:
    """Select survivors for the next generation.

    Parameters
    ----------
    rng : Random
        Random number generator.
    old_fitnesses : List[FITNESS_TYPE]
        The fitnesses of the old individuals.
    new_fitnesses : List[FITNESS_TYPE]
        The fitnesses of the new individuals.
    num_survivors : int
        The number of survivors.
    tournament_size : int
        The size of the tournament.

    Returns
    -------
    Tuple[List[int], List[int]]
        The indices of the old and new individuals that are selected as survivors.
    """

    # Merge fitnesses
    fitnesses = old_fitnesses + new_fitnesses

    # Sort the fitnesses
    fit_sorted = sorted(enumerate(fitnesses), key=lambda x: x[1], reverse=True)
    fit_generator = [i for i in range(len(fit_sorted))]

    # Select survivors
    survivors = []
    for __ in range(num_survivors):
        idx = min(rng.choices(fit_generator, k=tournament_size))
        survivors.extend([fit_sorted[idx][0]])
        fit_generator.remove(idx)

    # Retrive matching indices
    len_old = len(old_fitnesses)
    old_indices = [i for i in survivors if i < len_old]
    new_indices = [i - len_old for i in survivors if i >= len_old]

    # Return the parents
    return (old_indices, new_indices)


def select_parents_tournament(
    rng: Random,
    fitnesses: List[FITNESS_TYPE],
    num_parent_groups: int,
    num_of_parents: int,
    tournament_size: int,
) -> List[List[int]]:
    """Select parents for the next generation.

    Parameters
    ----------
    rng : Random
        Random number generator.
    fitnesses : List[FITNESS_TYPE]
        The fitnesses of the population.
    num_parent_groups : int
        The number of parent groups to select.
    num_of_parents : int
        The number of parents in each group.
    tournament_size : int
        The size of the tournament.

    Returns
    -------
    List[List[int]]
        The indices of the selected parents.
    """

    # Sort the fitnesses
    fit_sorted = sorted(enumerate(fitnesses), key=lambda x: x[1], reverse=True)
    fit_generator = range(len(fit_sorted))

    # Select parents
    parents = []
    for __ in range(num_parent_groups):
        idx = sorted(rng.sample(fit_generator, tournament_size))
        _parents = [fit_sorted[i][0] for i in idx[:num_of_parents]]
        parents.append(_parents)

    # Return the parents
    return parents
