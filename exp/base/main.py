#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

- ./runner.sh: check install
- python main.py --n_gen=NUM_OF_GEN: run the optimization
- python plot.py ./database simpleopt: plot the results (saved locally)
- python run_best.py: run the best individual

- python extra/calculators.py estimator NUM_OF_GEN SEC_PER_GEN: estimate the time to run the evolutionary optimizer 
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

    # Parameters for the evolutionary algorithm
    POPULATION_SIZE = 10
    OFFSPRING_SIZE = 10
    NUM_OF_GENERATIONS = 5

    # CPPN
    NUM_INITIAL_MUTATIONS = 10
    SIMULATION_TIME = 10.0
    SAMPLING_FREQUENCY = 60
    CONTROL_FREQUENCY = 5

    # Log experiment parameters
    logging.info(f"Population size: {POPULATION_SIZE}")
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
    db_id = DbId.root("opt")

    # multineat innovation databases
    innov_db_body = multineat.InnovationDatabase()  # type: ignore # STUB
    innov_db_brain = multineat.InnovationDatabase()  # type: ignore # STUB

    # Generate a list of random population
    initial_population = [
        random_genotype(innov_db_body, innov_db_brain, rng, NUM_INITIAL_MUTATIONS)
        for _ in range(POPULATION_SIZE)
    ]

    maybe_optimizer = await Optimizer.from_database(
        database=database,
        db_id=db_id,
        innov_db_body=innov_db_body,
        innov_db_brain=innov_db_brain,
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
            innov_db_brain=innov_db_brain,
            simulation_time=SIMULATION_TIME,
            sampling_frequency=SAMPLING_FREQUENCY,
            control_frequency=CONTROL_FREQUENCY,
        )

    # Log start optimization
    logging.info("Start optimization")

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

    # Run the main program
    import asyncio

    asyncio.run(main())
