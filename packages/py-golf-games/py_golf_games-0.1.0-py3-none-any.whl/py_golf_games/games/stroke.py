#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .game import Game


class Stroke(Game):
    def __init__(self, *args, **kwargs):
        super(Stroke, self).__init__("Stroke", *args, **kwargs)


# vim: filetype=python
