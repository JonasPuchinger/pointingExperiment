#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import random
import numpy
import math
import itertools
import pointing_technique
from PyQt5 import QtGui, QtWidgets, QtCore


class PointingExperimentModel(object):

    def __init__(self, user_id, repetitions, widths, x_distances, y_distances, width, height):
        self.timer = QtCore.QTime()
        self.user_id = user_id
        self.repetitions = repetitions
        self.widths = widths
        self.width = width
        self.height = height
        self.x_distances = x_distances
        self.y_distances = y_distances
        self.elapsed = 0
        self.mouse_moving = False
        self.right_target_clicked = False
        self.create_targets()
        self.current_targets = []

    def create_targets(self):
        self.targets = []
        self.append_pointing_technique = []
        for width in self.widths:
            for i in range(10):
                ran_x = random.randrange(width, (self.width/2-width), 1)
                ran_y = random.randrange(width, (self.height/2-width), 1)
                targets = [
                    (ran_x, ran_y, width),
                    (ran_x, -ran_y, width),
                    (-ran_x, ran_y, width),
                    (-ran_x, -ran_y, width)
                ]

                if i%2 == 0:
                    apt = True
                else:
                    apt = False
                self.append_pointing_technique.append(apt)

                random.shuffle(targets)
                self.targets.append(targets),

        connected_list = list(zip(self.targets, self.append_pointing_technique))
        random.shuffle(connected_list)
        self.targets, self.append_pointing_technique = zip(*connected_list)

    def current_target(self):
        if self.elapsed > len(self.targets) or self.elapsed == 0:
            return None
        else:
            return self.targets[self.elapsed-1]

    # def click_log():
    #     pass

    # @click_log
    def check_click(self, event):
        if self.elapsed != 0:
            for num, ellipse in enumerate(self.current_targets):
                if ellipse.contains(event.pos()):
                    click_offset = (ellipse.center().x()-event.x(), ellipse.center().y()-event.y())
                    self.log_time(self.stop_measurement(), click_offset)
                    self.elapsed += 1

                    if num == 3:
                        self.right_target_clicked = True
                    else:
                        self.right_target_clicked = False
        else:
            self.elapsed += 1

    def log_time(self, time, click_offset):
        x_distance, y_distance, width = self.current_target()[3]
        print("%s; %s; %d; %d; %d; %d; %d; %d; %d; %s" % (
            self.timestamp(),
            self.user_id,
            self.elapsed,
            x_distance,
            y_distance,
            width,
            time,
            click_offset[0],
            click_offset[1],
            self.right_target_clicked))

    def start_measurement(self):
        self.timer.start()

    def stop_measurement(self):
        return self.timer.elapsed()

    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)


class PointingExperiment(QtWidgets.QWidget):

    def __init__(self, model, width, height):
        super(PointingExperiment, self).__init__()
        self.model = model
        self.size = (width, height)
        self.start_pos = (width/2, height/2)
        self.initUI()
        self.tq = pointing_technique.PointingTechnique(self)

    def initUI(self):
        self.text = "Please click on the green target \n" \
                    "Click to start"
        self.setGeometry(0, 0, self.size[0], self.size[1])
        self.setWindowTitle('Pointing Experiment')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.model.check_click(ev)
            self.text = ""
            self.update()

    def mouseMoveEvent(self, ev):
        if self.model.elapsed != 0:
            if self.model.append_pointing_technique[self.model.elapsed-1]:
                self.tq.set_mouse(ev, self.model.current_targets, [i[2] for i in self.model.current_target()])
            self.update()
    
    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        self.drawTargets(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)

    def target_pos(self, x_distance, y_distance):
        x = self.start_pos[0] + x_distance
        y = self.start_pos[1] + y_distance
        return x, y

    def drawTargets(self, event, qp):
        self.model.current_targets = []
        if self.model.current_target() is not None:
            for i, target in enumerate(self.model.current_target()):
                self.drawTarget(qp, target, i)
                self.model.start_measurement()

        elif self.model.elapsed != 0:
            sys.stderr.write("no targets left...")
            sys.exit(1)

    def drawTarget(self, qp, target, index):
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
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    model = PointingExperimentModel(*parse_setup(sys.argv[1]), width, height)
    fitts_law_test = PointingExperiment(model, width, height)
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