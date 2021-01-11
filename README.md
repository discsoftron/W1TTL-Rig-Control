# W1TTL-Rig-Control

## Description
W1TTL Rig Control is a web-based collaborative application for amateur radio QSOs.  I created this application so I could remotely teach amateur radio QSOs to students using a conferencing program like Google Meet or Zoom.  I wanted to create a program that was clean and simple where any rig could be used (even a Kenwood TS-820S) and students could key the rig and collaboratively log the QSOs.  When the application is running, anyone can key the rig or mute the rig.  Students can help each other by sending the callsign they think they heard to everyone's web browser.  Also, one student can take on the task of logging the QSO with everyone seeing the updated log once it's been submitted.  Callsigns in the log are hyperlinked to the station's QRZ page.

This application is meant for use with [School Club Roundup](http://www.arrl.org/school-club-roundup), so the logging is formatted towards the SCR contest.  There is a Python program included here called export_log.py that will create a log file in Cabrillo format to submit to SCR.  The application's log file is in comma-separated values (csv) format, so it can be edited on the back end for corrections, if needed.

Running on a Raspberry Pi, this program uses Flask and Python on the back end with Javascript/CSS on the front end.  Two relays are controlled by the Pi to provide push-to-talk (PTT) and audio muting.  

## Hardware

A Raspberry Pi running Raspbian with Python installed is needed.  This application has been tested on a Raspberry Pi 4.

A relay board like the [ELEGOO 4 Channel Relay Module](https://www.amazon.com/ELEGOO-Channel-Optocoupler-Arduino-Raspberry/dp/B01HEQF5HU/) works great.  This board has opto-isolators to isolate the Raspberry Pi's 3.3V signals from the relays and can be powered by the Raspberry Pi's 5VDC source.  Of course, you can roll your own if you want.  If you decide to use the ELEGOO (or clone) relay module, please be aware that a LOW signal triggers the relay while a HIGH signal puts the relay back in its "rest" state.
