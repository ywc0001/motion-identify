# 健身管家

#### 项目介绍
基于mediapipe、opencv、PyQt5构建的健身动作检测程序，检测范围包括仰卧、俯卧、深蹲、引体、哑铃右侧屈伸、哑铃两侧屈伸和哑铃向上推举动作。 


#### 软件架构
1. 控制台模块
2. 哑铃模块
3. 俯卧撑、仰卧起坐、深蹲、引体向上模块


#### 使用环境

1.  Windows10及以上版本的PC
2. 基于3.10版本的python
3. IDE使用pycharm
4. 安装opencv、mediapipe-python、PyQt5及pandas解释器

#### 安装教程
1. 用户可直接从gitee上将代码克隆到本地

```
git clone https://gitee.com/ywc2023/motion-identify.git

```
2. 安装opencv、mediapipe-python、PyQt5及pandas解释器

 _使用pip工具可快速安装相关解释器_ 

验证是否安装pip:在命令行输入

```
pip --version
```

opencv安装

```
pip install opencv-python
```
mediapipe安装

```
pip install mediapipe
```
PyQt5安装

```
pip3 install PyQt5 
```
pandas安装

```
pip install pandas
```
#### 使用示例
仰卧起坐部分有四个选项，点击各选项即可开启摄像头进行检测
![仰卧起坐等](Dumbbell%20detection/final_work/images/%E4%BB%B0%E5%8D%A7%E8%B5%B7%E5%9D%90%E7%AD%89.png)
哑铃健身有三个选项，支持文件检测和摄像头实时检测
![哑铃健身](Dumbbell%20detection/final_work/images/%E5%93%91%E9%93%83%E5%81%A5%E8%BA%AB%E9%A1%B5%E9%9D%A2.png)



#### 参与贡献

成员：李傲、张泽轩、侯俊丽、邢广威、常文艺

#### 鸣谢
本项目参考了其他一些相关的优秀开源项目，在此一并致谢：

[mediapipe-Fitness-counter](https://github.com/MichistaLin/mediapipe-Fitness-counter)

[Ai-Personal-Trainer](https://github.com/mbhupendra/Ai-Personal-Trainer)




