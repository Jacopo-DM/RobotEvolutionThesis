#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Standard libraries
from dataclasses import dataclass
from random import Random
from typing import List

# Third-party libraries
from revolve2.core.database import IncompatibleError, Serializer
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

# Local libraries
try:
    from .item import Item
except ImportError:
    from item import Item  # type: ignore # FIXME stubs and multiple imports

DbBase = declarative_base()

import os

os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"  # FIXME depricated API


@dataclass
class Genotype:
    """Genotype for the knapsack problem."""

    items: List[bool]


class DbGenotype(DbBase):
    """Database representation of a genotype."""

    __tablename__ = "genotype"

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        autoincrement=True,
        primary_key=True,
    )
    items = Column(String, nullable=False)


class GenotypeSerializer(Serializer[Genotype]):
    @classmethod
    async def create_tables(cls, session: AsyncSession) -> None:
        """Create the tables for the genotype."""
        await (await session.connection()).run_sync(DbGenotype.metadata.create_all)

    @classmethod
    def identifying_table(cls) -> str:
        """Return the name of the table that identifies the genotype."""
        return DbGenotype.__tablename__

    @classmethod
    async def to_database(
        cls, session: AsyncSession, objects: List[Genotype]
    ) -> List[int]:
        """Save the objects to the database."""

        # Create the database objects
        db_objects = [
            DbGenotype(items="".join(["1" if gene else "0" for gene in genotype.items]))
            for genotype in objects
        ]

        # Save the objects to the database
        session.add_all(db_objects)

        # Flush the session to ensure that the IDs are assigned
        await session.flush()

        # Get the IDs of the objects
        ids = [db_object.id for db_object in db_objects if db_object.id is not None]

        # Check that the IDs were assigned
        assert len(ids) == len(objects)

        # Return the IDs of the objects
        return ids

    @classmethod
    async def from_database(
        cls, session: AsyncSession, ids: List[int]
    ) -> List[Genotype]:
        """Load the objects from the database."""

        # Get the database objects
        rows = (
            (await session.execute(select(DbGenotype).filter(DbGenotype.id.in_(ids))))
            .scalars()
            .all()
        )

        # Check that the correct number of objects were found
        if len(rows) != len(ids):
            print(f"Requested {len(ids)} objects, but only found {len(rows)}")
            raise IncompatibleError

        # Create the objects
        id_map = {row.id: row for row in rows}
        items_strs = [id_map[id].items for id in ids]
        items_bool = [[bool(int(gene)) for gene in item_str] for item_str in items_strs]
        objects = [Genotype(items=item) for item in items_bool]

        # Return the objects
        return objects


def random_genotype(rng: Random, probability: float, num_of_items: int) -> Genotype:
    """Generate a random genotype, by generating a random string of booleans."""
    return Genotype(
        rng.choices(
            [True, False], weights=[probability, 1 - probability], k=num_of_items
        )
    )


def _test() -> None:
    """Test the module."""

    # Test the Genotype class
    genotype = Genotype([True, True, True, True, True])
    print(f"genotype: {genotype}")

    # Test the random_genotype function
    items = [Item(1, 1), Item(2, 2), Item(3, 3), Item(4, 4), Item(5, 5)]
    genotype = random_genotype(rng=Random(), probability=0.5, num_of_items=len(items))
    print(f"items: {items}")
    print(f"genotype: {genotype}")


if __name__ == "__main__":
    _test()
