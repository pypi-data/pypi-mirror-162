from cvindrones import faceProcessor
import cv2
cap = cv2.VideoCapture(0)
while True:
    success, image = cap.read()
    funValues = faceProcessor(image,draw=True)
    image = funValues[0]
    area = funValues[1]
    x,y,w,h = funValues[2]
    cv2.imshow('Faces', image)
    cv2.waitKey(1)
cap.release()