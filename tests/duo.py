#Antiquated
#This program was the original startUp prgram. It runs both shooterVision and gearVision simultaneously.
#Read the documentation for more information

import numpy as np
import cv2
import logging
import math
import time
from networktables import NetworkTable

#logging.basicConfig(filename="vision.log", level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

#Configure network tables
NetworkTable.setIPAddress("10.38.80.13")
NetworkTable.setClientMode()
NetworkTable.initialize()
sd=NetworkTable.getTable("SmartDashboard")

roiCenterX = -1
roiCenterY = -1
averageX = -1
averageY = -1
rois = -1

class Vision:
    def __init__(self, video_device_index) :
        self.cap = cv2.VideoCapture(video_device_index)
        self.cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.05)
        self.cap1 = cv2.VideoCapture(1)
        self.cap1.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.05)
        self.DEGREES_PER_PIXEL = 0.105

    def ZipGenerator(self):
        while (True):
            global frameHeight, frameWidth
            _, frame = self.cap.read()
            _, frame1 = self.cap1.read()
            zFrame = zip(frame)
            z1Frame = zip(frame1)
            yield frame, frame1

    def Display(self, windowTitle, frame):
        cv2.imshow(windowTitle, frame)

    def TargetRecognition(self, frame) :
            #Convert to HSL so that we can focus in on green
            #Note that OpenCV Hue ranges only to 180 (not 360), so use 1/2 values shown in graphics program
        hsl = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            #Smooth out pixels
        blurred = cv2.blur(hsl, (5,5))
            #Modify this as necessary
        min_green = (40, 130, 130)
        max_green = (100, 255, 255)
        inrange_green = cv2.inRange(blurred, min_green, max_green)
        inrange = inrange_green
        contours, _ = cv2.findContours(inrange, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #Modify minimum contour area as necessary
        filteredContours = filter(lambda contour : cv2.contourArea(contour) > 30, contours)
        #sd.putNumber("gearRoiCount", len(filteredContours)) #was roiCount
        # Calculate the center of the
        i = 0
        minROIIndex = -1
        minCenterY = -1000000
        minCenterX = -1
        for contour in filteredContours:
            m = cv2.moments(contour)
            if m["m00"] > 0 :
                cx = int(m["m10"] / m["m00"])
                cy = int(m["m01"] / m["m00"])
                varNameX = "gearCenterX{0}".format(i) #was roiCenterX
                varNameY = "gearCenterY{0}".format(i) #was roiCenterY
                    #sd.putNumber(varNameX, cx)
                    #sd.putNumber(varNameY, cy)
                    # Find if th current contour is lower (in Y) than minCenterY
                if cy > minCenterY :
                    minROIIndex = i
                    minCenterY = cy
                    minCenterX = cx
            i += 1
            #sd.putNumber("roiCenterX", minCenterX)

        return frame, filteredContours, (minCenterX, minCenterY)

    def Overlay(self, frame, regionsOfInterest, chosenTargetSpot):
        green = cv2.cv.Scalar(0, 255, 0)
        red = cv2.cv.Scalar(0, 0, 255)
        cv2.drawContours(frame, regionsOfInterest, -1, red)

            #Draw the target spot in magenta
        cv2.rectangle(frame, chosenTargetSpot, (chosenTargetSpot[0] + 4, chosenTargetSpot[1] + 4), cv2.cv.Scalar(255,0,255),-1)

        if len(regionsOfInterest) > 0 :
            x, y, w, h = cv2.boundingRect(regionsOfInterest[0])
            cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y + h)), cv2.cv.Scalar(255,0,0),2)
            cv2.line(frame, ( chosenTargetSpot[0], 0), (chosenTargetSpot[0], 800), cv2.cv.Scalar(255,0,0))
        # Draw the center of the image
        height, width = frame.shape[:2]
        centerX = int(width / 2)
        centerY = int(height / 2)
        cv2.circle(frame, (centerX, centerY), 20, red)
        cv2.line(frame, (0, centerY), (width, centerY), red)
        cv2.line(frame, (centerX, 0), (centerX, height), red)
            # How many ROIs?
            #font = cv2.FONT_HERSHEY_SIMPLEX
            #msg = "Found {0} ROIs!".format(len(regionsOfInterest))
            #cv2.putText(frame, msg, (10, 50), font, 2, red, 2, cv2.CV_AA)
        return frame

    def DegreesToTurn(self, targetX):
        centerX = 320.0
        distanceFt = 0
        turn = (targetX * self.DEGREES_PER_PIXEL) - (centerX * self.DEGREES_PER_PIXEL)#Degrees from center of frame to edge
        logging.log(logging.DEBUG, "{0} - {1}".format(centerX, targetX))
        logging.log(logging.DEBUG, "Degrees to turn: {0}".format( turn))
        return turn

    def IsAligned(self, roi, frame) :
        height, width = frame.shape[:2]
        centerX = int(width / 2)
        centerY = int(height / 2)
        roiCenterX = roi[0] + (roi[2] // 2)
        roiCenterY = roi[1] + (roi[3] // 2)
        horizontalOffset = abs(centerX - roiCenterX)
        verticalOffset = abs(centerY - roiCenterY)
        distanceSquared = horizontalOffset * horizontalOffset + verticalOffset* verticalOffset
        return True if distanceSquared < 2500 else False

    def left(self, rois):
        def xComparator(roi):
            x, _, _, _ = cv2.boundingRect(roi)
            return x
        sortedFromLeft = sorted(rois, key = xComparator)
        rects = map(lambda roi : cv2.boundingRect(roi), rois)
        XList = map(lambda rect : rect[0], rects)
        XList = sorted(XList)
        lowest = -1

        for i in range(0, len(XList)):
            for j in range(0, len(XList)):
                if (XList[j] < XList[i]):
                    lowest = XList[j]
        #print "Lowest X Value: ", lowest
        return lowest

    def cluster(self, rois):
        def xComparator(roi):
            x, _, _, _ = cv2.boundingRect(roi)
            return x

        def average(xList):
            i = reduce(lambda x, y: x + y, xList) / len(xList)
            return round(i, 0)
            #set initials values to equivilent of the origin to avoid issues in averaging
        left = [320]
        right = [320]
        print "left len ", len(left)
        print "right len ", len(right)
        sortedFromLeft = sorted(rois, key = xComparator)
        rects = map(lambda roi : cv2.boundingRect(roi), rois)
        XList = map(lambda rect : rect[0], rects)
        xList = sorted(XList)
            #Makes 2 lists
        print "Average: ", average(XList)
        for i in range(0, len(XList)):
             if XList[i] < average(XList):
                 left.append(i)
                    #print "Left appended, i: ", i
             else:
                 right.append(i)
                    #print "Right appended, i: ", i
        rightTarget = average(right)
        leftTarget = average(left)
        return leftTarget

    def EstimateRange(self, roi, tapeIsVertical) :
        #print roi
        _, _, w, h = cv2.boundingRect(roi)
        # If isVertical means that we're targeting gears and therefore the "height" of the tape is its horizontal measure
        target = w
        if tapeIsVertical :
            target = h
        estimatedAngle = target * self.DEGREES_PER_PIXEL
        subtendedAtTenFeet = 9.5
        estimatedDistance = (subtendedAtTenFeet/ estimatedAngle) * 10 # * 10'
        logging.log(logging.INFO, "Estimated distance {0}".format(estimatedDistance))
        return estimatedDistance

    def ScoreROI(self, roi) :
        #point = self.GetPoint()
        x, y, w, h = cv2.boundingRect(roi)
        aspectRatio = (1.0 * w) / (1.0 * h)
        idealTopTapeRatio = 15.0 / 4.0
        idealBottomTapeRatio = 15.0 / 2.0
        ratioRelativeToTop = aspectRatio / idealTopTapeRatio
        ratioRelativeToBottom = aspectRatio / idealBottomTapeRatio
        # the closer either of those is to 1, the better
        if ratioRelativeToTop == 1.0 :
            topScore = 10000
        else:
            topScore = abs(10 / (ratioRelativeToTop - 1.0))
        if ratioRelativeToBottom == 1.0 :
            bottomScore = 10000
        else:
            bottomScore = abs(10 / (ratioRelativeToBottom - 1.0))
        return (topScore, roi)

    def ScoreROIPair(self, top, bottom) :
        ax, ay, aw, ah = cv2.boundingRect(top)
        bx, by, bw, bh = cv2.boundingRect(bottom)
        xDif = ax - bx
        #Threshold to cut out obvious wrong ROIs
        if xDif > 550 or xDif < 150:
            print xDif, " is outside of range"
        else:
            averageX = (ax + bx) / 2
            print "averageX: ", averageX
            averageY = (ay + by) / 2
        #Offset in x
        bottomDeltaX = bx - ax
        distanceBetweenTopAndBottom = by - (ay + ah)
        xOffsetScore = -1
        yOffsetScore = -1
        #Score based on closeness of offset in X
        if bottomDeltaX == 0 :
            xOffsetScore = 10000
        else :
            xoffsetScore = abs(10000 / bottomDeltaX)
    #TODO: Since top tape is 4" high and distance between 2 is 4
        if distanceBetweenTopAndBottom == ah :
            # There's 4" between them
            yOffsetScore = 10000
        else :
            yOffsetScore = abs(10000 / ah - distanceBetweenTopAndBottom)
        return xOffsetScore, yOffsetScore

    def ScoreROIs(self, rois) :
        scoredROIs = map(self.ScoreROI, rois)
        scoredROIs.sort(key = lambda t : t[0], reverse=True)
        bestROI = scoredROIs[0][1]
        chosenX, chosenY, chosenW, chosenH = cv2.boundingRect(bestROI)
        ctr = (chosenX + chosenW / 2, chosenY + chosenH / 2)
        return ctr

    def gearVision(self, roiCenterX, rois):
        targetX = None
        targetY = None
        if len(rois) > 1 and len(rois) < 5:
            print len(rois), " rois found"
            scoredROIs = map(self.ScoreROI, rois)
            scoredROIs.sort(key = lambda t : t[0], reverse=True)
            chosenX, chosenY, chosenW, chosenH = cv2.boundingRect(scoredROIs[0][1])
            ctr = (chosenX + chosenW / 2, chosenY + chosenH / 2)
            targetX = self.left(rois)
            print "Far left X ", targetX
        elif len(rois) > 4:
            #Gives location to far left tape
            print len(rois), " Rois found"
            targetX = self.cluster(rois)
        elif len(rois) == 1:
            print len(rois), " roi found"
            x, y, w, h = cv2.boundingRect(rois[0])
            targetX = (x + w) / 2
            targetY = (y + h) / 2
            print "Roi X ", targetX
        else:
            print len(rois), " rois found. Out of range."

        return targetX, targetY

    def shooterVision(self, roiCenterX, rois):
        ctr = None
        if rois != None:
            ctr = self.ScoreROIs(rois) if len(rois) > 1 else ctr
        return ctr

    def CaptureLoop(self, roiCenterX, roiCenterY, rois):
        #shootingFrame,            , gearFrame
        for (shootingFrame, gearFrame) in self.ZipGenerator():
            frame, rois, ctr = self.TargetRecognition(shootingFrame)
            frame1, rois1, ctr1 = self.TargetRecognition(gearFrame)
            isAligned = False
            bestROI = None
            targetX = None
            if len(rois) == 1 :
                bestROI = rois[0]

            sTarget = self.shooterVision(roiCenterX, rois)
            gTarget = self.gearVision(roiCenterX, rois1)

            if sTarget != None:
                if(sTarget[0] != None):
                    sTurn = self.DegreesToTurn(sTarget[0])
                    DEGREES_WHEN_CENTER_IS_ZERO = -33.705
                    if sTurn == DEGREES_WHEN_CENTER_IS_ZERO:
                        logging.log(logging.DEBUG, "ROI not found")
                        notFound = -404
                        sd.putNumber("shooterDegrees", notFound)
                    else:
                        logging.log(logging.INFO, "Putting turn {0}".format(sTurn))
                        sd.putNumber("shooterDegrees",sTurn)

            if gTarget != None:
                if gTarget[0] != None:
                    gTurn = self.DegreesToTurn(gTarget[0])
                    DEGREES_WHEN_CENTER_IS_ZERO = -33.705
                    if gTurn == DEGREES_WHEN_CENTER_IS_ZERO:
                        logging.log(logging.DEBUG, "ROI not found")
                        notFound = -404
                        sd.putNumber("gearDegrees", notFound)
                    else:
                        logging.log(logging.INFO, "Putting turn {0}".format(gTurn))
                        sd.putNumber("gearDegrees", gTurn)

            if bestROI != None:
                # Estimate range for target shooting (isVertical == False)
                estRange = self.EstimateRange(bestROI, False)
                #sd.putNumber("estimatedRange", estRange)
            sOutput = self.Overlay(frame, rois, ctr)
            gOutput = self.Overlay(frame1, rois1, ctr1)
            sQuit = self.Display("shooting", sOutput)
            gQuit = self.Display("gear", gOutput)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    #cv2.imwrite("capture.png", frame)
            #    break
def main(argv=None):
    vision = Vision(0)
    vision.CaptureLoop(roiCenterX, roiCenterY, rois)

if __name__ == "__main__":
    main()
