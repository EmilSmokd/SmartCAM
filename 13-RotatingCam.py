import cv2
import time
import numpy as np
from pyfirmata import Arduino, SERVO
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
board = Arduino('COM5')
board.digital[11].mode = SERVO
board.digital[3].mode = SERVO

def setServoAngle(pin, angle):
    board.digital[pin].write(angle)
    time.sleep(0.015)


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

W = 640  # Ancho de la ventana de la videoCam
H = 400  # Altura de la ventana de la videoCam
video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, W)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

while video.isOpened():

    ret, video1 = video.read()
    gray = cv2.cvtColor(video1, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    cv2.line(video1, (W//2, 0), (W//2, H), (0, 0, 255), 2)  # Eje y
    cv2.line(video1, (0, H//2), (W, H//2), (0, 0, 255), 2)  # Eje x
    p1 = cv2.circle(video1, (W//2, H//2), 2, (255, 215, 0), 10)  # Punto centrado a los ejes

    for (x, y, w, h) in faces:
        img = cv2.rectangle(video1, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Cuadro de color azul para toda la cara
        p2X, p2Y = int(x + w / 2), int(y + h / 2)  # Punto de referencia del cuadro de la ventana
        p2 = cv2.circle(video1, (p2X, p2Y), 2, (124, 252, 0), 10)

        deltaX = abs(w-x)  # Distancia del ancho del rectancugulo para x
        betaX = abs(int(W/2)-int(x+w/2))  # Distancia de p1 a p2 para x
        deltaY = abs(h-y)  # Distancia del alto del rectancugulo para y
        betaY = abs(int(H/2)-int(y+h/2))  # Distancia de p1 a p2 para y

        p2xRp1, p2yRp1 = (-W//2+x+w//2), (H//2-(y+h//2))

        cv2.putText(video1, 'p2x= {0}, p2y={1}'.format(p2xRp1, p2yRp1), (300, 350), cv2.QT_FONT_NORMAL, 0.7, (124, 252, 0), 1)

        if betaX > deltaX*0.2:
            cv2.putText(video1, 'X', (160, 100), cv2.QT_FONT_NORMAL, 0.7, (255, 0, 0), 3)
            if p2xRp1 > 0:
                ejeX = _map(p2xRp1,0,320,90,180)
                setServoAngle(11,ejeX)
            elif p2xRp1 < 0:
                ejeX = _map(p2xRp1,-320,0,0,90)
                setServoAngle(11,ejeX)
        elif betaY > deltaY*0.6:
            cv2.putText(video1, 'Y', (160*3, 100), cv2.QT_FONT_NORMAL, 0.7, (0, 0, 255), 3)
            if p2yRp1 > 0:
                ejeY = _map(p2yRp1,0,100,90,180)
                setServoAngle(3,ejeY)
            elif p2yRp1 < 0:
                ejeY = _map(p2yRp1,-100,0,0,90)
                setServoAngle(3,ejeY)
    cv2.imshow('Video camara', video1)
    if cv2.waitKey(1) == ord(' '):
        break
video.release()
cv2.destroyAllWindows()