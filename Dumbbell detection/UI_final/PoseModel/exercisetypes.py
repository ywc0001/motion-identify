import numpy as np
from PoseModel.anglecom import BodyPartAngle
from PoseModel.utils import *


class TypeOfExercise(BodyPartAngle):
    def __init__(self, landmarks):
        super().__init__(landmarks)

    def pull_up(self, counter, status, avg_score):
        right_arm_angle = self.angle_of_the_right_arm()

        standard = [33, 130]
        standard_sum = 2 * sum(standard)

        if status:
            if  right_arm_angle < 50:
                counter += 1
                status = False
            avg_score = 0
        else:
            if right_arm_angle > 140:
                status = True
            avg_score = ( 1- abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100

        return [counter, status, avg_score]


    def push_up(self, counter, status, avg_score):
        right_arm_angle = self.angle_of_the_right_arm()
        left_arm_angle = self.angle_of_the_left_arm()
        standard = [33, 130]
        standard_sum = 2 * sum(standard)

        if status:
            if  right_arm_angle < 50 and left_arm_angle < 50:
                counter += 1
                status = False
            avg_score = 0
        else:
            if right_arm_angle > 140 and left_arm_angle > 140:
                status = True
            right_score = ( 1- abs((self.angle_of_the_right_arm() - standard[0]) / standard_sum)) * 100
            left_score = ( 1- abs((self.angle_of_the_left_arm() - standard[0]) / standard_sum)) * 100
            avg_score=(right_score + left_score)/2
        return [counter, status, avg_score]




    def sit_up(self, counter, status, avg_score):
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
            avg_score = 100-(left_arm_score + right_arm_score + left_shoulder_score + right_shoulder_score) / 4
        else:
            if nose[1] < avg_shoulder_y:
                status = True
            avg_score = 100

        return [counter, status, avg_score]




    def calculate_exercise(self, exercise_type, counter, status, avg_score):
        if exercise_type == "both sides":
            counter, status, avg_score = TypeOfExercise(self.landmarks).push_up(
                counter, status, avg_score)
        elif exercise_type == "right side":
            counter, status, avg_score = TypeOfExercise(self.landmarks).pull_up(
                counter, status, avg_score)
        elif exercise_type == "push upwards":
            counter, status, avg_score = TypeOfExercise(self.landmarks).sit_up(
                counter, status, avg_score)

        return [counter, status, avg_score]

    def score_table(self, exercise, counter, status, avg_score, isPause):
        score_table = cv2.imread("./images/5.png")
        cv2.putText(score_table, "Activity : " + exercise.replace("-", " "),
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2,
                    cv2.LINE_AA)
        cv2.putText(score_table, "Counter : " + str(counter), (10, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
        cv2.putText(score_table, "Status : " + str(status), (10, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (182, 158, 128), 2, cv2.LINE_AA)
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

