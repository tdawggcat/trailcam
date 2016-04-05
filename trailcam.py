#!/usr/bin/python
#
# trailcam.py
#
# Author : Trey Thompson
# Date   : 23 June 2015

# Import required Python libraries
import RPi.GPIO as GPIO
import time
import datetime
import subprocess

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_PIR = 7
UploadToDropBox = 1
Iterations = 0
BasePicPath = "/home/pi/trailcampics/"
DropBoxUploadCommand = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload "
###############################################################################
# Variables/settings for still images
RaspiStill = "/usr/bin/raspistill"
NumPics = 2
CameraTimeDelay = "100"
StillWidth = "640"
StillHeight = "480"
###############################################################################
# Variables/settings for videos
VideoEnabled = 1
RaspiVid = "/usr/bin/raspivid"
VideoWidth = "640"
VideoHeight = "480"
VideoTime = "30000" # in ms
VideoBitRate = "100000" # in bits/second
###############################################################################

print "PIR Module Test (CTRL-C to exit)"

# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)

Current_State  = 0
Previous_State = 0

try:

	print "Waiting for PIR to settle ..."

	# Loop until PIR output is 0
	while GPIO.input(GPIO_PIR)==1:
		Current_State  = 0    

	print "Ready - waiting for motion..."

	# Loop until users quits with CTRL-C
	while True :
		# Read PIR state
		Current_State = GPIO.input(GPIO_PIR)
		Iterations = Iterations + 1
		if Iterations == 1000:
			print "Still waiting..."
			Iterations = 0   
		if Current_State==1 and Previous_State==0:
			# PIR is triggered
			# Record previous state
			Previous_State=1
 			print "Motion detected!"
			PicsTaken = {}
			for x in range (0, NumPics):
				MonthSubFolder = datetime.datetime.now().strftime('%Y%m%d') + "/"
				TimeStamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
				PictureFileName = BasePicPath + MonthSubFolder + TimeStamp + ".jpg"
				RaspiStillCommand = RaspiStill + " -t " + CameraTimeDelay + " -w " + StillWidth + " -h " + StillHeight + " -o " + PictureFileName
				print "Executing -> " + RaspiStillCommand
				subprocess.call (RaspiStillCommand, shell=True)
				PicsTaken[x] = PictureFileName
				time.sleep(0.5)

			if VideoEnabled == 1:
				VideoFileName = BasePicPath + MonthSubFolder + TimeStamp + ".264"
				VideoFileNameMP4 = BasePicPath + MonthSubFolder + TimeStamp + ".mp4"
				RaspiVidCommand = RaspiVid + " -w " + VideoWidth + " -h " + VideoHeight + " -b " + VideoBitRate + " -t " + VideoTime + " -o " + VideoFileName
				subprocess.call (RaspiVidCommand, shell=True)
				MP4BoxCommand = "/usr/bin/MP4Box -fps 30 -add " + VideoFileName + " " + VideoFileNameMP4
				subprocess.call (MP4BoxCommand, shell=True)
			if UploadToDropBox == 1:
				print "Uploading to DropBox"
				#print "Uploading to DropBox"
				for x in range (0, NumPics):
					subprocess.call (DropBoxUploadCommand + PicsTaken[x] + " /Raspi/" + MonthSubFolder, shell=True)
				if VideoEnabled == 1:
					subprocess.call (DropBoxUploadCommand + VideoFileNameMP4 + " /Raspi/" + MonthSubFolder, shell=True)
			print "Sleeping 5 seconds"
			time.sleep(5)
		elif Current_State==0 and Previous_State==1:
			# PIR has returned to ready state
			print "Ready - waiting for motion..."
			Previous_State=0

		# Wait for 10 milliseconds
		time.sleep(0.01)

except KeyboardInterrupt:
	print "Quitting..."
	# Reset GPIO settings
	GPIO.cleanup()
