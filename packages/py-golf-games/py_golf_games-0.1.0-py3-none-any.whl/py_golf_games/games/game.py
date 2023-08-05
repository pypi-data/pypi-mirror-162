#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc


class Game(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, players, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        self._name = name
        self._players = {}
        for player in players:
            self._players[player] = player

    @property
    def name(self):
        return self._name

    @property
    def players(self):
        return self._players.values()

    @property
    def is_participating(self, player):
        return player in self._players.values()

    @abc.abstractmethod
    def pre_round(self):
        raise NotImplementedError

    @abc.abstractmethod
    def pre_hole(self):
        raise NotImplementedError

    @abc.abstractmethod
    def at_turn(self):
        raise NotImplementedError

    @abc.abstractmethod
    def post_hole(self):
        raise NotImplementedError

    @abc.abstractmethod
    def post_round(self):
        raise NotImplementedError


# vim: filetype=python
