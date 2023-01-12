#!/usr/bin/env python3

"""
Author:     as, jmdm
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
    """Stores serialized multineat genomes."""

    __tablename__ = "body_cppnwin_genotype"

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        unique=True,
        autoincrement=True,
        primary_key=True,
    )
    serialized_multineat_genome = sqlalchemy.Column(sqlalchemy.String, nullable=False)
