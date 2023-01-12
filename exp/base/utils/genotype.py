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
from typing import List

# Revolve2
from revolve2.core.database import IncompatibleError, Serializer

# SQLAlchemy
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

# Genotypes
from body.cppnwin import Genotype as BodyGenotype
from body.cppnwin import GenotypeSerializer as BodyGenotypeSerializer
from brain.cppnwin import Genotype as BrainGenotype
from brain.cppnwin import GenotypeSerializer as BrainGenotypeSerializer

# Local libraries
from .genotype_schema import DbBase, DbGenotype


@dataclass
class Genotype:
    """Genotype for the knapsack problem."""

    body: BodyGenotype
    brain: BrainGenotype


class GenotypeSerializer(Serializer[Genotype]):
    @classmethod
    async def create_tables(cls, session: AsyncSession) -> None:
        """Create the tables for the genotype."""

        await (await session.connection()).run_sync(DbBase.metadata.create_all)
        await BodyGenotypeSerializer.create_tables(session)
        await BrainGenotypeSerializer.create_tables(session)

    @classmethod
    def identifying_table(cls) -> str:
        """Return the name of the table that identifies the genotype."""
        return DbGenotype.__tablename__

    @classmethod
    async def to_database(
        cls, session: AsyncSession, objects: List[Genotype]
    ) -> List[int]:
        """Save the objects to the database."""

        # Save the bodies to the database
        body_ids = await BodyGenotypeSerializer.to_database(
            session, [genotype.body for genotype in objects]
        )

        # Save the brains to the database
        brain_ids = await BrainGenotypeSerializer.to_database(
            session, [genotype.brain for genotype in objects]
        )

        # Create the database objects
        db_objects = [
            DbGenotype(
                body_id=body_id,
                brain_id=brain_id,
            )
            for body_id, brain_id in zip(body_ids, brain_ids)
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

        # Get ID's
        body_ids = [id_map[id].body_id for id in ids]
        brain_ids = [id_map[id].brain_id for id in ids]

        # Get genotypes
        body_genotypes = await BodyGenotypeSerializer.from_database(session, body_ids)

        brain_genotypes = await BrainGenotypeSerializer.from_database(
            session, brain_ids
        )

        # Form objects
        objects = [
            Genotype(body=body, brain=brain)
            for body, brain in zip(body_genotypes, brain_genotypes)
        ]

        # Return the objects
        return objects
