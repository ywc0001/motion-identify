import cv2
import numpy as np
import time
import PoseModule as pm

'''
右臂哑铃
思路：检测大小臂形成的角度
'''
# 创建捕获视频的变量，捕获并初始化摄像头
# 默认值为-1，表示随机选取一个摄像头。如果电脑有多个摄像头，则用数字0表示第一个，用数字1表示第二个。如果电脑只有一个摄像头，既可以用0，也可以用-1来作为摄像头的ID号。
cap = cv2.VideoCapture(0)
# PoseDetector 类估计人体的姿势点
detector = pm.poseDetector()
# 哑铃次数
count = 0
# 运动方向，0上升，1下降，0-1或1-0为一次完整动作
dir = 0
# previoustime,后面用于计算帧率
pTime = 0
while True:
    # 一帧一帧地读取图像，返回一个布尔值给sucess(True/False)。如果帧读取的是正确的, 就是True
    success, img = cap.read()
    # 指定图像大小，固定长1280px,宽720px
    img = cv2.resize(img, (1280, 720))
    # 读取图像姿势，不绘制pose，返回值：处理后的图像img
    img = detector.findPose(img, False)
    # 读取图像姿势，不绘制pose，返回一系列三维坐标值：self.lmList：人体特征点信息；self.bboxInfo：人体边界框信息
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:
        # 右臂：点12,14,16
        # p1：点1；p2：点2；p3：点3，返回值：计算出 p1p2 与 p2p3 之间的角度值 Angle [0, 360)
        angle = detector.findAngle(img, 12, 14, 16)
        # 左臂
        # angle = detector.findAngle(img, 11, 13, 15,False)
        # 对得到的角度插值处理，将范围转变为百分比（0-100）
        per = np.interp(angle, (210, 310), (0, 100))
        # 此处100为最大值
        bar = np.interp(angle, (220, 310), (650, 100))
        # print(angle, per)

        # Check for the dumbbell curls
        color = (255, 0, 255)
        # 运动次数计算
        if per == 100:
            # 进度条变紫色
            color = (0, 255, 0)
            if dir == 0:
                count += 0.5
                dir = 1
        if per == 0:
            color = (0, 255, 0)
            if dir == 1:
                count += 0.5
                dir = 0
        print(count)

        # 右侧进度条，以百分比显示
        cv2.rectangle(img, (1100, 100), (1175, 650), color, 3)
        cv2.rectangle(img, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
        cv2.putText(img, f'{int(per)} %', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                    color, 4)

        # 左上角文字计数
        cv2.rectangle(img, (0, 450), (250, 720), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (45, 670), cv2.FONT_HERSHEY_PLAIN, 15,
                    (255, 0, 0), 25)

    cTime = time.time()
    # 帧率
    fps = 1 / (cTime - pTime)
    pTime = cTime
    #绘制帧率文本，org：文字在图像中的左下角坐标
    cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5,
                (255, 0, 0), 5)

    # 绘制摄像头捕获的图像
    cv2.imshow("Image", img)
    # 等待一毫秒继续执行
    cv2.waitKey(1)
