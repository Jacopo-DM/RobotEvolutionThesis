#!/usr/bin/env python3

"""
Author:     as, jl, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""


# Standard libraries
import logging
import math
import pickle
from copy import deepcopy
from random import Random
from typing import List, Tuple

# MultiNEAT
import multineat

# Third-party libraries
from pyrr import Quaternion, Vector3

# Revolve2
from revolve2.actor_controller import ActorController
from revolve2.actor_controllers.cpg import Cpg, CpgNetworkStructure
from revolve2.core.database import IncompatibleError
from revolve2.core.database.serializers import Ndarray1xnSerializer
from revolve2.core.database.serializers._float_serializer import FloatSerializer
from revolve2.core.optimization import DbId
from revolve2.core.optimization.ea.generic_ea import EAOptimizer
from revolve2.core.optimization.ea.openai_es import DbOpenaiESOptimizerIndividual
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
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

# Genotypes
from brain.lag import Genotype as BrainGenotype

# Local libraries
from .crossover import crossover
from .genotype import Genotype, GenotypeSerializer
from .helpers import (
    EnvironmentActorController,
    develop,
    select_parents_tournament,
    select_survivors_tournament,
)
from .learning.openai_es.optimizer import Optimizer as OpenaiESOptimizer
from .mutate import mutate
from .optimizer_schema import DbFitness, DbOptimizerState

# Global variables
FITNESS_TYPE = float
FITNESS_SERIAL = FloatSerializer


class Optimizer(EAOptimizer[Genotype, FITNESS_TYPE]):
    """Optimizer for the knapsack problem."""

    _db_id: DbId
    _rng: Random
    _num_generations: int

    # CPPN
    _runner: Runner
    _controllers: List[ActorController]

    _innov_db_body: multineat.InnovationDatabase  # type: ignore # STUB
    _simulation_time: int
    _sampling_frequency: float
    _control_frequency: float

    async def ainit_new(
        self,
        database: AsyncEngine,
        session: AsyncSession,
        db_id: DbId,
        offspring_size: int,
        initial_population: List[Genotype],
        rng: Random,
        num_generations: int,
        innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
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
        self._init_runner()
        self._innov_db_body = innov_db_body
        self._simulation_time = simulation_time
        self._sampling_frequency = sampling_frequency
        self._control_frequency = control_frequency
        self._num_generations = num_generations

        # create database structure if it doesn't exist
        await (await session.connection()).run_sync(
            DbOptimizerState.metadata.create_all  # HACK used to be DbBase
        )

        # save items to database
        self._on_generation_checkpoint(session)

    def _on_generation_checkpoint(self, session: AsyncSession) -> None:
        """Save the optimizer state to the database."""

        # save optimizer state
        opt_state = DbOptimizerState(
            db_id=self._db_id.fullname,
            generation_index=self.generation_index,
            rng=pickle.dumps(self._rng.getstate()),
            innov_db_body=self._innov_db_body.Serialize(),
            simulation_time=self._simulation_time,
            sampling_frequency=self._sampling_frequency,
            control_frequency=self._control_frequency,
            num_generations=self._num_generations,
        )

        # add to session
        session.add(opt_state)

    def _init_runner(self) -> None:
        """Initialize the runner."""
        self._runner = LocalRunner(headless=True)

    async def ainit_from_database(
        self,
        database: AsyncEngine,
        session: AsyncSession,
        db_id: DbId,
        rng: Random,
        innov_db_body: multineat.InnovationDatabase,  # type: ignore # STUB
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

        # success
        return True

    def _must_do_next_gen(self) -> bool:
        """Check if the next generation must be done."""
        return (
            self.generation_index != self._num_generations
        )  # HACK hoping equality is not a problem, ideally should be <

    def _select_parents(
        self,
        population: List[Genotype],  # NOTE: not used
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
        old_individuals: List[Genotype],  # NOTE: not used
        old_fitnesses: List[FITNESS_TYPE],
        new_individuals: List[Genotype],  # NOTE: not used
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
        return crossover(parents[0], parents[1], self._rng)

    def _mutate(self, genotype: Genotype) -> Genotype:
        """Mutate the given genotype."""
        return mutate(genotype, self._innov_db_body, self._rng)

    async def _evaluate_generation(
        self,
        genotypes: List[Genotype],
        database: AsyncEngine,
        db_id: DbId,
    ) -> List[FITNESS_TYPE]:
        """Evaluate the fitness of the given genotypes."""

        # Evaluate the fitness of the genotypes before learning
        fitnesses_before = await self._evaluate_robots(genotypes)

        # ==================== START LEARNING PERIOD ====================

        # Perform the learning period
        logging.info(
            f"--- Start Learning Period Gen \033[92m{self.generation_index}\033[0m ---"
        )

        # rewrite smaller case
        population_size = 20
        num_generations = 10

        simulation_time = 15
        sampling_frequency = 5
        control_frequency = 60

        sigma = 0.1
        learning_rate = 0.05

        # log the learning parameters in green
        logging.info(f"Population size: \033[92m{population_size}\033[0m")
        logging.info(f"Sigma: \033[92m{sigma}\033[0m")
        logging.info(f"Learning rate: \033[92m{learning_rate}\033[0m")
        logging.info(f"Number of generations: \033[92m{num_generations}\033[0m")
        logging.info(f"Simulation time: \033[92m{simulation_time}\033[0m")
        logging.info(f"Sampling frequency: \033[92m{sampling_frequency}\033[0m")
        logging.info(f"Control frequency: \033[92m{control_frequency}\033[0m")

        for idx, __ in enumerate(genotypes):
            new_brain = await self._learning_period(
                genotypes[idx],
                database=database,
                population_size=population_size,
                sigma=sigma,
                learning_rate=learning_rate,
                num_generations=num_generations,
                simulation_time=simulation_time,
                sampling_frequency=sampling_frequency,
                control_frequency=control_frequency,
            )
            genotypes[idx].brain = new_brain

        # ==================== END LEARNING PERIOD  ====================

        # Evaluate the fitness of the genotypes after learning
        fitnesses_after = await self._evaluate_robots(genotypes)

        # Learning delta
        learning_delta = [
            fitness_after - fitness_before
            for fitness_before, fitness_after in zip(fitnesses_before, fitnesses_after)
        ]

        # Commit the fitness_before, fitness_after and learning_delta to the database
        db_objects = [
            DbFitness(
                db_id=db_id.fullname,
                generation_index=self.generation_index,
                learner_index=learner_index,
                fitness_before=fitness_before,
                fitness_after=fitness_after,
                learning_delta=learning_delta,
            )
            for learner_index, (
                fitness_before,
                fitness_after,
                learning_delta,
            ) in enumerate(zip(fitnesses_before, fitnesses_after, learning_delta))
        ]

        async with AsyncSession(database) as session:
            async with session.begin():
                session.add_all(db_objects)
                await session.flush()

        # return fitnesses
        return learning_delta

    async def _learning_period(
        self,
        genotype: Genotype,
        database: AsyncEngine,
        population_size: int,
        sigma: float,
        learning_rate: float,
        num_generations: int,
        simulation_time: float,
        sampling_frequency: float,
        control_frequency: float,
    ) -> BrainGenotype:
        """Perform the learning period.

        Parameters
        ----------
        genotype : Genotype
            The genotype to be learned.
        database : AsyncEngine
            The database to use.
        population_size : int
            The population size.
        sigma : float
            The sigma.
        learning_rate : float
            The learning rate.
        num_generations : int
            The number of generations.
        simulation_time : float
            The simulation time.
        sampling_frequency : int
            The sampling frequency.
        control_frequency : int
            The control frequency.

        Returns
        -------
        BrainGenotype
            The learned brain genotype.
        """

        # unique database identifier for optimizer
        db_id = DbId.root("openaies")

        robot = develop(genotype)
        body = robot.body
        grid_size = genotype.brain.grid_size

        hinges = body.find_active_hinges()
        cpgs = [Cpg(i) for i, _ in enumerate(hinges)]
        brain = CpgNetworkStructure(cpgs, set())

        params = []
        for hinge in hinges:
            pos = body.grid_position(hinge)
            params.append(
                genotype.brain.genotype[
                    int(pos[0] + pos[1] * grid_size + grid_size**2 / 2)
                ]
            )

        maybe_optimizer = await OpenaiESOptimizer.from_database(
            database=database,
            db_id=db_id,
            rng=self._rng,
            robot_body=body,
            simulation_time=simulation_time,
            sampling_frequency=sampling_frequency,
            control_frequency=control_frequency,
            num_generations=num_generations,
            cpg_structure=brain,
        )
        if maybe_optimizer is not None:
            optimizer = maybe_optimizer
        else:
            optimizer = await OpenaiESOptimizer.new(
                database=database,
                db_id=db_id,
                rng=self._rng,
                population_size=population_size,
                sigma=sigma,
                learning_rate=learning_rate,
                robot_body=body,
                simulation_time=simulation_time,
                sampling_frequency=sampling_frequency,
                control_frequency=control_frequency,
                num_generations=num_generations,
                cpg_structure=brain,
                initial_mean=params,
            )

        await optimizer.run()

        async with AsyncSession(database) as session:
            best_individual = (
                (
                    await session.execute(
                        select(DbOpenaiESOptimizerIndividual).order_by(
                            DbOpenaiESOptimizerIndividual.fitness.desc()
                        )
                    )
                )
                .scalars()
                .all()[0]
            )
            params = [
                p
                for p in (
                    await Ndarray1xnSerializer.from_database(
                        session, [best_individual.individual]
                    )
                )[0]
            ]

        improved_brain = deepcopy(genotype.brain)
        improved_brain_genotype = deepcopy(genotype.brain.genotype)

        for hinge, learned_weight in zip(hinges, params):
            pos = body.grid_position(hinge)
            improved_brain_genotype[
                int(pos[0] + pos[1] * grid_size + grid_size**2 / 2)
            ] = learned_weight

        improved_brain.genotype = improved_brain_genotype
        return improved_brain

    async def _evaluate_robots(
        self,
        genotypes: List[Genotype],
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
        """Control the robot.

        Parameters
        ----------
        environment_index : int
            The index of the environment.
        dt : float
            The time step.
        control : ActorControl
            The control object.
        """

        # Control the robot
        controller = self._controllers[environment_index]
        controller.step(dt)
        control.set_dof_targets(actor=0, targets=controller.get_dof_targets())

    @staticmethod
    def _calculate_fitness(begin_state: ActorState, end_state: ActorState) -> float:
        """Calculate the fitness of the robot.

        Distance traveled.

        Parameters
        ----------
        begin_state : ActorState
            The state of the robot at the beginning of the simulation.
        end_state : ActorState
            The state of the robot at the end of the simulation.

        Returns
        -------
        float
            The fitness of the robot.
        """
        return float(
            math.sqrt(
                (end_state.position.x - begin_state.position.x) ** 2
                + (end_state.position.y - begin_state.position.y) ** 2
            )
        )
