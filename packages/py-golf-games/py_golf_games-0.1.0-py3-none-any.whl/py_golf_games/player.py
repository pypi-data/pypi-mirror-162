#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from enum import unique


@unique
class Gender(Enum):
    M = 1
    F = 2


class Player(object):
    """
    >>> p = Player("SpongeBob", Gender.M, 10)
    >>> p.name
    'SpongeBob'
    >>> p.gender.name
    'M'
    >>> p.handicap
    10
    >>> str(p)
    'SpongeBob'
    """

    def __init__(self, name, gender, handicap=0, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self._name = name
        self._gender = gender
        self._handicap = handicap
        assert self._gender in list(Gender)

    @property
    def name(self):
        return self._name

    @property
    def gender(self):
        return self._gender

    @property
    def handicap(self):
        return self._handicap

    def __str__(self):
        return self._name


# vim: filetype=python
