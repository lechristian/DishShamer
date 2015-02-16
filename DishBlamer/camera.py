import cv2
import time
import serial
from datetime import datetime

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

import operator
import json

# Serial port for Arduino
SERIAL_PORT = "/dev/tty.usbmodem1411"

testing = True

log = open("log.txt","r+w")
logContent = log.read()
logArray = json.loads(logContent)
emails = {"Sarah":"schasins@gmail.com","Alison":"schasins@gmail.com","Baxter":"schasins@gmail.com","Christian":"schasins@gmail.com"}
GMAIL_USER = 'yourangrydishes@gmail.com'
GMAIL_PASS = 'yosupyosup'
histograms = {}

def features(imageFile):
    img=cv2.imread(imageFile)
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    histogram = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
    Nhistogram=cv2.normalize(histogram)
    return Nhistogram.flatten()

def setupComparisonHistograms():
    for name in emails:
        histogram = features("images/training/"+name+".jpg")
        histograms[name] = histogram
    return

def guessUser(filename):
    currHist = features(filename)
    bestSimSoFar = -100000000000000000000
    nameGuessSoFar = ""
    for name in histograms:
        sim = cv2.compareHist(currHist,histograms[name],cv2.cv.CV_COMP_CORREL)
        if sim > bestSimSoFar:
            bestSimSoFar = sim
            nameGuessSoFar = name
    return nameGuessSoFar

def processNewEvent(filename, addedDishes):
    global log
    timestamp = time.time()
    name = guessUser(filename)
    scoreDiff = 1
    if not addedDishes:
        scoreDiff = -1
    logArray.append([name,timestamp,scoreDiff,filename])
    log.truncate(0)
    log.seek(0)
    log.write(json.dumps(logArray))
    log.close()
    log = open("log.txt","r+w")

def generateEmail():
    scores = {}
    for cells in logArray:
        name = cells[0]
        scores[name] = scores.get(name,0)+int(cells[2]) # -1 if removed plates, +1 if added plates
    sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    print sortedScores

    emailString = ""
    best = None
    worst = None
    for i in range(len(sortedScores)):
        score = sortedScores[i]
        emailString += score[0]+":\t"+str(score[1])+"\n"
        if i == 0:
            best = score[0]
        if i == (len(sortedScores)-1):
            worst = score[0]

    for name in emails:
        addition = "Your dish washing results, "+name
        if name == best:
            addition = "You're the best, "+name+"!!!!!"
        elif name == worst:
            addition = "You're in trouble, "+name+"!!!!!"
        currEmailString = addition+"\n"+emailString

        recipient = emails[name]

        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(GMAIL_USER, GMAIL_PASS)
        header = 'To:' + recipient + '\n' + 'From: ' + GMAIL_USER
        header = header + '\n' + 'Subject:' + addition + '\n'
        print header
        msg = header + '\n' + currEmailString + ' \n\n'
        smtpserver.sendmail(GMAIL_USER, recipient, msg)
        smtpserver.close()

def testWithoutSerialInput():
    time.sleep(5);
    processNewEvent("images/a.jpg",True)
    time.sleep(6);
    processNewEvent("images/g.jpg",False)
    time.sleep(5);
    processNewEvent("images/c.jpg",True)
    time.sleep(6);
    processNewEvent("images/f.jpg",False)
    time.sleep(3);
    processNewEvent("images/b.jpg",False)
    time.sleep(4);
    processNewEvent("images/h.jpg",True)
    time.sleep(3)
    processNewEvent("images/e.jpg",True)


def imageCapture():   
    cap = cv2.VideoCapture(0)
    time.sleep(1)

    s = serial.Serial(SERIAL_PORT, 9600)

    while True:
        try:
            data = s.read(s.inWaiting())
            if data:
                curDateTime = ""
                if data == "g" or data == "b":
                    ret, frame = cap.read()
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

                    curDateTime = data
                    curDateTime += datetime.now().strftime('%m.%d.%Y-%H.%M.%s')
                    curDateTime += '.jpg'
                    out = cv2.imwrite(curDateTime, frame)
                if data == "g":
                    #plates returned
                    processNewEvent(curDateTime,true)
                elif data == "b":
                    #plates removed
                    processNewEvent(curDateTime,false)


        except serial.serialutil.SerialException:
            pass

if __name__ == "__main__":
    #generateEmail()
    setupComparisonHistograms()
    try:
        if testing:
            testWithoutSerialInput()
            generateEmail()
        else:
            imageCapture()
    except KeyboardInterrupt:
        pass
