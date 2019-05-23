#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import random
import math
import itertools
from PyQt5 import QtGui, QtWidgets, QtCore

class PointingExperimentModel(object):

    def __init__(self, user_id, repetitions, widths, x_distances, y_distances):
        self.timer = QtCore.QTime()
        self.user_id = user_id
        self.repetitions = repetitions
        self.widths = widths
        self.x_distances = x_distances
        self.y_distances = y_distances
        self.elapsed = 0
        self.mouse_moving = False
        self.create_targets()
        self.current_targets = []

    def create_targets(self):
        targets_1 = list(itertools.product(self.x_distances[0], self.y_distances[0], self.widths))
        targets_2 = list(itertools.product(self.x_distances[1], self.y_distances[1], self.widths))
        targets_3 = list(itertools.product(self.x_distances[2], self.y_distances[2], self.widths))
        targets_4 = list(itertools.product(self.x_distances[3], self.y_distances[3], self.widths))
        random.shuffle(targets_1)
        random.shuffle(targets_2)
        random.shuffle(targets_3)
        random.shuffle(targets_4)
        self.targets = list(zip(targets_1, targets_2, targets_3, targets_4))
    
    def current_target(self):
        if self.elapsed >= len(self.targets):
            return None
        else:
            return self.targets[self.elapsed]

    # def click_log():
    #     pass

    # @click_log
    def register_click(self, target_pos, click_pos):
        dist = math.sqrt((target_pos[0] - click_pos[0]) * (target_pos[0] - click_pos[0]) +
                         (target_pos[1] - click_pos[1]) * (target_pos[1] - click_pos[1]))
        target_dist = math.sqrt(self.current_target()[3][0] ** 2 +
                                self.current_target()[3][1] ** 2)
        if dist > target_dist:
            return False
        else:
            click_offset = (target_pos[0] - click_pos[0], target_pos[1] - click_pos[1])
            self.log_time(self.stop_measurement(), click_offset)
            self.elapsed += 1
            return True

    def check_click(self, event):
        for num, ellipse in enumerate(self.current_targets):
            if ellipse.contains(event.pos()):
                #TODO
                #calculate offset if necessary
                click_offset = (0 ,0)
                self.log_time(self.stop_measurement(), click_offset)
                self.elapsed += 1

                if num == 3:
                    print("Clicked right bubble...")
                else:
                    print("Clicked wrong bubble...")

                return True
        print("Clicked no bubble...")
        return False

    def log_time(self, time, click_offset):
        x_distance, y_distance, width = self.current_target()[3]
        print("%s; %s; %d; %d; %d; %d; %d; %d; %d" % (self.timestamp(), self.user_id, self.elapsed, x_distance, y_distance, width, time, click_offset[0], click_offset[1]))

    def start_measurement(self):
        if not self.mouse_moving:
            self.timer.start()
            self.mouse_moving = True

    def stop_measurement(self):
        if self.mouse_moving:
            elapsed = self.timer.elapsed()
            self.mouse_moving = False
            return elapsed
        else:
            return -1

    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

class PointingExperiment(QtWidgets.QWidget):

    def __init__(self, model):
        super(PointingExperiment, self).__init__()
        self.model = model
        self.start_pos = (960, 400)
        self.initUI()

    def initUI(self):
        self.text = "Please click on the target"
        self.setGeometry(0, 0, 1920, 800)
        self.setWindowTitle('Pointing Experiment')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
        self.setMouseTracking(True)
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            hit = self.model.check_click(ev)
            if hit:
                QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(self.start_pos[0], self.start_pos[1])))
            self.update()

    def mouseMoveEvent(self, ev):
        if (abs(ev.x() - self.start_pos[0]) > 5) or (abs(ev.y() - self.start_pos[1]) > 5):
            self.model.start_measurement()
            self.update()
    
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawBackground(event, qp)
        self.drawText(event, qp)
        self.drawTargets(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        self.text = "%d / %d (%05d ms)" % (self.model.elapsed, len(self.model.targets), self.model.timer.elapsed())
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def target_pos(self, x_distance, y_distance):
        x = self.start_pos[0] + x_distance
        y = self.start_pos[1] + y_distance
        return (x, y)

    def drawBackground(self, event, qp):
        if self.model.mouse_moving:
            qp.setBrush(QtGui.QColor(220, 190, 190))
        else:
            qp.setBrush(QtGui.QColor(200, 200, 200))
        qp.drawRect(event.rect())

    def drawTargets(self, event, qp):
        self.model.current_targets = []
        if self.model.current_target() is not None:
            for i, target in enumerate(self.model.current_target()):
                self.drawTarget(event, qp, target, i)
        else:
            sys.stderr.write("no targets left...")
            sys.exit(1)

    def drawTarget(self, event, qp, target, index):
        x_distance, y_distance, width = target
        x, y = self.target_pos(x_distance, y_distance)

        if index <= 2:
            qp.setBrush(QtGui.QColor(200, 34, 20))
        else:
            qp.setBrush(QtGui.QColor(20, 200, 150))

        ellipse = QtCore.QRect(x - width / 2, y - width / 2, width, width)
        self.model.current_targets.append(ellipse)
        qp.drawEllipse(ellipse)


def main():
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: %s <setup file>\n" % sys.argv[0])
        sys.exit(1)
    model = PointingExperimentModel(*parse_setup(sys.argv[1]))
    fitts_law_test = PointingExperiment(model)
    sys.exit(app.exec_())


def parse_setup(filename):
    with open(filename) as f:
        contents = json.load(f)
    user_id = contents['user_id']
    repetitions = contents['repetitions']
    widths = contents['widths']
    x_distances = contents['x_distances']
    y_distances = contents['y_distances']
    return user_id, repetitions, widths, x_distances, y_distances

if __name__ == '__main__':
    main()