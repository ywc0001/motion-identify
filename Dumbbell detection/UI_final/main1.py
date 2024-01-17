import os
import time
import joblib
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
from myGUI import Ui_MainWindow
import sys
import numpy as np
import cv2
from PoseModel.utils import *
from PoseModel.anglecom import *
import mediapipe as mp
from PoseModel.exercisetypes import TypeOfExercise


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


class ScoreThread(QThread):
    sinOut = pyqtSignal(QImage)
    scoreSignal = pyqtSignal(str)

    def __init__(self, mw, exercise_type):
        super(ScoreThread, self).__init__()
        self.cond = QWaitCondition()
        self._isPause = False
        self.mutex = QMutex()
        self.mw = mw
        self.exercise_type = exercise_type

    def pause(self):
        self._isPause = True

    def run(self):
        prevTime = 0
        with mp_pose.Pose(min_detection_confidence=0.5,
                          min_tracking_confidence=0.5) as pose:
            counter = 0  # movement of exercise
            status = True  # state of move
            avg_score = 0
            self.mutex.lock()
            while self.mw.cap.isOpened():
                ret, frame = self.mw.cap.read()
                nchannel = frame.shape[2]

                frame = cv2.resize(frame, (1200, 680), interpolation=cv2.INTER_AREA)
                # recolor frame to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                # make detection
                results = pose.process(frame)
                # recolor back to BGR
                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                try:
                    landmarks = results.pose_landmarks.landmark
                    counter, status, avg_score = TypeOfExercise(landmarks).calculate_exercise(
                        self.exercise_type, counter, status, avg_score)
                except:
                    pass

                TypeOfExercise(landmarks).score_table(self.exercise_type, counter, status, avg_score, self._isPause)
                self.scoreSignal.emit(str(avg_score))

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 255, 255),
                                           thickness=2,
                                           circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0,255,0),
                                           thickness=2,
                                           circle_radius=2),
                )
                currTime = time.time()
                fps = 1 / (currTime - prevTime)
                prevTime = currTime
                cv2.putText(frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 6)
                cv2.putText(frame, str(counter), (45, 670), cv2.FONT_HERSHEY_PLAIN, 15,(126, 12, 110), 25)

                per = np.interp(avg_score, (0,100), (0, 100))
                bar = np.interp(avg_score, (0,100), (650, 100))
                count = 0
                dir = 0

                color = (126, 12, 110)
                if per == 100:
                    color = (0, 255, 0)
                    if dir == 0:
                        count += 0.5
                        dir = 1
                if per == 0:
                    color = (0, 255, 0)
                    if dir == 1:
                        count += 0.5
                        dir = 0

                cv2.rectangle(frame, (1100, 100), (1175, 650), color, 3)
                cv2.rectangle(frame, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
                cv2.putText(frame, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 2.5,
                            color, 3)

                frameHeight = frame.shape[0]
                frameWidth = frame.shape[1]
                a = self.mw.ui.video.size()
                if a.width() / frameWidth < a.height() / frameHeight:
                    scaleFactor = a.width() / frameWidth
                else:
                    scaleFactor = 1.0 * a.height() / frameHeight

                timg = cv2.resize(frame, (int(scaleFactor * frame.shape[1]), int(scaleFactor * frame.shape[0])))
                timg = cv2.cvtColor(timg, cv2.COLOR_BGR2RGB)
                limage = QtGui.QImage(timg.data, timg.shape[1], timg.shape[0], nchannel * timg.shape[1],
                                      QtGui.QImage.Format_RGB888)
                self.mw.ui.video.setPixmap(QtGui.QPixmap(limage))
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                if self._isPause:
                    break
                    #self.cond.wait(self.mutex)
            cv2.destroyAllWindows()
            #self.msleep(1000)
            #self.mutex.unlock()


class myMainWindow(QMainWindow):
    signalImage = pyqtSignal(QImage)

    def __init__(self):
        super(myMainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.image = None
        self.cap = None
        self.exercise_type = None
        self.track_type = 0
        self.func = 0
        # self.btn_ext.clicked.connect(self.exit)
        self.ui.btn_file.clicked.connect(self.openfile)
        self.ui.btn_camera.clicked.connect(self.opencam)
        self.ui.pull_up.clicked.connect(self.pullup)
        self.ui.sit_up.clicked.connect(self.situp)
        self.ui.push_up.clicked.connect(self.pushup)
        self.ui.tabWidget.currentChanged[int].connect(self.function)
        self.setMinimumSize(700, 1100)


    def openfile(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "Select Video", "", "All Files(*)")
        self.cap = cv2.VideoCapture(filename)

        self.thread0 = ScoreThread(self, self.exercise_type)

        # self.btn_ok.clicked.connect(self.t.resume)
        # self.thread.scoreSignal.connect(self.Change)
        # self.t.sinOut.connect(self.updatalabel)
        if self.func == 0:
            if self.exercise_type is None:
                QMessageBox.warning(self, '警告', '未选择锻炼类型')
            else:
                self.thread0.start()
                self.ui.btn_pause.clicked.connect(self.thread0.pause)
        elif self.func == 2:
            self.thread2.start()
            self.ui.btn_pause.clicked.connect(self.thread2.pause)

    def opencam(self):
        self.cap = cv2.VideoCapture(0)
        self.thread0 = ScoreThread(self, self.exercise_type)
        # self.t.scoreSignal.connect(self.Change)
        if self.func == 0:
            if self.exercise_type is None:
                QMessageBox.warning(self, '警告', '未选择锻炼类型')
            else:
                self.thread0.start()
                self.ui.btn_pause.clicked.connect(self.thread0.pause)
        elif self.func == 1:
            if self.track_type == 0:
                QMessageBox.warning(self, '警告', '未选择锻炼类型')
            if self.track_type == 1:
                self.thread1.start()
                self.thread3.start()
            elif self.track_type == 2:
                self.thread5.start()
                self.ui.btn_pause.clicked.connect(self.thread5.pause)
            elif self.track_type == 4:
                self.thread4.start()
                self.ui.btn_pause.clicked.connect(self.thread4.pause)
        elif self.func == 2:
            self.thread2.start()
            self.ui.btn_pause.clicked.connect(self.thread2.pause)

    def function(self, index):
        self.func = index

    def passImage(self, image):
        self.image = image
        self.signalImage.emit(self.image)

    def exit(self):
        self.close()

    def Change(self, msg):
        self.label.setText("Score : " + str(msg))

    def pullup(self):
        self.exercise_type = "right side"

    def situp(self):
        self.exercise_type = "push upwards"

    def pushup(self):
        self.exercise_type = "both sides"



def main1():
    app = QApplication(sys.argv)
    my_gui = myMainWindow()
    my_gui.show()
    app.exec_()

if __name__ == '__main__':
    main1()