#!/usr/bin/env python3

"""
Author:     as, jl, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# SQLAlchemy
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

# import os
# os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
DbBase = declarative_base()  # FIXME this is deprecated


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

    body_id = Column(
        Integer,
        nullable=False,
    )

    brain_id = Column(
        Integer,
        nullable=False,
    )
