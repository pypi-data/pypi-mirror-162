# probcalc - Calculate probabilities for distributions
# Copyright (C) 2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module contains classes for various probability distributions, and a convenience function."""

from __future__ import annotations

import math
from typing import Literal

from .distribution_classes import Distribution, NonsenseError

# Compute constants at import time for slight speed increase
ROOT_TWO = math.sqrt(2)
ROOT_TWO_PI = math.sqrt(2 * math.pi)


class BinomialDistribution(Distribution):
    """This is a binomial distribution, used to model multiple independent, binary trials."""

    def __init__(self, number_of_trials: int, probability: float):
        """Construct a binomial distribution from a given number of trials and probability of success for each trial."""
        if not 0 <= probability <= 1:
            raise NonsenseError(f'Binomial probability must be between 0 and 1, not {probability}')

        super().__init__(accepts_floats=False)

        self._number_of_trials = number_of_trials
        self._probability = probability

    def __repr__(self) -> str:
        """Return a nice repr of the distribution."""
        return f'B({self._number_of_trials}, {self._probability})'

    def _check_nonsense(self, successes: int, *, strict: bool) -> Literal[None, -1]:
        """Check if the given number of successes is nonsense.

        :param int successes: The number of successes to check
        :param bool strict: Whether to throw errors or just return -1
        :returns: None on success, -1 on fail
        :rtype: Literal[None, -1]

        :raises NonsenseError: If the number of successes is outside the valid range
        :raises NonsenseError: If the number of successes is not an integer
        """
        if successes < 0:
            if strict:
                raise NonsenseError(f'Cannot have negative number of successes ({successes})')

            return -1

        if successes > self._number_of_trials:
            if strict:
                raise NonsenseError(f'Cannot have more successes ({successes}) than trials ({self._number_of_trials})')

            return -1

        if successes != int(successes):
            if strict:
                raise NonsenseError(f'Cannot ask probability of {successes} successes')

            return -1

        return None

    def pmf(self, successes: int, *, strict: bool = True) -> float:
        r"""Return the probability that we get a given number of successes.

        This method uses the formula :math:`\binom{n}{r} p^r q^{n - r}` where
        :math:`n` is the number of trials, :math:`r` is the number of successes,
        :math:`p` is the probability of each success, and :math:`q = 1 - p`.

        :param int successes: The number of successes to find the probability of
        :param bool strict: Whether to throw errors for invalid input, or return 0
        :returns float: The probability of getting exactly this many successes

        :raises NonsenseError: If the number of successes is outside the valid range
        :raises NonsenseError: If the number of successes is not an integer
        """
        if self._check_nonsense(successes, strict=strict) is not None:
            return 0

        # PMF taken from https://github.com/scipy/scipy/blob/main/scipy/stats/_discrete_distns.py#L67-L74
        magic_number = math.lgamma(self._number_of_trials + 1) - (
                math.lgamma(successes + 1) +
                math.lgamma(self._number_of_trials - successes + 1)
        )

        return math.exp(
            magic_number +
            successes * math.log(self._probability) +
            (self._number_of_trials - successes) * math.log1p(-self._probability)
        )

    def cdf(self, successes: int, *, strict: bool = True) -> float:
        """Return the probability that we get less than or equal to the given number of successes.

        This method just sums :meth:`pmf` from 0 to the given number of successes.

        :param int successes: The number of successes to find the probability for
        :param bool strict: Whether to throw errors for invalid input, or return 0
        :returns float: The probability of getting less than or equal to this many successes

        :raises NonsenseError: If the number of successes is outside the valid range
        :raises NonsenseError: If the number of successes is not an integer
        """
        if self._check_nonsense(successes, strict=strict) is not None:
            return 0

        if successes == self._number_of_trials:
            return 1

        # mypy expects this sum to have ints for some reason, so we ignore it
        return sum(self.pmf(x) for x in range(successes + 1))  # type: ignore[misc]

    def calculate(self, *, strict: bool = True) -> float:
        """Check for nonsense in an edge case.

        This method overrides :meth:`Distribution.calculate`. See that method for documentation.
        """
        if self.bounds.lower == (self._number_of_trials, False):
            raise NonsenseError(f'Cannot have more successes (> {self._number_of_trials}) '
                                f'than trials ({self._number_of_trials})')

        return super().calculate(strict=strict)


