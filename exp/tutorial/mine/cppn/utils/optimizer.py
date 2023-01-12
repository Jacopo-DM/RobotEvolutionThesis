#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""


# Standard libraries
import math
import pickle
from random import Random
from typing import List, Tuple

# MultiNEAT
import multineat  # type: ignore # STUB

# Third-party libraries
from pyrr import Quaternion, Vector3  # type: ignore # STUB

# Revolve2
from revolve2.actor_controller import ActorController
from revolve2.core.database import IncompatibleError
from revolve2.core.database.serializers._float_serializer import FloatSerializer
from revolve2.core.optimization import DbId
from revolve2.core.optimization.ea.generic_ea import EAOptimizer
from revolve2.core.physics.running import (
    ActorControl,
    ActorState,
    Batch,
    Environment,
    PosedActor,
    Runner,
)
from revolve2.runners.mujoco import LocalRunner

# SQLAlchemy
from sqlalchemy import Column, Float, Integer, PickleType, String
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

# Local libraries
try:
    from .genotype import Genotype  # type: ignore # STUB and multiple imports
    from .genotype import GenotypeSerializer  # type: ignore # STUB and multiple imports
    from .helpers import (  # type: ignore # STUB and multiple imports
        EnvironmentActorController,
        crossover,
        develop,
        mutate,
        select_parents_tournament,
        select_survivors_tournament,
    )
except ImportError:
    from genotype import Genotype  # type: ignore # STUB and multiple imports
    from genotype import GenotypeSerializer  # type: ignore # STUB and multiple imports
    from helpers import (  # type: ignore # STUB and multiple imports
        EnvironmentActorController,
        crossover,
        develop,
        mutate,
        select_parents_tournament,
        select_survivors_tournament,
    )

# Global variables
FITNESS_TYPE = float
FITNESS_SERIAL = FloatSerializer
DbBase = declarative_base()


class DbOptimizerState(DbBase):
    """Database representation of the optimizer state."""

    __tablename__ = "optimizer_state"

    db_id = Column(
        String,
        nullable=False,
        primary_key=True,
    )
    generation_index = Column(Integer, nullable=False, primary_key=True)
    rng = Column(PickleType, nullable=False)
    num_generations = Column(Integer, nullable=False)

    # CPPN
    innov_db_body = Column(String, nullable=False)
    innov_db_brain = Column(String, nullable=False)
    simulation_time = Column(Integer, nullable=False)
    sampling_frequency = Column(Float, nullable=False)
    control_frequency = Column(Float, nullable=False)


