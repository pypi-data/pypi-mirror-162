#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GameEngine(object):
    def __init__(self, round, *args, **kwargs):
        super(GameEngine, self).__init__(*args, **kwargs)
        self._round = round
        self._games = []

    def enable_game(self, player, game):
        self._games.append(game)


# vim: filetype=python
