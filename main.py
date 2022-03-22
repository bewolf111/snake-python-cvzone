import cvzone
import cv2
import numpy as np
import self as self
from cvzone.HandTrackingModule import HandDetector
import math
import random



cap = cv2.VideoCapture(2) #quale cam prende 0 pc, 1 esterna ecc
# grandezza video
cap.set(3, 1280)
cap.set(4, 720)


detector = HandDetector(detectionCon=0.8, maxHands=1)
# corpo del serpente:
class SnakeClass:
    def __init__(self, pathFood):
        self.points = []  # punti del serpente
        self.lengths = []  # distanza tra punti
        self.currentLenght = 0  # lunghezza totale attuale
        self.allowedLength = 100  # lunghezza totale iniziale
        self.previousHead= 0, 0  # punto precedente

        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED) # per mantenere la png trasparente
        self.hFood, self.wFood,_ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()
        self.score = 0
        self.pun = 0
        self.gameOver = False


    def randomFoodLocation(self):
        self.foodPoint = [random.randint(150, 1000), random.randint(150, 550)]


    def update(self, imgMain: object, currentHead: object) -> object:
        global rx, ry
        if self.gameOver:

            cvzone.putTextRect(imgMain, "Game Over", [300,400],
                               scale = 6, thickness= 4, offset= 20)
            cvzone.putTextRect(imgMain, f'punteggio: {self.score}', [300, 550],
                               scale=6, thickness= 4, offset=20)

        else:

            px, py = self.previousHead   # testa precedente
            cx, cy = currentHead         # testa attuale

            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)  # ipotenusa
            self.lengths.append(distance)  # creiamo la distance appena generata
            self.currentLenght += distance  # aggiungiamo la distance appena generata
            self.previousHead = cx, cy


    #  riduzione della lunghezza totale
            if self.currentLenght > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLenght -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self. currentLenght < self.allowedLength:
                        break

            # hai mangiato?
            rx, ry = self.foodPoint  # punti random
            if rx - self.wFood//2 <cx < rx +self.wFood//2 and\
                    ry - self.wFood//2 < cy < ry + self.hFood//2: #se lo tocca, then:
                self.randomFoodLocation()
                self.allowedLength +=50
                self.score +=1
                print(self.score)



            # serpe
            if self.points:
                for i, point in enumerate(self.points):
                    if i!= 0:  # punto iniziale
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (100,0,155), 20)  # disegnamo il primo punto
                cv2.circle(imgMain, self.points[-1], 15, (100, 128, 0), cv2.FILLED)

            # cibo avvelenato

            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

            cvzone.putTextRect(imgMain, f'Punteggio: {self.score}', [50, 80],
                                   scale=1, thickness=2, offset=10)
            cvzone.putTextRect(imgMain, f'Premi r per reset', [30, 60],
                                   scale=1, thickness=2, offset=10)

            # su,  centrare le coordinate

            # collisione basandoci su punti, ed escludendo i più vicini alla testa
            pts = np.array(self.points[:-2], np.int32)  # esclusi testa e punto prima, interi 32bit
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (100, 100, 0), 3)
            minDist = cv2.pointPolygonTest(pts,(cx, cy), True)


            if -1<= minDist <= 1:
                print("a")
                self.gameOver = True
                self.points = []  # punti del serpente
                self.lengths = []  # distanza tra punti
                self.currentLenght = 0  # lunghezza totale
                self.allowedLength = 100  # lunghezza totale iniziale
                self.previousHead = 0, 0  # punto precedente
                self.randomFoodLocation()
                self.pun = 0


        return imgMain

gioco = SnakeClass("mela.png")


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:  # dizionario con dentro il valore lmlist
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]  # 3 valori xy e. z 0,2 toglie z
        img = gioco.update(img, pointIndex)

    cv2.imshow("image", img)
    key = cv2.waitKey(30)
    if key == ord('r'):
        gioco.gameOver = False
        gioco.score = 0
