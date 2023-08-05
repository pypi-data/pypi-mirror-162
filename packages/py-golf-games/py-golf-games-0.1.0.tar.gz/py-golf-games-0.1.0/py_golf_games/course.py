#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Course(object):
    """
    >>> from .hole import Hole
    >>> from .tee import TeeMarker, Tee
    >>> c = Course("Hawaii Kai")
    >>> c.name
    'Hawaii Kai'
    >>> t1 = Tee(TeeMarker.Gold, 5, 600, 1)
    >>> t2 = Tee(TeeMarker.Gold, 3, 300, 2)
    >>> h1 = Hole(1, {TeeMarker.Gold: t1})
    >>> h2 = Hole(2, {TeeMarker.Gold: t2})
    >>> c.add_hole(1, h1)
    >>> c.add_hole(2, h2)
    >>> c.total_distance(TeeMarker.Gold)
    900
    >>> c.total_par(TeeMarker.Gold)
    8
    >>> len(c.holes)
    2
    >>> str(c)
    'Hawaii Kai'
    >>> h1 is c.get_hole(1)
    True
    """

    def __init__(self, name, *args, **kwargs):
        super(Course, self).__init__(*args, **kwargs)
        self._name = name
        self._holes = {}

    def add_hole(self, hole_number, hole):
        self._holes[hole_number] = hole

    def get_hole(self, hole_number):
        return self._holes[hole_number] if hole_number in self._holes else None

    @property
    def holes(self):
        return self._holes.values()

    @property
    def name(self):
        return self._name

    def total_distance(self, tee_marker):
        return sum([hole.get_tee(tee_marker).distance for hole in self.holes])

    def total_par(self, tee_marker):
        return sum([hole.get_tee(tee_marker).par for hole in self.holes])

    def __str__(self):
        return self.name


# vim: filetype=python
