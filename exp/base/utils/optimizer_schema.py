#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# SQLAlchemy
from sqlalchemy import Column, Float, Integer, PickleType, String
from sqlalchemy.ext.declarative import declarative_base

# import os
# os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
DbBase = declarative_base()  # FIXME this is deprecated


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
