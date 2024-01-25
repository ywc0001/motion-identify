# Fitness Butler

#### Description
Based on mediapipe, opencv and PyQt5, the fitness action detection program includes supine, prone, squat, pull-up, right dumbbell flexion and extension, both sides of dumbbell flexion and extension and dumbbell upward push.

#### Software Architecture

1. Console module
2. Dumbbell module
3. Push ups, sit-ups, squats, pull-ups module

#### Environment

1. Windows10 and above PC
2. Based on python version 3.10
3. The IDE uses pycharm
4. Install opencv, mediapipe-python, PyQt5, and pandas interpreters

#### Installation
1. Users can clone the code locally directly from gitee

```
git clone https://gitee.com/ywc2023/motion-identify.git
```

2. Install opencv, mediapipe-python, PyQt5, and pandas interpreters

_Use the pip tool for quick installation of the relevant interpretors_

Verify that pip is installed: type it at the command line

```
pip --version
```

Installing opencv
```
pip install opencv-python
```

Installing mediapipe

```
pip install mediapipe
```

Installing PyQt5

```
pip3 install PyQt5
```
Installing pandas

```
pip install pandas
```

#### Instructions

There are four options in the sit-up section, and clicking each option opens the camera for detection.

Dumbbell Fitness has three options that support file detection and real-time camera detection.

#### Contribution

Members: LI Ao, ZHANG Zexuan, HOU Junli, XING Guangwei, CHANG Wenyi


#### Thanks

This project makes reference to some other excellent open source projects. Thanks:

[mediapipe-Fitness-counter](https://github.com/MichistaLin/mediapipe-Fitness-counter)

[Ai-Personal-Trainer](https://github.com/mbhupendra/Ai-Personal-Trainer)