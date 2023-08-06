"""
::

    Sphinx-autodoc can't document typevars properly right now,
    see https://github.com/agronholm/sphinx-autodoc-typehints/issues/39
"""
from typing import List, TypeVar, NewType

IndexType = TypeVar('IndexType')
"""Generic index type."""

EchelonType = NewType('EchelonType', List[IndexType])
"""Nothing but a list of indices of the data."""

EchelonsType = NewType('EchelonsType', List[EchelonType])
"""List of echelons."""
