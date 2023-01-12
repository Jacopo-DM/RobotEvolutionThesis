#!/usr/bin/env python3

"""
Author:     as, jl, jmdm
Date:       2023-01-10
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

- ./runner.sh: check install (note this will probably throw errors)
- python main.py --n_gen=NUM_OF_GEN: run the optimization
- python plot.py ./database simpleopt: plot the results (saved locally)
- python run_best.py: run the best individual
- python plot_learning.py ./extra/database openaies

- python extra/calculators.py estimator NUM_OF_GEN SEC_PER_GEN: estimate the time to run the evolutionary optimizer 


The code, in general has the following structure:
optimize_robot:
    init_robot_population
    for generation in num_gen:
        start_fitness = evaluate(population)
        learning_period.run(population)
        end_fitness = evaluate(population)
        return end_fitness 
"""

# Standard libraries
import logging
import time
from random import Random

# Multineat
import multineat

# Revolve2
from revolve2.core.database import open_async_database_sqlite
from revolve2.core.optimization import DbId

# Local libraries
from extra import Clr, setup
from utils import Optimizer
from utils import random as random_genotype


async def main() -> None:
    """Run the main program."""

    # General parameters for the evolutionary algorithm
    POPULATION_SIZE = 50
    OFFSPRING_SIZE = 25
    NUM_OF_GENERATIONS = 100

    # Specific parameters for the simulation
    SIMULATION_TIME = 15
    SAMPLING_FREQUENCY = 5
    CONTROL_FREQUENCY = 60

    # Number of mutations to apply to the initial population
    NUM_INITIAL_MUTATIONS = 10

    # Log experiment parameters
    logging.info(f"Population size: {Clr.green}{POPULATION_SIZE}{Clr.end}")
    logging.info(f"Offspring size: {Clr.green}{OFFSPRING_SIZE}{Clr.end}")
    logging.info(f"Number of generations: {Clr.green}{NUM_OF_GENERATIONS}{Clr.end}")
    logging.info(
        f"Number of initial mutations: {Clr.green}{NUM_INITIAL_MUTATIONS}{Clr.end}"
    )
    logging.info(f"Simulation time: {Clr.green}{SIMULATION_TIME}{Clr.end}")
    logging.info(f"Sampling frequency: {Clr.green}{SAMPLING_FREQUENCY}{Clr.end}")
    logging.info(f"Control frequency: {Clr.green}{CONTROL_FREQUENCY}{Clr.end}")

    # Random number generator
    rng = Random()
    rng.seed(28)

    # database
    database = open_async_database_sqlite("./extra/database", create=True)

    # unique database identifier for optimizer
    db_id = DbId.root("opt")  # learning delta optimization

    # multineat innovation databases
    innov_db_body = multineat.InnovationDatabase()  # type: ignore # STUB

    # Generate a list of random population
    initial_population = [
        random_genotype(
            innov_db_body=innov_db_body,
            rng=rng,
            num_initial_mutations=NUM_INITIAL_MUTATIONS,
            brain_grid_size=22,
        )
        for _ in range(POPULATION_SIZE)
    ]

    maybe_optimizer = await Optimizer.from_database(
        database=database,
        db_id=db_id,
        innov_db_body=innov_db_body,
        rng=rng,
    )
    if maybe_optimizer is not None:
        optimizer = maybe_optimizer
    else:
        optimizer = await Optimizer.new(
            database=database,
            db_id=db_id,
            num_generations=NUM_OF_GENERATIONS,
            offspring_size=OFFSPRING_SIZE,
            initial_population=initial_population,
            rng=rng,
            innov_db_body=innov_db_body,
            simulation_time=SIMULATION_TIME,
            sampling_frequency=SAMPLING_FREQUENCY,
            control_frequency=CONTROL_FREQUENCY,
        )

    # Log start optimization
    logging.info("=== Start optimization ===")

    # Run the optimizer
    start = time.time()
    await optimizer.run()
    end = time.time()

    # Log end optimization
    logging.info("End optimization")

    # Log time taken
    logging.info(f"Number of generations: {NUM_OF_GENERATIONS}")
    logging.info(f"Time: {time.strftime('%H h %M m %S s', time.gmtime(end - start))}")
    logging.info(
        f"Time per generation: {round((end - start) / NUM_OF_GENERATIONS * 100, 3)} cs"
    )
    logging.info(
        f"Time per generation: {round((end - start) / NUM_OF_GENERATIONS, 3)} s"
    )
    logging.info(
        f"Time per generation: {round((end - start) / NUM_OF_GENERATIONS / 60, 3)} min"
    )


if __name__ == "__main__":
    """Run the main program."""

    # Setup logging and check install
    setup()

    # remove ./extra/database
    import shutil

    shutil.rmtree("./extra/database", ignore_errors=True)

    # Run the main program
    import asyncio

    asyncio.run(main())
