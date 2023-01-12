#!/usr/bin/env python3

"""
Author:     as, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
from typing import List, Tuple, cast

# Multineat
import multineat

# Revolve
from revolve2.core.modular_robot import ActiveHinge, Body
from revolve2.core.modular_robot.brains import (
    BrainCpgNetworkNeighbour as ModularRobotBrainCpgNetworkNeighbour,
)


class BrainCpgNetworkNeighbour(ModularRobotBrainCpgNetworkNeighbour):
    """
    A CPG brain based on `ModularRobotBrainCpgNetworkNeighbour` that creates weights from a CPPNWIN network.

    Weights are determined by querying the CPPN network with inputs:
    (hinge1_posx, hinge1_posy, hinge1_posz, hinge2_posx, hinge2_posy, hinge3_posz)
    If the weight in internal, hinge1 and hinge2 position will be the same.
    """

    _genotype: multineat.Genome  # type: ignore # STUB

    def __init__(self, genotype: multineat.Genome):  # type: ignore # STUB
        """
        Initialize this object.

        :param genotype: A multineat genome used for determining weights.
        """
        self._genotype = genotype

    def _make_weights(
        self,
        active_hinges: List[ActiveHinge],
        connections: List[Tuple[ActiveHinge, ActiveHinge]],
        body: Body,
    ) -> Tuple[List[float], List[float]]:
        brain_net = multineat.NeuralNetwork()  # type: ignore # STUB
        self._genotype.BuildPhenotype(brain_net)

        internal_weights = [
            self._evaluate_network(
                brain_net,
                [
                    1.0,
                    float(pos.x),
                    float(pos.y),
                    float(pos.z),
                    float(pos.x),
                    float(pos.y),
                    float(pos.z),
                ],
            )
            for pos in [
                body.grid_position(active_hinge) for active_hinge in active_hinges
            ]
        ]

        external_weights = [
            self._evaluate_network(
                brain_net,
                [
                    1.0,
                    float(pos1.x),
                    float(pos1.y),
                    float(pos1.z),
                    float(pos2.x),
                    float(pos2.y),
                    float(pos2.z),
                ],
            )
            for (pos1, pos2) in [
                (body.grid_position(active_hinge1), body.grid_position(active_hinge2))
                for (active_hinge1, active_hinge2) in connections
            ]
        ]

        return (internal_weights, external_weights)

    @staticmethod
    def _evaluate_network(
        network: multineat.NeuralNetwork, inputs: List[float]  # type: ignore # STUB
    ) -> float:
        network.Input(inputs)
        network.ActivateAllLayers()
        return cast(float, network.Output()[0])
