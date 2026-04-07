"""Definitions for ternary and signed binary state representations.

Balanced ternary values are used throughout this package to express
three valued semantics: positive (+1), neutral (0) and negative (−1).
These states capture notions of approval, witness/uncertainty and
opposition respectively.  Balanced ternary is more expressive than
ordinary binary and allows algorithms to explicitly defer judgment when
evidence is insufficient.

Signed binary values are two valued states which carry polarity.  They
are useful for modelling pure support/opposition dynamics without a
neutral option.  They can also be combined with ternary values to
express richer spaces of outcomes.

The enumerations defined here can be compared, iterated over and
converted to integers.  They are implemented using Python's
``Enum`` class to provide clear names and type safety.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class BalancedTernary(Enum):
    """An enumeration for balanced ternary values.

    Each member represents one of three distinct semantic states:

    * ``NEGATIVE``: indicates opposition, rejection or an adversarial
      interpretation.  Numerically equals −1.
    * ``NEUTRAL``: indicates the node does not take a position yet, either
      due to insufficient evidence or because it serves as a witness
      recording observations.  Numerically equals 0.
    * ``POSITIVE``: indicates support, acceptance or alignment.  Numerically
      equals +1.

    Arithmetic operations on the raw integer value can be used to
    aggregate votes across multiple nodes or bundles.  For example,
    summing ternary votes and thresholding the result can produce a
    fused decision.
    """

    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        names = {
            BalancedTernary.NEGATIVE: "NEGATIVE",
            BalancedTernary.NEUTRAL: "NEUTRAL",
            BalancedTernary.POSITIVE: "POSITIVE",
        }
        return names[self]

    @classmethod
    def from_int(cls, val: int) -> "BalancedTernary":
        """Create a ``BalancedTernary`` from an integer.

        Parameters
        ----------
        val:
            An integer in {−1, 0, 1}.

        Returns
        -------
        BalancedTernary
            The corresponding ternary value.

        Raises
        ------
        ValueError
            If ``val`` is not one of −1, 0 or 1.
        """
        if val not in (-1, 0, 1):
            raise ValueError(f"Cannot convert {val} to BalancedTernary")
        return cls(val)


class SignedBinary(Enum):
    """An enumeration for signed binary (polarity) values.

    Members represent pure support/opposition dynamics:

    * ``NEGATIVE``: indicates an adversarial or opposing force (−1).
    * ``POSITIVE``: indicates support or alignment (+1).

    ``SignedBinary`` does not include a neutral element; if neutrality is
    required, use :class:`BalancedTernary` instead.
    """

    NEGATIVE = -1
    POSITIVE = 1

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return "NEGATIVE" if self is SignedBinary.NEGATIVE else "POSITIVE"

    @classmethod
    def from_int(cls, val: int) -> "SignedBinary":
        """Create a ``SignedBinary`` from an integer.

        Accepts only −1 or +1.  Use ``BalancedTernary`` if a neutral state
        is required.
        """
        if val not in (-1, 1):
            raise ValueError(f"Cannot convert {val} to SignedBinary")
        return cls(val)



def balanced_ternary_sum(values: list[BalancedTernary]) -> int:
    """Compute the numeric sum of a list of ternary values.

    Parameters
    ----------
    values:
        A sequence of :class:`BalancedTernary` members.

    Returns
    -------
    int
        The arithmetic sum of the integer codes (−1 for NEGATIVE,
        0 for NEUTRAL, +1 for POSITIVE).  The result is an integer
        between ``−len(values)`` and ``+len(values)`` inclusive.
    """
    return sum(int(v) for v in values)



def majority_vote(values: list[BalancedTernary]) -> BalancedTernary:
    """Compute a majority vote among ternary values.

    A majority vote returns the value that appears most often in
    ``values``.  Ties between NEGATIVE and POSITIVE votes result in
    ``NEUTRAL``.  If all values are ``NEUTRAL``, the result is also
    ``NEUTRAL``.

    Parameters
    ----------
    values:
        A list of ternary values from which to compute the majority.

    Returns
    -------
    BalancedTernary
        The most common value or ``NEUTRAL`` in case of a tie.
    """
    counts = {BalancedTernary.NEGATIVE: 0, BalancedTernary.NEUTRAL: 0, BalancedTernary.POSITIVE: 0}
    for v in values:
        counts[v] += 1
    # If there is a tie between NEGATIVE and POSITIVE and neither has
    # strictly more votes than the other, return NEUTRAL.
    if counts[BalancedTernary.NEGATIVE] == counts[BalancedTernary.POSITIVE] != 0:
        return BalancedTernary.NEUTRAL
    # Otherwise return the key with the maximum count.
    return max(counts, key=counts.get)
