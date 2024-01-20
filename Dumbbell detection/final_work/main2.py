import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton,QLabel
from PyQt5.QtGui import QFont,QIcon
from PyQt5.QtCore import Qt
import cv2
import mediapipe as mp
import math
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.resize(1500, 1000)
        self.setWindowTitle('仰卧起坐、俯卧撑、深蹲、引体向上部分')

        self.label1 = QLabel(self)
        self.label1.setText("<font color=white>体育强则中国强，国运兴则体育兴。&emsp;---习近平 </font>")
        self.label1.setAutoFillBackground(True)
        self.label1.move(10,30)
        self.label1.setStyleSheet("background-color: rgba(126,12,110,160)")
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setFont(QFont('Arial', 27))
        self.update1()

        self.label2 = QLabel(self)
        self.label2.setText("<font color=white>摄像头状态下可按“q”键暂停退出</font>")
        self.label2.setAutoFillBackground(True)
        self.label2.move(600,650)
        self.label2.setStyleSheet("background-color: rgba(126,12,110,255)")
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setFont(QFont('Arial', 10))
        self.update2()

        self.setWindowIcon(QIcon("images/2.2.png"))
        self.button1 = QPushButton('仰卧起坐', self)
        self.button1.setStyleSheet(
            '''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button1.setFont(QFont('Arial', 15))
        self.button1.setGeometry(QtCore.QRect(150, 700, 200, 100))
        self.button1.clicked.connect(self.clickButton1)
        self.button2 = QPushButton('俯卧撑', self)
        self.button2.setStyleSheet(
            '''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button2.setFont(QFont('Arial', 15))
        self.button2.setGeometry(QtCore.QRect(500, 700, 200, 100))
        self.button2.clicked.connect(self.clickButton2)
        self.button3 = QPushButton('深蹲', self)
        self.button3.setStyleSheet(
            '''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button3.setFont(QFont('Arial', 15))
        self.button3.setGeometry(QtCore.QRect(850, 700, 200, 100))
        self.button3.clicked.connect(self.clickButton3)
        self.button4 = QPushButton('引体向上', self)
        self.button4.setStyleSheet(
            '''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.button4.setFont(QFont('Arial', 15))
        self.button4.setGeometry(QtCore.QRect(1150, 700, 200, 100))
        self.button4.clicked.connect(self.clickButton4)


    def clickButton1(self):
        trainer(11, 23, 27, 90, 170)

    def clickButton2(self):
        trainer(11, 13, 15, 60, 150)

    def clickButton3(self):
        trainer(23, 25, 27, 80, 170)

    def clickButton4(self):
        trainer(11, 13, 15, 90, 155)


    def update1(self):
        self.label1.adjustSize()

    def update2(self):
        self.label2.adjustSize()


#定义一个类，将一些同类功能模块化
class poseTool():

    def __init__(self, mode=False, upBody=False, smooth=True,detectionCon=0.5, trackCon=0.5):
        '''
        :param mode: 是否是静态图片，默认为否
        :param upBody: 是否是上半身，默认为否
        :param smooth: 设置为True减少抖动
        :param detectionCon: 人员检测模型的最小置信度值，默认为0.5
        :param trackCon: 姿势可信标记的最小置信度值，默认为0.5
        '''
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        # 创建一个Pose对象用于检测人体姿势
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth,False,self.detectionCon, self.trackCon)

    def drawPose(self, img, draw=True):
        '''
        给画面打点
        :param img: 一帧图像
        :param draw: 是否画出人体姿势节点和连接图
        :return: 处理过的图像
        '''
        #默认是不兼容的，要用cvtColor把bgr转成rgb
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # pose.process(imgRGB) 会识别这帧图片中的人体姿势数据，保存到self.results中
        self.results = self.pose.process(imgRGB)
        # 有数据时
        if self.results.pose_landmarks:
            # draw=True表示要画节点和连接图
            if draw:
                #results.pose_landmarks是画点；mpPose.POSE_CONNECTIONS是画线
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,self.mpPose.POSE_CONNECTIONS)
        return img

    def getPosition(self, img, draw=True):
        '''
        获取点的坐标并储存
        :param img: 帧图像
        :param draw: 是否画出人体姿势节点和连接图
        :return: 人体姿势数据列表
        '''
        #用于存储点的id及具体坐标
        self.lmList = []
        if self.results.pose_landmarks:
            #遍历0-32个点，获取对应坐标
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                #img的高、宽和，通道？
                h, w, c = img.shape
                #坐标
                cx, cy = int(lm.x * w), int(lm.y * h)
                #点的id及计算出的坐标存入lmlist
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)#cx,cy画红色圆点
        return self.lmList

    def calculateAngle(self, img, p1, p2, p3, draw=True):
        '''
        获取人体姿势中3个点p1-p2-p3，并计算角度
        :param img: 一帧图像
        :param p1: 第1个点
        :param p2: 第2个点
        :param p3: 第3个点
        :param draw: 是否画出3个点的连接图
        :return: 计算出来的角度
        '''
        # 获得需要的三个点的坐标（x，y）存入lmlist中
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # 计算三点之间的角度:使用函数公式获取3个点p1-p2-p3，以p2为角的角度值，0-180度之间
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        # 保证角度在0-180
        if angle < 0:
            angle = angle + 360
        if angle > 180:
            angle = 360 - angle

        # 给三个点设置不同的样式
        if draw:
            # 把(x1, y1)和 (x2, y2)之间的线改成白色，粗细为3
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            # 给x1,y1两个点设置为：大小为10的蓝色圆点，实心（filled）
            cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            # 给x1画一个大小为15的蓝圈（2）
            cv2.circle(img, (x1, y1), 15, (255, 0, 0), 2)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 0), 2)
            cv2.circle(img, (x3, y3), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (255, 0, 0), 2)
            # putText往img画面放文字；内容为angle,即计算出的角度；然后是位置字体设置等
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle


