#!/usr/bin/env python3

"""
Author:     jmdm
Date:       YYYY-MM-DD
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

Plot average, min, and max fitness over generations, using the results of the evolutionary optimizer.

Assumes fitness is a float and database is files.
See program help for what inputs to provide.

"""

# Standard libraries
import argparse

# Third-party libraries
import fire  # type: ignore # FIXME cannot find stubs
import matplotlib.pyplot as plt  # type: ignore # FIXME cannot find stubs
import pandas
from revolve2.core.database import open_database_sqlite
from revolve2.core.database.serializers import DbFloat
from revolve2.core.optimization import DbId
from revolve2.core.optimization.ea.generic_ea import (
    DbEAOptimizer,
    DbEAOptimizerGeneration,
    DbEAOptimizerIndividual,
)
from revolve2.core.optimization.ea.openai_es import DbOpenaiESOptimizerIndividual
from sqlalchemy.future import select

# Local libraries
from utils import Palette

# Plotting parameters
STYLE = "bmh"
DPI = 500
font = {"weight": "bold", "size": 9}
plt.rc("font", **font)


def plot(database: str, _db_id: str) -> None:
    """
    Plot fitness as described at the top of this file.

    Parameters
    ----------
    database
        The database file.
    _db_id
        The database id.
    """

    # DbId
    db_id = DbId(_db_id)

    # Open the database
    db = open_database_sqlite(database)

    # Read the optimizer data into a pandas dataframe
    df = pandas.read_sql(
        select(
            DbEAOptimizer,
            DbEAOptimizerGeneration,
            DbEAOptimizerIndividual,
            DbFloat,
        ).filter(
            (DbEAOptimizer.db_id == db_id.fullname)
            & (DbEAOptimizerGeneration.ea_optimizer_id == DbEAOptimizer.id)
            & (DbEAOptimizerIndividual.ea_optimizer_id == DbEAOptimizer.id)
            & (DbEAOptimizerIndividual.fitness_id == DbFloat.id)
            & (
                DbEAOptimizerGeneration.individual_id
                == DbEAOptimizerIndividual.individual_id
            )
        ),
        db,
    )

    # Calculate max min avg
    describe = (
        df[["generation_index", "value"]]
        .groupby(by="generation_index")
        .describe()["value"]
    )
    mean = describe[["mean"]].values.squeeze()
    std = describe[["std"]].values.squeeze()

    # ==== Plotting ====
    plt.style.use(STYLE)

    # Plot the mean and std
    describe[["max", "mean", "min"]].plot(
        color=[Palette.GREEN, Palette.PINK, Palette.ORANGE],
    )
    # Horizontal line at avg of best and add text with value and std
    plt.axhline(
        describe["max"].mean(),
        color=Palette.DARK_GREEN,
        linestyle="--",
        label=f"avg max: {describe['max'].mean():.2f} ± {describe['max'].std():.2f}",
    )

    # Horizontal line at avg of avg
    plt.axhline(
        describe["mean"].mean(),
        color=Palette.DARK_PINK,
        linestyle="--",
        label=f"avg mean: {describe['mean'].mean():.2f} ± {describe['mean'].std():.2f}",
    )

    # Horizontal line at avg of worst
    plt.axhline(
        describe["min"].mean(),
        color=Palette.DARK_ORANGE,
        linestyle="--",
        label=f"avg min: {describe['min'].mean():.2f} ± {describe['min'].std():.2f}",
    )

    plt.title(f"Fitness Over Generations for '{db_id.fullname}'")

    plt.xlabel("Generation")

    plt.ylabel("Fitness")

    plt.legend(loc="best")

    plt.fill_between(
        range(len(mean)),
        mean - std,
        mean + std,
        alpha=0.3,
        color=Palette.BLUE,
    )

    # Save the plot
    plt.savefig(f"./extra/{db_id.fullname}.png", dpi=DPI)


def main() -> None:
    """Run this file as a command line tool."""

    # Fire the command line tool
    fire.Fire(plot)


if __name__ == "__main__":
    main()
