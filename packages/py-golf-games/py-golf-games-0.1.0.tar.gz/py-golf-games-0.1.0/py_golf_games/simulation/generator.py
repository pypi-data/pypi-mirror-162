#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..course import Course
from ..hole import Hole
from ..player import Player
from ..player import Gender
from ..round import Round
from ..tee import Tee
from ..tee import TeeMarker
import random


class CourseGenerator(object):
    @classmethod
    def generate(cls, name, num_holes):
        course = Course(name)
        for hole_number in range(1, num_holes + 1):
            hole = HoleGenerator.generate(hole_number)
            course.add_hole(hole_number, hole)
        return course


class HoleGenerator(object):
    @classmethod
    def generate(cls, hole_number):
        tees = TeesGenerator.generate()
        return Hole(hole_number, tees)


class TeesGenerator(object):
    @classmethod
    def generate(cls):
        tees = {}
        for marker in list(TeeMarker):
            tee = TeeGenerator.generate(marker)
            tees[marker] = tee
        return tees


class TeeGenerator(object):
    @classmethod
    def generate(cls, tee_marker):
        par = random.randint(3, 5)
        distance = random.randrange(250, 550, 50)
        return Tee(tee_marker, par, distance)


class PlayersGenerator(object):
    @classmethod
    def _random_name(cls):
        return "Player " + str(int(random.random() * 1024))

    @classmethod
    def _random_gender(cls):
        return random.choice(list(Gender))

    @classmethod
    def generate(cls, max_players=4):
        players = []
        for x in range(random.randint(1, max_players)):
            players.append(Player(cls._random_name(), cls._random_gender()))
        return players


class RoundGenerator(object):
    @classmethod
    def generate(cls, course, players):
        round = Round(course, players)

        for player in players:
            for hole in range(1, len(course.holes) + 1):
                strokes = random.randint(3, 10)
                round.record_score(player, hole, strokes)

        return round


# vim: filetype=python
