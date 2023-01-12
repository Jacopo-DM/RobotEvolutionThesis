#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-09
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
import math
from random import Random

# Third-party libraries
from pyrr import Quaternion, Vector3  # type: ignore # STUB no stubs
from revolve2.actor_controller import ActorController
from revolve2.core.modular_robot import ActiveHinge, Body, Brick, ModularRobot
from revolve2.core.modular_robot.brains import BrainCpgNetworkNeighbourRandom
from revolve2.core.physics.running import (
    ActorControl,
    Batch,
    Environment,
    EnvironmentController,
    PosedActor,
)
from revolve2.runners.mujoco import LocalRunner

# Local libraries


def create_body() -> Body:
    """Create a robot body"""

    # Create a body
    body = Body()

    # Attach active hinge to the body (left)
    body.core.left = ActiveHinge(rotation=math.pi / 2.0)
    body.core.left.attachment = ActiveHinge(rotation=math.pi / 2.0)  # type: ignore # STUB improper parsing of revolve2.core.modular_robot.ActiveHinge
    body.core.left.attachment.attachment = Brick(rotation=0.0)  # type: ignore # STUB improper parsing of revolve2.core.modular_robot.Brick

    # Attach active hinge to the body (right)
    body.core.right = ActiveHinge(rotation=math.pi / 2.0)
    body.core.right.attachment = ActiveHinge(rotation=math.pi / 2.0)  # type: ignore # STUB improper parsing of revolve2.core.modular_robot.ActiveHinge
    body.core.right.attachment.attachment = Brick(rotation=0.0)  # type: ignore # STUB improper parsing of revolve2.core.modular_robot.Brick

    # Return the body
    body.finalize()
    return body


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


class Simulator:
    async def simulate(self, robot: ModularRobot, control_frequency: float) -> None:
        """Connection to the physics engine simulator."""

        # Batch parameters
        batch = Batch(
            simulation_time=1000000,
            sampling_frequency=0.0001,
            control_frequency=control_frequency,
        )

        # Initialize the robot
        actor, controller = robot.make_actor_and_controller()
        bounding_box = actor.calc_aabb()

        # Initialize the environment
        env = Environment(EnvironmentActorController(controller))
        env.actors.append(
            PosedActor(
                actor=actor,
                position=Vector3(
                    [
                        0.0,
                        0.0,
                        bounding_box.size.z / 2.0 - bounding_box.offset.z,
                    ]
                ),
                orientation=Quaternion(),
                dof_states=[0.0 for _ in controller.get_dof_targets()],
            )
        )
        batch.environments.append(env)

        # Run the simulation
        runner = LocalRunner()
        await runner.run_batch(batch)


async def main() -> None:

    # Create a Random object
    rng = Random()

    # Set seed to 42
    rng.seed(42)

    # Create a body
    body = create_body()

    # Create brain
    brain = BrainCpgNetworkNeighbourRandom(rng)

    # Create a robot
    robot = ModularRobot(body, brain)

    # Create a simulator
    sim = Simulator()
    await sim.simulate(robot=robot, control_frequency=60)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
