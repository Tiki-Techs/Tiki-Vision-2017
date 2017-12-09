import numpy as np
import cv2

class Vision :
    def __init__(self, video_device_index) :
        self.cap = cv2.VideoCapture(video_device_index)

    def CaptureGenerator(self):
        while (True):
            global frameeight, frameWidth
            _, frame = self.cap.read()
            yield frame

    def Display(self, frame):
        cv2.imshow('frame', frame)

    def GreenContours(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        green_min = np.array([85, 130, 90], np.uint8)
        green_max = np.array([116, 255, 255], np.uint8)
        green_frame = cv2.inRange(hsv, green_min, green_max)
        contours, hierarchy = cv2.findContours(green_frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        filteredContours = filter(lambda contour: cv2.contourArea(contour) > 650.0, contours)
        return frame, filteredContours

    def BrightestRegion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(blurred)
        roi = [maxLoc[0] - 11, maxLoc[1] - 11, 22, 22]
        return frame, [roi]

    def Overlay(self, frame, regionsOfInterest):
        green = cv2.cv.Scalar(0, 255, 0)
        red = cv2.cv.Scalar(0, 0, 255)

        # Draw a rectangle around the ROIs
        for (x, y, w, h) in regionsOfInterest:
            cv2.rectangle(frame, (x, y), (x + w, y + h), green, 2)
        #cv2.drawContours(frame, regionsOfInterest, 0, green)

        # Draw "LEDs"
        def drawLeds(frame, roi) :
            color = lambda b: green if b else red

            def drawHorizontalLed(low,ok,high) :
                cv2.circle(frame, (20, 40), 10, color(low), -1)
                cv2.circle(frame, (40, 40), 10, color(ok), -1)
                cv2.circle(frame, (60, 40), 10,  color(high), -1)

            def drawVerticalLed(low,ok,high) :
                cv2.circle(frame, (80, 20), 10, color(low), -1)
                cv2.circle(frame, (80, 40), 10, color(ok), -1)
                cv2.circle(frame, (80, 60), 10,  color(high), -1)


            roiX = roi[0] + roi[2] // 2
            roiY = roi[1] + roi[3] // 2
            height, width = frame.shape[:2]
            centerX = int(width / 2)
            centerY = int(height / 2)
            TOLERANCE = 15
            roiHorizontal = centerX - roiX
            roiVertical = centerY - roiY
            if roiHorizontal > TOLERANCE :
                drawHorizontalLed(True, False, False)
            elif roiHorizontal < -TOLERANCE :
                drawHorizontalLed(False, False, True)
            else :
                drawHorizontalLed(False, True, False)

            if roiVertical > TOLERANCE :
                drawVerticalLed(True, False, False)
            elif roiVertical <- TOLERANCE :
                drawVerticalLed(False, False, True)
            else :
                drawVerticalLed(False,  True, False)

        drawLeds(frame, regionsOfInterest[0])


        # Draw the center of the image
        height, width = frame.shape[:2]
        centerX = int(width / 2)
        centerY = int(height / 2)
        cv2.circle(frame, (centerX, centerY), 20, red)
        cv2.line(frame, (0, centerY), (width, centerY), red)
        cv2.line(frame, (centerX, 0), (centerX, height), red)

        # How many ROIs?
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # msg = "Found {0} ROIs!".format(len(regionsOfInterest))
        # cv2.putText(frame, msg, (10, 50), font, 2, red, 2, cv2.CV_AA)

        # Highlight the first ROI
        def tryROIMessage(rois):
            if len(rois) > 0:
                roi = rois[0]
                roiCenterX = roi[0] + (roi[2] // 2)
                roiCenterY = roi[1] + (roi[3] // 2)
                locMsg = "Center of first ROI is at [{0},{1}]".format(roiCenterX, roiCenterY)
                return locMsg
            return None

        # roiMsg = tryROIMessage(regionsOfInterest)
        #if (roiMsg is not None):
        #    cv2.putText(frame, roiMsg, (10, 100), font, 2, red, 2, cv2.CV_AA)

        return frame

    def CaptureLoop(self):
        for frame in self.CaptureGenerator():
            output = self.Overlay(* self.BrightestRegion(frame))

            self.Display(output)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

def main(argv=None):
    vision = Vision(0)
    vision.CaptureLoop()

main()

if __name__ == "__main__":
    main()