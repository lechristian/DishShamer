import cv2
import time
import serial
from datetime import datetime

# Serial port for Arduino
SERIAL_PORT = "/dev/tty.usbmodem1411"

def imageCapture():   
    cap = cv2.VideoCapture(0)
    time.sleep(1)

    s = serial.Serial(SERIAL_PORT, 9600)

    while True:
        try:
            data = s.read(s.inWaiting())
            if data:
                if data == "c":
                    ret, frame = cap.read()
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

                    curDateTime = datetime.now().strftime('%m.%d.%Y-%H.%M.%s')
                    curDateTime += '.jpg'
                    out = cv2.imwrite(curDateTime, frame)

        except serial.serialutil.SerialException:
            pass

if __name__ == "__main__":
    try:
        imageCapture()
    except KeyboardInterrupt:
        pass
