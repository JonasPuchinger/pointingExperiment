#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import random
import math
import itertools
import os
import csv
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
        self.elapsed_distance = 0
        self.mouse_location = (0, 0)
        self.mouse_moving = False
        self.right_target_clicked = False
        self.create_targets()
        self.current_targets = []

    def create_targets(self):
        self.targets = []
        self.append_pointing_technique = []
        for width in self.widths:
            for i in range(10):
                targets = [
                    (random.randrange(width, (self.width/2-width), 1),
                     random.randrange(width, (self.height/2-width), 1), width),
                    (random.randrange(width, (self.width/2-width), 1),
                     -random.randrange(width, (self.height/2-width), 1), width),
                    (-random.randrange(width, (self.width/2-width), 1),
                     random.randrange(width, (self.height/2-width), 1), width),
                    (-random.randrange(width, (self.width/2-width), 1),
                     -random.randrange(width, (self.height/2-width), 1), width)
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
                    self.log_csv(self.stop_measurement(), click_offset)
                    self.elapsed += 1

                    if num == 3:
                        self.right_target_clicked = True
                    else:
                        self.right_target_clicked = False
        else:
            self.elapsed += 1

        self.save_mouse_location(event)

    def save_mouse_location(self, event):
        if self.elapsed_distance != self.elapsed:
            self.mouse_location = (event.x(), event.y())
            self.elapsed_distance += 1

    def log_csv(self, time, click_offset):
        file_name = 'pointing_experiment_results.csv'
        x_distance, y_distance, width = self.current_target()[3]
        ellipse = self.current_targets[3]
        target_distance = math.sqrt((ellipse.center().x() - self.mouse_location[0]) ** 2 +
                                    (ellipse.center().y() - self.mouse_location[1]) ** 2)
        res = [self.user_id, self.elapsed,  self.append_pointing_technique[self.elapsed-1],
               width, click_offset[0], click_offset[1], self.right_target_clicked, x_distance, y_distance,
               time, target_distance, self.timestamp()]

        if not os.path.isfile("./"+file_name):
            # https://realpython.com/python-csv/
            with open(file_name, 'w', newline='') as result_file:
                fieldnames = [
                    'Participant_ID',
                    'Count',
                    'Pointing_Technique',
                    'Width',
                    'Click_Offset_X',
                    'Click_Offset_Y',
                    'Right_Target_Clicked',
                    'X_Distance',
                    'Y_Distance',
                    'Time',
                    'Target_Distance',
                    "Timestamp"
                ]
                file_writer = csv.DictWriter(result_file, fieldnames=fieldnames)
                file_writer.writeheader()
                file_writer.writerow({fieldnames[0]: res[0],
                                      fieldnames[1]: res[1],
                                      fieldnames[2]: res[2],
                                      fieldnames[3]: res[3],
                                      fieldnames[4]: res[4],
                                      fieldnames[5]: res[5],
                                      fieldnames[6]: res[6],
                                      fieldnames[7]: res[7],
                                      fieldnames[8]: res[8],
                                      fieldnames[9]: res[9],
                                      fieldnames[10]: res[10],
                                      fieldnames[11]: res[11]
                                      })
        else:
            # https://stackoverflow.com/questions/2363731/append-new-row-to-old-csv-file-python
            with open(file_name, 'a') as result_file:
                fields = res
                file_writer = csv.writer(result_file)
                file_writer.writerow(fields)

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