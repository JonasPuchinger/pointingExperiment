#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

class PointingTechnique():

    def __init__(self):
        pass

    def filter(self, curr_cursor_pos, curr_targets):
        distances_to_targets = []
        return distances_to_targets[0]

    def get_distance(self, cursor, target):
        return math.sqrt(
            abs(cursor[0] - target[0]) ** 2 +
            abs(cursor[1] - target[1]) ** 2
        )

pt = PointingTechnique()
print(pt.get_distance((50, 50), (90, 90)))