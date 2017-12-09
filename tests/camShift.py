import numpy as np
import argparse
import cv2
from matplotlib import pyplot as plt
cap = cv2.VideoCapture(0)

while (True) :
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([50,80,50])
    upper_green = np.array([90,200,80])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    res = cv2.bitwise_and(frame,frame, mask= mask)
    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)
    
