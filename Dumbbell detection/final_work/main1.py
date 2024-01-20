import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtGui                     #利用PyQt5,构建了GUI界面，方便用户的使用。
from GUI import Ui_MainWindow               #引入GUI文件
import mediapipe as mp                      #引入mediapipe
import pandas as pd
import numpy as np
import cv2

mp_drawing = mp.solutions.drawing_utils #作为一个模块，可以首先为该模块创建一个别名
mp_pose = mp.solutions.pose  # 姿态识别方法，创建一个别名

def calculate_angle(a, b, c):#用到的计算三角点角度的函数
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def detection_body_part(landmarks, body_part_name):#检测身体部位坐标，名称函数
    return [
        landmarks[mp_pose.PoseLandmark[body_part_name].value].x,
        landmarks[mp_pose.PoseLandmark[body_part_name].value].y,
        landmarks[mp_pose.PoseLandmark[body_part_name].value].visibility
    ]


def detection_body_parts(landmarks):#检测身体部位坐标，将其转化为数组表格DataFrame
    body_parts = pd.DataFrame(columns=["body_part", "x", "y"])

    for i, lndmrk in enumerate(mp_pose.PoseLandmark):
        lndmrk = str(lndmrk).split(".")[1]
        cord = detection_body_part(landmarks, lndmrk)
        body_parts.loc[i] = lndmrk, cord[0], cord[1]

    return body_parts

class BodyPartAngle:#计算身体各角度的类
    def __init__(self, landmarks):
        self.landmarks = landmarks   #用所给坐标初始化

    def angle_of_the_left_arm(self):  #计算左臂的角度
        l_shoulder = detection_body_part(self.landmarks, "LEFT_SHOULDER")
        l_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        l_wrist = detection_body_part(self.landmarks, "LEFT_WRIST")
        return calculate_angle(l_shoulder, l_elbow, l_wrist)

    def angle_of_the_right_arm(self): #计算右臂的角度
        r_shoulder = detection_body_part(self.landmarks, "RIGHT_SHOULDER")
        r_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        r_wrist = detection_body_part(self.landmarks, "RIGHT_WRIST")
        return calculate_angle(r_shoulder, r_elbow, r_wrist)

    def angle_of_the_left_shoulder(self):#计算左肩的角度
        l_hip = detection_body_part(self.landmarks, "LEFT_HIP")
        l_shoulder = detection_body_part(self.landmarks, "LEFT_SHOULDER")
        l_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        return calculate_angle(l_hip, l_shoulder, l_elbow)

    def angle_of_the_right_shoulder(self):#计算右肩的角度
        r_hip = detection_body_part(self.landmarks, "RIGHT_HIP")
        r_shoulder = detection_body_part(self.landmarks, "RIGHT_SHOULDER")
        r_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        return calculate_angle(r_hip, r_shoulder, r_elbow)