def trainer(p1, p2, p3,ag1, ag2):
    # 读取画面
    cap = cv2.VideoCapture("深蹲.mp4")
    cap.open(0)
    # cap = cv2.VideoCapture(0)
    detector = poseTool()  # 建立类poseTool的一个实例对象，命名为detector
    count = 0  # 用来记录做的个数
    dir = 0  # 记录方向
    while True:
        success, img = cap.read()  # 读取到的屏幕画面给img
        img = cv2.resize(img, (1280, 720))  # 设置img画面大小
        # 如果读取成功，显示图像
        if success:
            img = detector.drawPose(img, True)  # 调用detector实例的方法findPose,此时画面显示点、线，false效果：只留下需要的点和线，其他点线隐藏
            lmList = detector.getPosition(img, False)  # 调用detector实例的方法findPose传入lmlist，打印lmlist就会出现各个点的数值信息
            if len(lmList) != 0:
                # 调用detector实例的方法findAngle，标记p1, p2, p3三个点
                angle = detector.calculateAngle(img,  p1, p2, p3)
                # percent表示百分比，用numpy把ag1, ag2的角度转化为0-100的百分比————方便套用多个健身模式
                percent = np.interp(angle, (ag1, ag2), (0, 100))
                bar = np.interp(angle, (ag1, ag2), (650, 100))

                # 检查动作是否做完并计数
                color = (255, 0, 255)
                if percent == 100:  # percent等于100 ，方向为0，说明动作到最满标准了，可以计0.5
                    color = (0, 255, 0)
                    if dir == 0:
                        count += 0.5
                        dir = 1
                if percent == 0:  # percent等于0 ，方向为1，说明动作回到起始标准了，可以计0.5
                    color = (0, 255, 0)
                    if dir == 1:
                        count += 0.5
                        dir = 0
                # 显示计数和角度
                cv2.putText(img, "Finished: " + str(int(count)), (30, 80), cv2.FONT_HERSHEY_PLAIN, 4,(255, 0, 0), 7)
                cv2.putText(img, "Angle: " + str(int(angle)), (600, 80), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 7)

                # 显示百分比和动作条
                cv2.putText(img, f'{int(percent)} %', (1100, 80), cv2.FONT_HERSHEY_PLAIN, 3, color, 3)
                cv2.rectangle(img, (1100, 100), (1175, 650), color, 3)
                cv2.rectangle(img, (1100, int(bar)), (1175, 650), color, cv2.FILLED)

                cv2.imshow("Image", img)  # 显示画面

            # 1毫秒的延迟,mediapipe会自动降低帧率按下'q'键退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # 如果读取失败，显示错误信息并退出循环
        else:
            print("无法获取摄像头画面")
            break
    return


def main2():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.setObjectName("MainWindow")
    main.setStyleSheet("#MainWindow{border-image:url(images/2.1.jpg)}")
    main.show()
    app.exec_()


if __name__ == '__main__':
    main2()

