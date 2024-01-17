import cv2
import time
import practices11 as pr
import numpy as np
'''
双臂哑铃
'''

# 创建捕获视频的变量，捕获并初始化摄像头
# 默认值为-1，表示随机选取一个摄像头。如果电脑有多个摄像头，则用数字0表示第一个，用数字1表示第二个。如果电脑只有一个摄像头，既可以用0，也可以用-1来作为摄像头的ID号。

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# 后面用于计算帧率
bTime = 0
# PoseDetector类估计人体的姿势点
detector = pr.poseDetector()
# 计数
count = 0
# 运动方向，0上升，1下降，0-1或1-0为一次完整动作
rep_up=0
while True:
    # 一帧一帧地读取图像，返回一个布尔值给sucess(True/False)。如果帧读取的是正确的, 就是True
    success, image = cap.read()
    # 指定图像大小
    image = cv2.resize(image, (1280, 720))
    # 图像翻转，flipcode=0 表示绕x轴翻转；flipcode=任意正整数，比如1，2，3，表示绕y轴翻转；flipcode=任意负整数，比如-1，-2，-3，表示绕x轴和y轴同时翻转；
    # flip函数返回一个和img大小相同、类型相同的对象。
    image = cv2.flip(image, 2)
    # 读取图像姿势，不绘制pose，返回值：处理后的图像img
    image = detector.findPose(image,False)
    # 读取图像姿势，不绘制pose，返回：self.lmList：人体特征点信息；self.bboxInfo：人体边界框信息
    lmList =detector.findPosition(image,False)
    wrist = []
    if len(lmList) !=0:
        arm_r = detector.findAngle(image, 12, 14, 16)
        arm_l = detector.findAngle(image, 11, 13, 15)
        upbody_r =detector.findAngle(image,24,12,14)
        upbody_l = detector.findAngle(image, 23, 11, 13)
        per_l = np.interp(upbody_l, (235, 270), (100, 0))
        per_r = np.interp(upbody_r, (95, 124), (0, 100))
        if lmList[11][2]>lmList[14][2]:  #  khuy tay cao hon vai
            wrist.append([lmList[14][1], lmList[14][2]-detector.lenght(image,14,16)]) # ve co tay chuan ben phai
            wrist.append([lmList[13][1], lmList[13][2]-detector.lenght(image,14,16)])#ve co tay chuan trai
            angle_r = detector.cosin2goc(image,wrist[0],14,16)
            angle_l = detector.cosin2goc(image, wrist[1], 13, 15)
        # 计数
        if (per_l == 100 and per_r == 100):
            color = (255,0,255)
            if rep_up==0:
                count+=0.5
                rep_up =1
        if (per_l == 0 and per_r==0):
            color = (0, 255, 0)
            if rep_up == 1:
                count+=0.5
                rep_up = 0

        print(count)
        # 绘制计数文字
        cv2.rectangle(image, (0, 450), (250, 720), (0, 255, 0), cv2.FILLED)
        cv2.putText(image, str(int(count)), (40, 670), cv2.FONT_HERSHEY_PLAIN, 10,
                    (255, 0, 0), 13)





    nTime = time.time()
    fps = 1 / (nTime-bTime)
    bTime = nTime
    # 绘制帧率文字
    cv2.putText(image,f"FPS: {int(fps)}",(50,70), cv2.FONT_HERSHEY_SIMPLEX,3,(255,0,0),3)
    cv2.imshow("Dumbbell exercise detection", image)
    if cv2.waitKey(5) & 0xff == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()