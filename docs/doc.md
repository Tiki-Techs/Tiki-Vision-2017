Additional Documentation
===

File Structure
---
[shooterVision.py](https://github.com/Tiki-Techs/Tiki-Vision-2017/shooterVision.py) was our original program. It took input from a USB camera mounted on our robot's turret with the goal of aligning the turret with the boiler high goal.

[gearVision.py](https://github.com/Tiki-Techs/Tiki-Vision-2017/gearVision.py) was an add on which was never used to competition. Its goal was to align the front of the robot (which held the gear) to the peg on the airship.

[startUp.py](https://github.com/Tiki-Techs/Tiki-Vision-2017/startUp.py) this was a last minute addition when we discovered the Pi wasn't powerful enough to run shooterVision and gearVision simultaneously. It runs on startup, and takes input from the driver through network tables to switch between gearVision and shooterVision. Please note that the majority of this program was written last minute in a hotel room the night before competition and was never perfected or refactored.

[tests](https://github.com/Tiki-Techs/Tiki-Vision-2017/tests) holds a few programs and scripts we used during our testing phase which may be help to you.

Operation & Background
---
Regions of interest (ROIs) are areas detected which contain high amounts of green. This is because retro reflective tape is placed around the high goal and the gear peg. The tape reflects any light shown directly on it, we decided on green as there's not much green on the field. ROIs are determined by HSV thresholds and location in the frame.

To develop our ROI detection algorithm, we prototyped and developed our initial code using [GRIP](https://github.com/WPIRoboticsProjects/GRIP/wiki) (the Graphically Represented Image Processing engine) by WPI Robotics
