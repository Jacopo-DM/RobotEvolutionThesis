#!/usr/bin/env python3

"""
Author:     as, jl. jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Future libraries
from __future__ import annotations

# Standard libraries
import pickle
from dataclasses import dataclass
from typing import List

# Third-party libraries
import numpy as np
import numpy.typing as npt

# Revolve
from revolve2.core.database import IncompatibleError, Serializer

# SQLAlchemy
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select

# Local libraries
from .genotype_schema import DbBase, DbGenotype


@dataclass
class Genotype:
    """A generic Lamarckian Array Genotype (LAG)."""

    genotype: npt.NDArray[np.float_]  # vector
    grid_size: int  # scalar


class GenotypeSerializer(Serializer[Genotype]):
    """Serializer for the `Genotype` class."""

    @classmethod
    async def create_tables(cls, session: AsyncSession) -> None:
        """
        Create all tables required for serialization.

        This function commits. TODO fix this

        Parameters
        ----------
        session : AsyncSession
            Database session used for creating the tables.
        """
        await (await session.connection()).run_sync(DbBase.metadata.create_all)

    @classmethod
    def identifying_table(cls) -> str:
        """
        Get the name of the primary table used for storage.

        :returns: The name of the primary table.
        """
        return DbGenotype.__tablename__

    @classmethod
    async def to_database(
        cls, session: AsyncSession, objects: List[Genotype]
    ) -> List[int]:
        """
        Serialize the provided objects to a database using the provided session.

        Parameters
        ----------
        session : AsyncSession
            Session used when serializing to the database. This session will not be committed by this function.
        objects : List[Genotype]
            The objects to serialize.

        Returns
        -------
        List[int]
            A list of ids to identify each serialized object.
        """
        # for every genotype in the list of genotypes to be serialized
        dbfitnesses = [
            DbGenotype(
                genome=pickle.dumps(genotype.genotype),
                grid_size=genotype.grid_size,
            )
            for genotype in objects
        ]

        session.add_all(dbfitnesses)
        await session.flush()

        ids = [
            dbfitness.id for dbfitness in dbfitnesses if dbfitness.id is not None
        ]  # cannot be none because not nullable. used to silence mypy
        assert len(ids) == len(objects)  # but check just to be sure

        return ids

    @classmethod
    async def from_database(
        cls, session: AsyncSession, ids: List[int]
    ) -> List[Genotype]:
        """
        Deserialize a list of objects from a database using the provided session.

        Parameters
        ----------
        session : AsyncSession
            Session used for deserialization from the database. No changes are made to the database.
        ids : List[int]
            Ids identifying the objects to deserialize.

        Returns
        -------
        List[Genotype]
            The deserialized objects.

        Raises
        ------
        IncompatibleError
            In case the database is not compatible with this serializer.
        """
        rows = (
            (await session.execute(select(DbGenotype).filter(DbGenotype.id.in_(ids))))
            .scalars()
            .all()
        )

        if len(rows) != len(ids):
            raise IncompatibleError()

        id_map = {t.id: t for t in rows}
        genotypes = []
        for id in ids:
            genotype = pickle.loads(id_map[id].genome)
            grid_size = id_map[id].grid_size
            genotypes.append(Genotype(genotype, grid_size))
        return genotypes