class PoissonDistribution(Distribution):
    """This is a Poisson distribution, used to model independent events that happen at a constant average rate."""

    def __init__(self, rate: float):
        """Construct a Poisson distribution with the given average rate of event occurrence."""
        if rate < 0:
            raise NonsenseError(f'Cannot have negative rate in Poisson distribution ({rate})')

        super().__init__(accepts_floats=False)

        self._rate = rate

    def __repr__(self) -> str:
        """Return a nice repr of the distribution."""
        return f'Po({self._rate})'

    @staticmethod
    def _check_nonsense(number: int, *, strict: bool = True) -> Literal[None, -1]:
        """Check if the given number of event occurrences is nonsense.

        :param int number: The number of occurrences to check
        :param bool strict: Whether to throw errors or just return -1
        :returns: None on success, -1 on fail
        :rtype: Literal[None, -1]

        :raises NonsenseError: If the number is negative
        :raises NonsenseError: If the number is not an integer
        """
        if number < 0:
            if strict:
                raise NonsenseError(f'Cannot have negative number of event occurrences ({number})')

            return -1

        if number != int(number):
            if strict:
                raise NonsenseError(f'Number of occurrences must be an integer, not {number}')

            return -1

        return None

    def pmf(self, number: int, *, strict: bool = True) -> float:
        r"""Return the probability that we get a given number of occurrences.

        This method uses the formula :math:`\frac{e^{-\lambda} \lambda^x}{x!}`,
        where :math:`x` is the number of occurrences and :math:`\lambda` is the
        rate of the distribution.

        :param int number: The number of occurrences to find the probability of
        :param bool strict: Whether to throw errors for invalid input, or return 0
        :returns float: The probability of getting exactly this many occurrences

        :raises NonsenseError: If the number of occurrences is negative
        :raises NonsenseError: If the number of occurrences is not an integer
        """
        if self._check_nonsense(number, strict=strict) is not None:
            return 0

        if number == 0:
            return math.exp(-self._rate)

        # This line is pure magic that I stole from the SciPy source code
        # https://github.com/scipy/scipy/blob/main/scipy/stats/_discrete_distns.py#L854-L860
        log_pmf = number * math.log(self._rate) - math.lgamma(number + 1) - self._rate
        return math.exp(log_pmf)

    def cdf(self, number: int, *, strict: bool = True) -> float:
        """Return the probability that we get less than or equal to the given number of occurrences.

        This method just sums :meth:`pmf` from 0 to the given number of occurrences.

        :param int number: The number of occurrences to find the probability for
        :param bool strict: Whether to throw errors for invalid input, or return 0
        :returns float: The probability of getting less than or equal to this many occurrences

        :raises NonsenseError: If the number of occurrences is negative
        :raises NonsenseError: If the number of occurrences is not an integer
        """
        if self._check_nonsense(number, strict=strict) is not None:
            return 0

        return sum(self.pmf(x) for x in range(number + 1))  # type: ignore[misc]


class NormalDistribution(Distribution):
    """A normal distribution with mean and standard deviation."""

    def __init__(self, mean: float, std_dev: float):
        """Create a normal distribution with given mean and standard deviation.

        .. note:: We use standard deviation, not variance.
        """
        if std_dev == 0:
            raise NonsenseError('Cannot have standard deviation of 0')

        if std_dev < 0:
            raise NonsenseError('Cannot have negative standard deviation')

        super().__init__(accepts_floats=True)

        self._mean = mean
        self._std_dev = std_dev

    def __repr__(self) -> str:
        """Return a nice repr of the distribution."""
        return f'N({self._mean}, {self._std_dev}²)'

    def __lt__(self, other):
        """Call :meth:`probcalc.distribution_classes.Distribution.__le__`.

        This is because normal distributions don't distinguish strong/weak inequality.
        """
        return super().__le__(other)

    def __ge__(self, other):
        """Call :meth:`probcalc.distribution_classes.Distribution.__gt__`.

        This is because normal distributions don't distinguish strong/weak inequality.
        """
        return super().__gt__(other)

    def pmf(self, value: float, *, strict: bool = True) -> float:
        """Return the probability of getting the given value from this normal distribution.

        :param float value: The value to find the probability of
        :param bool strict: Whether to throw errors for invalid input, or return 0
        :returns float: The probability of getting exactly this many occurrences
        """
        exponent = -0.5 * (((value - self._mean) / self._std_dev) ** 2)
        return math.exp(exponent) / (self._std_dev * ROOT_TWO_PI)

    def cdf(self, value: float, *, strict: bool = True) -> float:
        r"""Return the probability that we get less than or equal to the given number of occurrences.

        This method uses the formula :math:`\frac{1}{2}\left[1+\text{erf}\left(\frac{x}{\sqrt{2}}\right)\right]`

        :param int value: The value to find the probability for
        :param bool strict: Whether to throw errors for invalid input, or return 0
        :returns float: The probability of getting less than or equal to this value
        """
        return 0.5 * (1 + math.erf((value - self._mean) / (self._std_dev * ROOT_TWO)))