class TypeOfExercise(BodyPartAngle):  #选择各运动的类型
    def __init__(self, landmarks):
        super().__init__(landmarks)

    def right_side(self, counter, status, avg_score): #右侧的屈伸哑铃动作
        right_arm_angle = self.angle_of_the_right_arm()
        standard = [22, 40]   #标准分，经过不断尝试得出
        standard_sum = 2 * sum(standard)

        if status:
            if  right_arm_angle < 40: #小于40度时计数一次
                counter += 1
                status = False
            avg_score =min(max(0,( 1- abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100),98) #平滑实现标准分
        else:
            if right_arm_angle > 140:
                status = True
            avg_score =min(max(0,( 1- abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100),98) #平滑实现标准分

        return [counter, status, avg_score]


    def both_sides(self, counter, status, avg_score): #两侧同时屈伸哑铃
        right_arm_angle = self.angle_of_the_right_arm()
        left_arm_angle = self.angle_of_the_left_arm()
        standard = [13, 40]   #标准分，经过不断尝试得出
        standard_sum = 2 * sum(standard)

        if status:
            if  right_arm_angle < 40 and left_arm_angle < 40:
                counter += 1
                status = False
            right_score = ( 1- abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100
            left_score = ( 1- abs((self.angle_of_the_left_arm() - standard[0]) / standard_sum)) * 100
            avg_score=min(max(0,(right_score + left_score)/2),98)#两侧同时锻炼时，分数取平均
        else:
            if right_arm_angle > 140 and left_arm_angle > 140:
                status = True
            right_score = ( 1- abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100
            left_score = ( 1- abs((self.angle_of_the_left_arm() - standard[0]) / standard_sum)) * 100
            avg_score=min(max(0,(right_score + left_score)/2),98)#两侧同时锻炼时，分数取平均
        return [counter, status, avg_score]




    def push_upwards(self, counter, status, avg_score):#向上推举
        nose = detection_body_part(self.landmarks, "NOSE")
        left_elbow = detection_body_part(self.landmarks, "LEFT_ELBOW")
        right_elbow = detection_body_part(self.landmarks, "RIGHT_ELBOW")
        avg_shoulder_y = (left_elbow[1] + right_elbow[1]) / 2

        standard = [20,40]
        standard_sum = 2 * sum(standard)

        if status:
            if nose[1] > avg_shoulder_y:
                counter += 1
                status = False
            left_arm_score = (1 - abs((self.angle_of_the_left_arm() - standard[0]) / standard_sum)) * 100
            right_arm_score = (1 - abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100
            left_shoulder_score = (1 - abs((self.angle_of_the_left_shoulder() - standard[1]) / standard_sum)) * 100
            right_shoulder_score = (1 - abs((self.angle_of_the_right_shoulder() - standard[1]) / standard_sum)) * 100
            avg_score = 100-(left_arm_score + right_arm_score + left_shoulder_score + right_shoulder_score) / 4 #角度合适，并且肘部举过鼻子下方，记一次
        else:
            if nose[1] < avg_shoulder_y:
                status = True
            avg_score = 100

        return [counter, status, avg_score]




    def calculate_exercise(self, exercise_type, counter, status, avg_score):     #传值，UI中选项传给后端做判断
        if exercise_type == "both sides":
            counter, status, avg_score = TypeOfExercise(self.landmarks).both_sides(
                counter, status, avg_score)
        elif exercise_type == "right side":
            counter, status, avg_score = TypeOfExercise(self.landmarks).right_side(
                counter, status, avg_score)
        elif exercise_type == "push upwards":
            counter, status, avg_score = TypeOfExercise(self.landmarks).push_upwards(
                counter, status, avg_score)

        return [counter, status, avg_score]

    def score_table(self, exercise, counter, status, avg_score, isPause):       #显示到前端UI的分数框内
        score_table = cv2.imread("images/5.png")
        cv2.putText(score_table, "Activity : " + exercise.replace("-", " "),
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2,
                    cv2.LINE_AA)#显示到前端UI的分数框内
        cv2.putText(score_table, "Counter : " + str(counter), (10, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)#显示到计数的分数框内
        cv2.putText(score_table, "Status : " + str(status), (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)#显示到状态的分数框内
        if exercise == "both sides":
            cv2.putText(score_table, "Score : " + str(avg_score), (10, 370),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
            cv2.putText(score_table, "Angle of left arm : " + str(self.angle_of_the_left_arm()), (10, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
            cv2.putText(score_table, "Angle of right arm : " + str(self.angle_of_the_right_arm()), (10, 470),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)

        elif exercise == "right side":
            cv2.putText(score_table, "Score : " + str(avg_score), (10, 370),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
            cv2.putText(score_table, "Angle of right arm : " + str(self.angle_of_the_right_arm()), (10, 470),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)

        elif exercise == "push upwards":
            cv2.putText(score_table, "Score : " + str(avg_score), (10, 370),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
            cv2.putText(score_table, "Angle of left arm : " + str(self.angle_of_the_left_arm()), (10, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
            cv2.putText(score_table, "Angle of right arm : " + str(self.angle_of_the_right_arm()), (10, 470),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)

        cv2.imshow("score", score_table)

class ScoreThread(QThread):#该类实现的功能是控制视频展示中内容，进行标点、画出帧率、计数等信息
    sinOut = pyqtSignal(QImage)
    scoreSignal = pyqtSignal(str)

    def __init__(self, mw, exercise_type):#初始化
        super(ScoreThread, self).__init__()
        self.cond = QWaitCondition()
        self._isPause = False
        self.mutex = QMutex()
        self.mw = mw
        self.exercise_type = exercise_type

    def pause(self):#停止按钮后触发函数
        self._isPause = True

    def run(self):#UI界面中视频展示部分中的显示设置
        prevTime = 0
        with mp_pose.Pose(min_detection_confidence=0.5,
                          min_tracking_confidence=0.5) as pose:
            counter = 0
            status = True
            avg_score = 0
            self.mutex.lock()
            while self.mw.cap.isOpened():
                ret, frame = self.mw.cap.read()
                nchannel = frame.shape[2]

                frame = cv2.resize(frame, (1200, 680), interpolation=cv2.INTER_AREA)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                results = pose.process(frame)
                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                try:
                    landmarks = results.pose_landmarks.landmark
                    counter, status, avg_score = TypeOfExercise(landmarks).calculate_exercise(
                        self.exercise_type, counter, status, avg_score)#执行calculate_exercise函数
                except:
                    pass

                TypeOfExercise(landmarks).score_table(self.exercise_type, counter, status, avg_score, self._isPause)
                self.scoreSignal.emit(str(avg_score))#执行显示分数的函数

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
                )#画点
                currTime = time.time()
                fps = 1 / (currTime - prevTime)
                prevTime = currTime
                cv2.putText(frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 6)
                cv2.putText(frame, str(counter), (45, 670), cv2.FONT_HERSHEY_PLAIN, 15,(126, 12, 110), 25)

                per = np.interp(avg_score, (10,98), (0, 100))
                bar = np.interp(avg_score, (10,98), (650, 100))
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
                            color, 3)#画出进度条，计数器，帧率等内容

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
            cv2.destroyAllWindows()


class myMainWindow(QMainWindow):#该类的方法用于在GUI上，连接调用函数，计算出内容返回到界面。
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
        self.ui.btn_file.clicked.connect(self.openfile)
        self.ui.btn_camera.clicked.connect(self.opencam)
        self.ui.right_side.clicked.connect(self.rightside)
        self.ui.push_upwards.clicked.connect(self.pushupwards)
        self.ui.both_sides.clicked.connect(self.bothsides)
        self.ui.tabWidget.currentChanged[int].connect(self.function)
        self.setMinimumSize(700, 1100)


    def openfile(self):#对文件中的动作进行识别
        filename, filetype = QFileDialog.getOpenFileName(self, "Select Video", "", "All Files(*)")
        self.cap = cv2.VideoCapture(filename)

        self.thread0 = ScoreThread(self, self.exercise_type)

        if self.func == 0:
            if self.exercise_type is None:
                QMessageBox.warning(self, '警告', '未选择锻炼类型')
            else:
                self.thread0.start()
                self.ui.btn_pause.clicked.connect(self.thread0.pause)
        elif self.func == 2:
            self.thread2.start()
            self.ui.btn_pause.clicked.connect(self.thread2.pause)

    def opencam(self):#打开摄像头进行识别
        self.cap = cv2.VideoCapture(0)
        self.thread0 = ScoreThread(self, self.exercise_type)
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

    def rightside(self):
        self.exercise_type = "right side"

    def pushupwards(self):
        self.exercise_type = "push upwards"

    def bothsides(self):
        self.exercise_type = "both sides"


def main1():   #主函数调用
    app = QApplication(sys.argv)
    my_gui = myMainWindow()
    my_gui.show()
    app.exec_()

if __name__ == '__main__':
    main1()