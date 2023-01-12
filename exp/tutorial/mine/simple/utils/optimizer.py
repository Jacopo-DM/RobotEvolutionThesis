#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""


# Standard libraries
import pickle
from random import Random
from typing import List, Tuple

# Third-party libraries
import revolve2.core.optimization.ea.generic_ea.population_management as population_management
from revolve2.core.database import IncompatibleError
from revolve2.core.database.serializers._float_serializer import FloatSerializer
from revolve2.core.optimization import DbId
from revolve2.core.optimization.ea.generic_ea import EAOptimizer
from sqlalchemy import Column, Integer, PickleType, String
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

# Local libraries
try:
    from .genotype import Genotype, GenotypeSerializer
    from .item import Item
    from .phenotype import Phenotype
except ImportError:
    from genotype import (  # type: ignore # FIXME stubs and multiple imports
        Genotype,
        GenotypeSerializer,
    )
    from item import Item  # type: ignore # FIXME stubs and multiple imports
    from phenotype import Phenotype  # type: ignore # FIXME stubs and multiple imports

# Global variables
FITNESS_TYPE = float
FITNESS_SERIAL = FloatSerializer
MUTATION_RATE = 0.05
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


class Optimizer(EAOptimizer[Genotype, FITNESS_TYPE]):
    """Optimizer for the knapsack problem."""

    _db_id: DbId
    _rng: Random
    _items: List[Item]
    _max_weight: float
    _num_generations: int

    async def ainit_new(  # type: ignore # FIXME
        self,
        database: AsyncEngine,
        session: AsyncSession,
        db_id: DbId,
        offspring_size: int,
        initial_population: List[Genotype],
        rng: Random,
        items: List[Item],
        max_weight: float,
        num_generations: int,
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
        self._items = items
        self._max_weight = max_weight
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
        )

        session.add(opt_state)

    async def ainit_from_database(  # type: ignore # FIXME
        self,
        database: AsyncEngine,
        session: AsyncSession,
        db_id: DbId,
        rng: Random,
        items: List[Item],
        max_weight: float,
        num_generations: int,
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
        self._rng = rng
        self._items = items
        self._max_weight = max_weight
        self._num_generations = num_generations

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

        # success
        return True

    async def _evaluate_generation(
        self, genotypes: List[Genotype], database: AsyncEngine, db_id: DbId
    ) -> List[FITNESS_TYPE]:
        """Evaluate the fitness of the given genotypes."""

        # Get the phenotypes for the genotypes
        phenotypes = [
            Phenotype(
                genotype=genotype,
                items=self._items,
                max_weight=self._max_weight,
                rng=self._rng,
            )
            for genotype in genotypes
        ]

        # Evaluate the phenotypes
        fitnesses = [float(phenotype.get_total_value()) for phenotype in phenotypes]
        return fitnesses

    def _must_do_next_gen(self) -> bool:
        """Check if the next generation must be done."""
        return (
            self.generation_index != self._num_generations
        )  # hoping equality is not a problem, ideally should be <

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

    def _crossover(self, parents: List[Genotype]) -> Genotype:
        """Perform uniform crossover on the given parents."""

        # check number of parents
        assert len(parents) == 2

        # get parents
        p1 = parents[0]
        p2 = parents[1]

        # create a new genotype (uniform crossover)
        return Genotype(
            [self._rng.choice([p1.items[i], p2.items[i]]) for i in range(len(p1.items))]
        )

    def _mutate(self, genotype: Genotype) -> Genotype:
        """Mutate the given genotype."""

        # Randomly inverse the value of a gene
        return Genotype(
            [
                self._rng.choice([item, not item])
                if self._rng.random() < MUTATION_RATE
                else item
                for item in genotype.items
            ]
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