class Optimizer(EAOptimizer[Genotype, FITNESS_TYPE]):
    """Optimizer for the knapsack problem."""

    _db_id: DbId
    _rng: Random
    _num_generations: int

    # CPPN
    _runner: Runner
    _controllers: List[ActorController]

    _innov_db_body: multineat.InnovationDatabase  # type: ignore # STUB
    _innov_db_brain: multineat.InnovationDatabase  # type: ignore # STUB
    _simulation_time: int
    _sampling_frequency: float
    _control_frequency: float

    async def ainit_new(  # type: ignore # STUB
        self,
        database: AsyncEngine,
        session: AsyncSession,
        db_id: DbId,
        offspring_size: int,
        initial_population: List[Genotype],
        rng: Random,
        num_generations: int,
        innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
        innov_db_brain: multineat.InnovationDatabase,  # type: ignore # STUB
        simulation_time: int,
        sampling_frequency: float,
        control_frequency: float,
    ) -> None:
        """Initialize the optimizer."""

        await super().ainit_new(
            database=database,
            session=session,
            db_id=db_id,
            genotype_type=Genotype,
            genotype_serializer=GenotypeSerializer,
            fitness_type=FITNESS_TYPE,
            fitness_serializer=FITNESS_SERIAL,
            offspring_size=offspring_size,
            initial_population=initial_population,
        )

        self._db_id = db_id
        self._rng = rng
        self._num_generations = num_generations

        # CPPN
        self._innov_db_body = innov_db_body
        self._innov_db_brain = innov_db_brain
        self._simulation_time = simulation_time
        self._sampling_frequency = sampling_frequency
        self._control_frequency = control_frequency
        self._num_generations = num_generations

        # create database structure if it doesn't exist
        await (await session.connection()).run_sync(DbBase.metadata.create_all)

        # save items to database
        self._on_generation_checkpoint(session)

    def _on_generation_checkpoint(self, session: AsyncSession) -> None:
        """Save the optimizer state to the database."""

        opt_state = DbOptimizerState(
            db_id=self._db_id.fullname,
            generation_index=self.generation_index,  # type: ignore # FIXME expected int got optional
            rng=pickle.dumps(self._rng.getstate()),
            innov_db_body=self._innov_db_body.Serialize(),
            innov_db_brain=self._innov_db_brain.Serialize(),
            simulation_time=self._simulation_time,
            sampling_frequency=self._sampling_frequency,
            control_frequency=self._control_frequency,
            num_generations=self._num_generations,
        )

        session.add(opt_state)

    def _init_runner(self) -> None:
        self._runner = LocalRunner(headless=True)

    async def ainit_from_database(  # type: ignore # STUB
        self,
        database: AsyncEngine,
        session: AsyncSession,
        db_id: DbId,
        rng: Random,
        innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
        innov_db_brain: multineat.InnovationDatabase,  # type: ignore # STUB
    ) -> bool:
        """Initialize the optimizer from the database."""

        # load optimizer state from database
        if not await super().ainit_from_database(
            database=database,
            session=session,
            db_id=db_id,
            genotype_type=Genotype,
            genotype_serializer=GenotypeSerializer,
            fitness_type=FITNESS_TYPE,
            fitness_serializer=FITNESS_SERIAL,
        ):
            # fail
            return False

        # save parameters
        self._db_id = db_id
        self._init_runner()

        # retrive row from database
        opt_row = (
            (
                await session.execute(
                    select(DbOptimizerState)
                    .filter(DbOptimizerState.db_id == db_id.fullname)
                    .order_by(DbOptimizerState.generation_index.desc())
                )
            )
            .scalars()
            .first()
        )

        # check if optimizer state was found
        if opt_row is None:
            print("Optimizer state not found in database")
            raise IncompatibleError

        # load random number generator state
        self._rng = rng
        self._rng.setstate(pickle.loads(opt_row.rng))

        # CPPN
        self._simulation_time = opt_row.simulation_time
        self._sampling_frequency = opt_row.sampling_frequency
        self._control_frequency = opt_row.control_frequency
        self._num_generations = opt_row.num_generations

        self._innov_db_body = innov_db_body
        self._innov_db_body.Deserialize(opt_row.innov_db_body)
        self._innov_db_brain = innov_db_brain
        self._innov_db_brain.Deserialize(opt_row.innov_db_brain)

        # success
        return True

    def _must_do_next_gen(self) -> bool:
        """Check if the next generation must be done."""
        return (
            self.generation_index != self._num_generations
        )  # HACK hoping equality is not a problem, ideally should be <

    def _select_parents(
        self,
        population: List[Genotype],
        fitnesses: List[FITNESS_TYPE],
        num_parent_groups: int,
    ) -> List[List[int]]:
        """Select parents for the next generation."""

        # Select parents using tournament selection
        return select_parents_tournament(
            rng=self._rng,
            fitnesses=fitnesses,
            num_parent_groups=num_parent_groups,
            num_of_parents=2,
            tournament_size=10,
        )

    def _select_survivors(
        self,
        old_individuals: List[Genotype],
        old_fitnesses: List[FITNESS_TYPE],
        new_individuals: List[Genotype],
        new_fitnesses: List[FITNESS_TYPE],
        num_survivors: int,
    ) -> Tuple[List[int], List[int]]:
        """Select survivors for the next generation."""
        # check number of survivors
        assert len(old_individuals) == num_survivors

        # select survivors
        return select_survivors_tournament(
            rng=self._rng,
            old_fitnesses=old_fitnesses,
            new_fitnesses=new_fitnesses,
            num_survivors=num_survivors,
            tournament_size=10,
        )

    def _crossover(self, parents: List[Genotype]) -> Genotype:
        """Perform uniform crossover on the given parents."""
        assert len(parents) == 2
        return crossover(parents[0], parents[1], self._rng)  # type: ignore # FIXME mypy doesn't like this?

    def _mutate(self, genotype: Genotype) -> Genotype:
        """Mutate the given genotype."""
        return mutate(genotype, self._innov_db_body, self._innov_db_brain, self._rng)  # type: ignore # FIXME mypy doesn't like this?

    async def _evaluate_generation(
        self, genotypes: List[Genotype], database: AsyncEngine, db_id: DbId
    ) -> List[FITNESS_TYPE]:
        """Evaluate the fitness of the given genotypes."""

        batch = Batch(
            simulation_time=self._simulation_time,
            sampling_frequency=self._sampling_frequency,
            control_frequency=self._control_frequency,
        )

        self._controllers = []

        for genotype in genotypes:
            # Initialize the robot
            actor, controller = develop(genotype).make_actor_and_controller()
            bounding_box = actor.calc_aabb()
            self._controllers.append(controller)

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
        batch_results = await self._runner.run_batch(batch)

        return [
            self._calculate_fitness(
                env_res.environment_states[0].actor_states[0],
                env_res.environment_states[-1].actor_states[0],
            )
            for env_res in batch_results.environment_results
        ]

    def _control(
        self, environment_index: int, dt: float, control: ActorControl
    ) -> None:
        """Control the robot."""

        controller = self._controllers[environment_index]
        controller.step(dt)
        control.set_dof_targets(actor=0, targets=controller.get_dof_targets())

    @staticmethod
    def _calculate_fitness(begin_state: ActorState, end_state: ActorState) -> float:
        """Calculate the fitness of the robot."""
        return float(
            math.sqrt(
                (end_state.position.x - begin_state.position.x) ** 2
                + (end_state.position.y - begin_state.position.y) ** 2
            )
        )
