#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-09
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

Plot average, min, and max fitness over generations, using the results of the evolutionary optimizer.

Assumes fitness is a float and database is files.
See program help for what inputs to provide.

"""

# Third-party libraries
import fire
import matplotlib.pyplot as plt
import pandas

# Revolve2
from revolve2.core.database import open_database_sqlite
from revolve2.core.database.serializers import DbFloat
from revolve2.core.optimization import DbId
from revolve2.core.optimization.ea.generic_ea import (
    DbEAOptimizer,
    DbEAOptimizerGeneration,
    DbEAOptimizerIndividual,
)
from revolve2.core.optimization.ea.openai_es import DbOpenaiESOptimizerIndividual

# SQLAlchemy
from sqlalchemy.future import select

# Local libraries
from extra import Palette
from utils.optimizer_schema import DbFitness

# Plotting parameters
STYLE = "bmh"
DPI = 500
font = {"weight": "bold", "size": 9}
plt.rc("font", **font)


class Plot(object):
    def learn(self, database: str, _db_id: str) -> None:
        """
        Do the actual plotting.

        :param database: The database with the results.
        :param db_id: The id of the ea optimizer to plot.
        """
        # DbId
        db_id = DbId(_db_id)

        # open the database
        db = open_database_sqlite(database)
        # read the optimizer data into a pandas dataframe
        df = pandas.read_sql(
            select(DbOpenaiESOptimizerIndividual).filter(
                DbOpenaiESOptimizerIndividual.db_id == "openaies"
            ),
            db,
        )
        # calculate max min avg
        describe = (
            df[["gen_num", "fitness"]].groupby(by="gen_num").describe()["fitness"]
        )
        mean = describe[["mean"]].values.squeeze()
        std = describe[["std"]].values.squeeze()

        # ==== Plotting ====
        plt.style.use(STYLE)

        # Plot the mean and std
        describe[["max", "mean", "min"]].plot(
            color=[Palette.GREEN, Palette.PINK, Palette.ORANGE],
        )

        plt.fill_between(
            range(len(mean)),
            mean - std,
            mean + std,
            alpha=0.3,
            color=Palette.PINK,
            label="std mean",
        )

        plt.title(f"Fitness Over Generations for '{db_id.fullname}'")

        plt.xlabel("Generation")

        plt.ylabel("Fitness")

        plt.legend(loc="best")

        # Save the plot
        plt.savefig(f"./extra/{db_id.fullname}.png", dpi=DPI)

    def basic(self, database: str, _db_id: str) -> None:
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
        # # Horizontal line at avg of best and add text with value and std
        # plt.axhline(
        #     describe["max"].mean(),
        #     color=Palette.DARK_GREEN,
        #     linestyle="--",
        #     label=f"avg max: {describe['max'].mean():.2f} ± {describe['max'].std():.2f}",
        # )

        # # Horizontal line at avg of avg
        # plt.axhline(
        #     describe["mean"].mean(),
        #     color=Palette.DARK_PINK,
        #     linestyle="--",
        #     label=f"avg mean: {describe['mean'].mean():.2f} ± {describe['mean'].std():.2f}",
        # )

        # # Horizontal line at avg of worst
        # plt.axhline(
        #     describe["min"].mean(),
        #     color=Palette.DARK_ORANGE,
        #     linestyle="--",
        #     label=f"avg min: {describe['min'].mean():.2f} ± {describe['min'].std():.2f}",
        # )

        plt.fill_between(
            range(len(mean)),
            mean - std,
            mean + std,
            alpha=0.3,
            color=Palette.PINK,
            label="std mean",
        )

        plt.title(f"Fitness Over Generations for '{db_id.fullname}'")

        plt.xlabel("Generation")

        plt.ylabel("Fitness")

        plt.legend(loc="best")

        # Save the plot
        plt.savefig(f"./extra/{db_id.fullname}.png", dpi=DPI)

    def fit(self, database: str, _db_id: str) -> None:
        """
        Do the actual plotting.

        :param database: The database with the results.
        :param db_id: The id of the ea optimizer to plot.
        """
        # DbId
        db_id = DbId(_db_id)

        # open the database
        db = open_database_sqlite(database)
        # read the optimizer data into a pandas dataframe
        df = pandas.read_sql(
            select(DbFitness).filter((DbEAOptimizer.db_id == db_id.fullname)),
            db,
        )

        # calculate max min avg
        describe = (
            df[["generation_index", "fitness_after"]]
            .groupby(by="generation_index")
            .describe()["fitness_after"]
        )
        mean = describe[["mean"]].values.squeeze()
        std = describe[["std"]].values.squeeze()

        # ==== Plotting ====
        plt.style.use(STYLE)

        # Plot the mean and std
        describe[["max", "mean", "min"]].plot(
            color=[Palette.GREEN, Palette.PINK, Palette.ORANGE],
        )

        plt.fill_between(
            range(len(mean)),
            mean - std,
            mean + std,
            alpha=0.3,
            color=Palette.PINK,
            label="std mean",
        )

        plt.title(f"Fitness Over Generations for '{db_id.fullname}'")

        plt.xlabel("Generation")

        plt.ylabel("Fitness")

        plt.legend(loc="best")

        # Save the plot
        plt.savefig(f"./extra/fit_{db_id.fullname}.png", dpi=DPI)


def main() -> None:
    """Run this file as a command line tool."""

    # Fire the command line tool
    fire.Fire(Plot)


if __name__ == "__main__":
    main()
