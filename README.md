Tiki Vision 2017
=========================
Raspberry Pi based computer vision for FIRST Steamworks robot

Overview
---
This was Team 3880's first year implementing computer vision. We decided to use Python 2.7 with a Raspberry Pi 3.

After connecting the Pi to the radio, we used network tables to send data from the Pi to the RIO. The goal of the program was to send data to align the turret with the high boiler goal, and to alight our front-mounted gear with the peg.

Hardware
---
* Raspberry Pi 3 - Model B
* USB Camera
* LED halo headlight accent lights -60mm Green

About the USB camera; it is important that the camera you use doesn't auto adjust things like brightness and contrast. Such features result in the program not properly detecting regions of interest (retro-reflective tape)  due to hard coded thresholds.

Hardware Layout
---

Two USB cameras, each with a green LED ring, ran to the Pi. The first camera was centered on the turret's shooter, and the second camera was adjacent to the gear intake and storage mechanism. The Pi and the RoboRIO were both hardwired to the radio.

Requirements
---
* [OpenCV](https://opencv.org/)
* [NumPY](http://www.numpy.org/)
* [Network Tables](https://github.com/robotpy/pynetworktables)
