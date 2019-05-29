#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from PyQt5 import QtGui


class PointingTechnique():

    def __init__(self, other_self):
        self.other_self = other_self
        pass

    def set_mouse(self, ev, current_targets, widths):
        nearest_rec = self.check_for_nearest(ev, current_targets, widths)
        if nearest_rec:
            QtGui.QCursor.setPos(self.other_self.mapToGlobal(nearest_rec.center()))

    def check_for_nearest(self, ev, current_targets, widths):
        nearest = []
        for x, i in enumerate(current_targets):
            distance = math.sqrt((i.center().x() - ev.x()) ** 2 +
                                 (i.center().y() - ev.y()) ** 2) - widths[x] / 2
            if distance <= 50:
                nearest.append(i)
        if len(nearest) != 1:
            return None
        else:
            return nearest[0]
