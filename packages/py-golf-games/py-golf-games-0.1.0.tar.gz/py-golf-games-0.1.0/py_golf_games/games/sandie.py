#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .game import Game


class Sandie(Game):
    def __init__(self, *args, **kwargs):
        super(Sandie, self).__init__("Sandie", *args, **kwargs)


# vim: filetype=python
