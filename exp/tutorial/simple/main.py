#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-04
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"

- ./runner.sh: check install
- python main.py: run the optimization
- python plot.py ./database simpleopt: plot the results (saved locally)
"""

# Standard libraries
import logging
import time
from random import Random

# Third-party libraries
from revolve2.core.database import open_async_database_sqlite
from revolve2.core.optimization import DbId

# Local libraries
from utils import Optimizer, random_genotype, random_items, setup


async def main() -> None:
    """Run the main program."""

    # Parameters for the evolutionary algorithm
    POPULATION_SIZE = 100
    OFFSPRING_SIZE = 100
    NUM_OF_GENERATIONS = 5000
    ITEM_PROBABILITY = 0.5
    MAX_WEIGHT = 300

    # Random number generator
    rng = Random()
    rng.seed(28)

    # Generate a list of random items
    items = random_items(
        rng=rng,
        num_of_items=POPULATION_SIZE,
        low_range=1,
        high_range=100,
    )

    # database
    database = open_async_database_sqlite("./extra/database", create=True)

    # unique database identifier for optimizer
    db_id = DbId.root("opt")

    initial_population = [
        random_genotype(rng, ITEM_PROBABILITY, len(items))
        for _ in range(POPULATION_SIZE)
    ]

    maybe_optimizer = await Optimizer.from_database(
        database=database,
        db_id=db_id,
        rng=rng,
        items=items,
        max_weight=MAX_WEIGHT,
        num_generations=NUM_OF_GENERATIONS,
    )
    if maybe_optimizer is not None:
        optimizer = maybe_optimizer
    else:
        optimizer = await Optimizer.new(
            database=database,
            db_id=db_id,
            offspring_size=OFFSPRING_SIZE,
            initial_population=initial_population,
            rng=rng,
            items=items,
            max_weight=MAX_WEIGHT,
            num_generations=NUM_OF_GENERATIONS,
        )
    # Log start optimization
    logging.info("Start optimization")

    # Run the optimizer
    start = time.time()
    await optimizer.run()
    end = time.time()

    # Log end optimization
    logging.info("End optimization")

    # Log time (format hh h mm min ss sec ms)
    logging.info(f"Number of generations: {NUM_OF_GENERATIONS}")
    logging.info(f"Time: {time.strftime('%H h %M m %S s', time.gmtime(end - start))}")
    # time per generation in centiseconds
    logging.info(
        f"Time per generation: {round((end - start) / NUM_OF_GENERATIONS * 100, 3)} cs"
    )
    # time per generation in seconds
    logging.info(
        f"Time per generation: {round((end - start) / NUM_OF_GENERATIONS, 3)} s"
    )
    # time per generation in minutes
    logging.info(
        f"Time per generation: {round((end - start) / NUM_OF_GENERATIONS / 60, 3)} min"
    )


if __name__ == "__main__":
    import asyncio

    setup()
    asyncio.run(main())
