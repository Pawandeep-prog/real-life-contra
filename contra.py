import cv2 
import numpy as np 
import time

import pyautogui
import mediapipe as mp

import matplotlib.pyplot as plt #temporary import

pose = mp.solutions.pose
pose_o = pose.Pose()
drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)


#logic
isInit = False
prevSum = 0
sum_list = np.array([0.0]*5)


#d - move forward
#j - jump
#s - shoot
d_down=False
s_down=False
j_down=False


def findSum(lst):
	sm = 0
	sm = lst[16].y*640 + lst[15].y*640 + lst[0].y*640 + lst[23].y*640 + lst[24].y*640
	return sm

def push(sm): 
	global sum_list
	for i in range(3, -1, -1): #reverse loop 3,2,1,0
		sum_list[i+1] = sum_list[i]

	sum_list[0] = abs(sm-prevSum)

def isRunning():
	sm = 0
	for i in sum_list:
		sm = sm + i

	if sm > 30:
		return True 
	return False

def inFrame(lst):
	if lst[24].visibility > 0.7 and lst[23].visibility > 0.7 and lst[15].visibility>0.7:
		return True 
	return False

def isJump(p):
	if p<80:
		return True
	return False

def isShoot(finalres):
	if abs(finalres[15].x*640 - finalres[16].x*640) < 100:
		return True 
	return False


while True:
	stime = time.time()

	_, frm = cap.read()

	res = pose_o.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
	
	if res.pose_landmarks:
		finalres = res.pose_landmarks.landmark

	drawing.draw_landmarks(frm, res.pose_landmarks, pose.POSE_CONNECTIONS)

	cv2.putText(frm, f"{int(1/(time.time()-stime))}", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (85,0,85), 2)

	#main logic
	if res.pose_landmarks and inFrame(finalres):
		if not(isInit):
			prevSum = findSum(finalres)
			isInit = True
		else:
			newSum = findSum(finalres)
			push(newSum)

			if isJump(finalres[0].y*480): #press j down only if j is not already down
				cv2.putText(frm, "JUMP DONE", (50,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

				if not(j_down):
					pyautogui.keyDown("j")
					j_down=True
				
			else: # relese j key
				cv2.putText(frm, "Not jump", (50,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

				if j_down:
					j_down=False 
					pyautogui.keyUp("j")

			if isRunning(): ##  running down the d key
				cv2.putText(frm, "Running", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
				if not(d_down):
					d_down = True
					pyautogui.keyDown("d")

			else: 
				cv2.putText(frm, "You are still", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

				if d_down:
					d_down = False
					pyautogui.keyUp("d")

			if isShoot(finalres): # press s key for shooting
				cv2.putText(frm, "Shooting", (50,180), cv2.FONT_HERSHEY_SIMPLEX, 1, (85,0,85), 2)

				if not(s_down):
					s_down = True
					pyautogui.keyDown("s")

				
			else: # release s key up
				cv2.putText(frm, "Not Shooting", (50,180), cv2.FONT_HERSHEY_SIMPLEX, 1, (85,0,85), 2)

				if s_down:
					s_down = False
					pyautogui.keyUp("s")

			prevSum = newSum

		

	else: # here chek if any key down the make it up
		cv2.putText(frm, "Make Sure full body in frame", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

		if d_down:
			pyautogui.keyUp("d")
			d_down=False
		if s_down:
			pyautogui.keyUp("s")
			s_down=False
			

	cv2.line(frm, (0,80), (640,80), (255,0,0), 1)
	cv2.imshow("window", frm)

	if cv2.waitKey(1) == 27:
		cap.release()
		cv2.destroyAllWindows()
		break