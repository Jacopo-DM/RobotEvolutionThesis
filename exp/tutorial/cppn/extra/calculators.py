#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2023-01-09
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""

# Third-party libraries
import fire


class Calculator(object):
    """A simple calculator class."""

    def estimator(self, generations: int, sec_per_generation: float) -> None:
        """Estimate the time to run the evolutionary optimizer.

        Parameters
        ----------
        generations
            The number of generations to run.
        time_per_generation
            The time to run a single generation.
        """
        # print in milliseconds
        print(f"{generations * sec_per_generation * 100} milliseconds")

        # print in seconds
        print(f"{generations * sec_per_generation} seconds")

        # print in minutes
        print(f"{generations * sec_per_generation / 60} minutes")

        # print in hours
        print(f"{generations * sec_per_generation / 3600} hours")


if __name__ == "__main__":
    fire.Fire(Calculator)
