import numpy as np
import cv2
import logging
import math
import time
from networktables import NetworkTable

#logging.basicConfig(filename="vision.log", level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

#Configure network tables
NetworkTable.setIPAddress("10.38.80.2") #IP of the RoboRIO
NetworkTable.setClientMode()
NetworkTable.initialize()
sd=NetworkTable.getTable("SmartDashboard")

class Vision :
    # Initializes the Vision subsystem, opening the camera at `video_device_index`
    # Additionally lowers the brightness of the camera -- this does not work with
    # all Webcams, and is an important feature, so check
    # Sets constants for estimating range and turn degrees
    def __init__(self, video_device_index) :
        self.cap = cv2.VideoCapture(video_device_index)
        self.cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.05)
        self.DEGREES_PER_PIXEL = 0.105


    # Generates an (infinite) sequence of video capture frames.
    def CaptureGenerator(self):
        while (True):
            global frameeight, frameWidth
            _, frame = self.cap.read()
            yield frame

    # Outputs `frame` in a window called "frame". If there is not a graphical desktop,
    # this function raises an exception
    def Display(self, frame):
        cv2.imshow('frame', frame)

    # Finds regions of interest (ROIs) in `frame`. These are defined as areas within a certain HSL range and
    # greater than a certain square area (in pixels).
    def TargetRecognition(self, frame) :
        #Convert to HSL so that we can focus in on green
        #Note that OpenCV Hue ranges only to 180 (not 360), so use 1/2 values shown in graphics program
        hsl = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #Smooth out pixels
        blurred = cv2.blur(hsl, (5,5))

        #Modify this as necessary
        #was 40, 100, 100
        #    80, 255, 255
        min_green = (40, 130, 130)
        max_green = (100, 255, 255)
        inrange_green = cv2.inRange(blurred, min_green, max_green)
        inrange = inrange_green

        contours, _ = cv2.findContours(inrange, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #Modify minimum contour area as necessary
        filteredContours = filter(lambda contour : cv2.contourArea(contour) > 30, contours)

        #sd.putNumber("roiCount", len(filteredContours))

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
                        #varNameX = "roiCenterX{0}".format(i)
                        #varNameY = "roiCenterY{0}".format(i)
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


    # Creates the visual elements for display. For instance, crosshairs, ROIs, etc.
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
    '''
    def averageRois(self, rois):
        def average(XList):
            i = reduce(lambda x, y: x + y, xList) / len(xList)
            return round(i, 0)

        def xCompartor():
    '''

    # `targetX` is relative to the left-hand side of the screen.
    # Assumes a 640-pixel wide screen (modify `centerX` to be resolution / 2) if necessary
    # Relies on DEGREES_PER_PIXEL, which was determined by trial-and-error (more or less)
    def DegreesToTurn(self, targetX):
        centerX = 320.0
        distanceFt = 0
        turn = (targetX * self.DEGREES_PER_PIXEL) - (centerX * self.DEGREES_PER_PIXEL)#Degrees from center of frame to edge
        logging.log(logging.DEBUG, "{0} - {1}".format(centerX, targetX))
        logging.log(logging.DEBUG, "Degrees to turn: {0}".format( turn))
        return turn

    # Returns true if roi is within 50 pixels of the center of `frame`
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

    #Returns the shooting spot (point 1, 2, or 3)
    #def GetPoint(self):
    #    return sd.getNumber('point', 1) #robotpy docs says parameters are: key (string to look up), defaultValue (value to be returned if no value is found)

    # Returns the range to ROI, based on the short side of the tape. For shooting, `tapeIsVertical` is False. For Gear, it is True
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

    # Scores the ROI n terms of how well it fits the expected aspect ratio of 15" to 4" or 2" (depending on whether top or bottom)
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
        #print "ROI aspect ratio {0} scores {1}, {2}".format(aspectRatio, topScore, bottomScore)

        #avgX = average ROIs X
        #deg = self.degreesToTurn(point, x)
        return (topScore, roi)

    # Scores a pair of ROIs in terms of how how well aligned they are horizontally and how close to the 4" apart they are
    def ScoreROIPair(self, top, bottom) :
        ax, ay, aw, ah = cv2.boundingRect(top)
        bx, by, bw, bh = cv2.boundingRect(bottom)
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

    # Pair-wise scores all ROIs. Note that this can involve a large number of calcs on many ROIs. If that's an issue, Google "quadtrees" and "space partitioning algorithms"
    def ScoreROIPairs(self, rois) :
        def yComparator (roi) :
            _, y, _, _ = cv2.boundingRect(roi)
            return y

        highXScore = -1
        highYScore = -1
        sortedFromTop = sorted(rois, key = yComparator)
        for i in range(0, len(sortedFromTop)) :
            top = sortedFromTop[i]
            for j in range(i, len(sortedFromTop)) :
                bottom = sortedFromTop[j]
                xScore, yScore = self.ScoreROIPair(top, bottom)
                if xScore > highXScore :
                    highXScore = xScore
                    bestROITop = i
                    bestROIBottom = j
                    highYScore = yScore
        bestTopRect = cv2.boundingRect(sortedFromTop[bestROITop])
        bestBottomRect = cv2.boundingRect(sortedFromTop[bestROIBottom])
        #print "Best pair is {0} over {1} with horizontal offset score {2}".format(bestTopRect, bestBottomRect, highXScore)
        return bestTopRect

    # Scores all the ROIs and chooses the one with the highest score. Returns that chosen ROI's center point.
    def ScoreROIs(self, rois) :
        scoredROIs = map(self.ScoreROI, rois)
        scoredROIs.sort(key = lambda t : t[0], reverse=True)
        bestROI = scoredROIs[0][1]
        chosenX, chosenY, chosenW, chosenH = cv2.boundingRect(bestROI)
        ctr = (chosenX + chosenW / 2, chosenY + chosenH / 2)
        return ctr

    # Main control loop. For each frame, performs target recognition, ROI selection, writes to network tables, and displays frame
    def CaptureLoop(self):
        for cap in self.CaptureGenerator():

            shooterVision = sd.getBoolean("shooterVision", True)
            if shooterVision == False:
                #bad = -404
                #sd.putNumber("degrees", bad)
                break

            frame, rois, ctr = self.TargetRecognition(cap)
            isAligned = False
            bestROI = None
            if len(rois) == 1 :
                bestROI = rois[0]

            ctr = self.ScoreROIs(rois) if len(rois) > 1 else ctr
            if ctr != None:
                turn = self.DegreesToTurn(ctr[0])
                DEGREES_WHEN_CENTER_IS_ZERO = -33.705
                if turn == DEGREES_WHEN_CENTER_IS_ZERO:
                    logging.log(logging.DEBUG, "ROI not found")
                    notFound = -404
                    sd.putValue("degrees", notFound)
                else:
                    logging.log(logging.INFO, "Putting turn {0}".format(turn))
                    sd.putValue("degrees",turn)
            if bestROI != None:
                #  Estimate range for target shooting (isVertical == False)
                estRange = self.EstimateRange(bestROI, False)
                sd.putNumber("estimatedRange", estRange)

            #if len(rois) == 2:
            #logging.log(logging.INFO, "Currently posting: {0}".format(ctr[0]))
            #fps = cap.get(cv2.cv.CV_CAP_PORP_FPS)
            #sd.putNumber("roiCenterX", ctr[0])
            #sd.putNumber("roiCenterY", ctr[1])

            #Displays video feed
                #Commented out for performence
            #output = self.Overlay(frame, rois, ctr)
            #self.Display(output)


            if cv2.waitKey(1) & 0xFF == ord('q'):       #Press "q" to quit the program
                #cv2.imwrite("capture.png", frame)      #records an image of the frame to the pi for future reference
                break

    # For event processing. Not currently used.
    def ROIDetected(self, callback):
        self.callbacks.append(callback)

def main(argv=None):
    vision = Vision(0)
    vision.CaptureLoop()

if __name__ == "__main__":
    main()
