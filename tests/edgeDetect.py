import numpy as np
import cv2
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from threading import Thread

frameWidth = -1
frameHeight = -1
mutableLineMessage = "Unknown"

def captureGenerator(cap) :
    while (True):
        global frameHeight, frameWidth
        ret, frame = cap.read()
        frameWidth = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        frameHeight = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

        yield frame

def display(frame) :
    cv2.imshow('frame', frame)

def init ():
    cap = cv2.VideoCapture(0)
    return cap

def initWebServer () :
    PORT = 8000
    server = HTTPServer(('localhost', PORT), MyHandler)
    server.serve_forever()

def teardown (cap):
    cap.release()
    cv2.destroyAllWindows()

def process (frame) :
    global mutableLineMessage
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray = frame
    thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    filteredContours = filter(lambda contour : cv2.contourArea(contour) > 250.0, contours)
    green = cv2.cv.Scalar(136,170,75)
    ALL_CONTOURS = -1
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(frame, filteredContours, ALL_CONTOURS, green)
    # Draw the center of the image
    height, width = gray.shape[:2]
    centerX = int (width / 2)
    centerY = int (height / 2)
    cv2.circle(frame, (centerX, centerY), 20, cv2.cv.Scalar(0, 0, 255))
    cv2.line(frame, (0, centerY), (width, centerY), cv2.cv.Scalar(0, 0, 255))
    cv2.line(frame, (centerX, 0), (centerX, height), cv2.cv.Scalar(0, 0, 255))
    return frame

# Web server
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global frameHeight, frameWidth, mutableLineMessage

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = "<html><p> [{0} X {1}] </p><p>{2}</p></html>".format(frameWidth, frameHeight, mutableLineMessage)

        self.wfile.write(html.encode())

def captureLoop() :
    cap = init()

    for frame in captureGenerator(cap):
        gray = process(frame)
        display(gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


webThread = Thread(target=initWebServer, args=())
webThread.start()
vidThread = Thread(target=captureLoop, args=())
vidThread.start()
vidThread.join()
