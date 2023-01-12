#!/usr/bin/env python3

"""
Author:     as, jl. jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

# import os
# os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
DbBase = declarative_base()  # FIXME this is deprecated


class DbGenotype(DbBase):
    """Stores serialized genomes."""

    __tablename__ = "brain_lag_genotype"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        unique=True,
        autoincrement=True,
        primary_key=True,
    )

    genome = sqlalchemy.Column(sqlalchemy.PickleType, nullable=False)

    grid_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
