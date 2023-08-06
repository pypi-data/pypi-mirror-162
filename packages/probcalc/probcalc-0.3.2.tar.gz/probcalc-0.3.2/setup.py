import pathlib
from setuptools import setup

if __name__ == "__main__":

    long_desc = '''`probcalc` is a library that aims to provide a probability calculator in any Python REPL. It's mainly aimed at IPython, since this is often regarded as the best Python REPL, but any of them will work with this library.

In statistics, we are often faced with random variables which are distributed as certain probability distributions and we need to work out the probability of certain things happening. This is often tedious and error-prone. `probcalc` is the solution.

Let's say you flip a coin 100 times and want to work out the probability of getting at least 30 but less than 50 heads. You can say that `X` is a random variable representing the number of heads you get in 100 throws and then `X` is distributed as a binomial distribution with 100 trials and probability of one half. This is where `probcalc` comes in. You just define the variables and let the computer do the work:

```python3
>>> from probcalc import P, B
>>> X = B(100, 0.5)
>>> P(10 < X <= 20)
0.4601893013
```

Or, let's say there's a call center that gets an average of 5 calls every minute and you want to know the probability that they get more than 10 calls in a minute. For this, we can use a Poisson distribution:

```python3
>>> from probcalc import Po
>>> Y = Po(5)
>>> P(Y > 10)
0.3840393452
```

And of course, you can use the normal distribution:

```python3
>>> from probcalc import N
>>> Z = N(0, 1)
>>> P(-1 < Z < 1)
0.6826894723
```

This project will implement more distributions in the future, and they will all be able to be used like this.

The full docs are available [here](https://doctordalek1963.github.io/probcalc).

## Changelog

### [Unreleased]

### v0.3.2
- Disallow keyword arguments when using `P()`
- Make backend attributes and methods non-public
- Use readthedocs.io for documentation

### v0.3.1
- Improve performance of normal distribution CDF with stdlib

### v0.3.0
- Add normal distribution
- Use more efficient calculations of binomial PMF
- Check for nonsense in inequality assignment

### v0.2.8
- Remove SciPy dependency by implemeting Poisson pmf with stdlib

### v0.2.7
- Fix bug in `ProbabilityCalculator` with resetting bounds after getting an error
- Deal with edge case in `BinomialDistribution.calculate()`

### v0.2.6
- Handle edge case in binomial distributions
- Allow Poisson to handle much larger numbers

### v0.2.5
- Add nice repr for probability calculator
- Implement `!=` functionality

### v0.2.4
- Fix mistake in publish workflow

### v0.2.3
- Fix bug in automated tests

### v0.2.2
- Add changelog

### v0.2.1
- Set up PyPI stuff and GitHub Action for PyPI

### v0.2.0
- Add Poisson distribution

### v0.1.2
- Fix minor issues

### v0.1.1
- Improve documentation and add alias table

### 0.1.0
- Initial version
- Add Binomial distribution
- Add P() syntax
'''

    setup(
        long_description=long_desc,
        long_description_content_type='text/markdown'
    )
