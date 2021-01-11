# W1TTL-Rig-Control

## Description
W1TTL Rig Control is a web-based collaborative application for amateur radio QSOs.  I created this application so I could remotely teach amateur radio QSOs to students using a conferencing program like Google Meet or Zoom.  I wanted to create a program that was clean and simple where any rig could be used (even a Kenwood TS-820S) and students could key the rig and collaboratively log the QSOs.  When the application is running, anyone can key the rig or mute the rig.  Students can help each other by sending the callsign they think they heard to everyone's web browser.  Also, one student can take on the task of logging the QSO with everyone seeing the updated log once it's been submitted.  Callsigns in the log are hyperlinked to the station's QRZ page.

This application is meant for use with [School Club Roundup](http://www.arrl.org/school-club-roundup) (SCR), so the logging is formatted towards the SCR contest.  There is a Python program included here called export_log.py that will create a log file in Cabrillo format to submit to SCR.  The application's log file is in comma-separated values (csv) format, so it can be edited on the back end for corrections, if needed.

Running on a Raspberry Pi, this program uses Flask and Python on the back end with Javascript/CSS on the front end.  Two relays are controlled by the Pi to provide push-to-talk (PTT) and audio muting.  A separate computer running Google Meet or Zoom (or some other videoconferencing software) with audio input/output jacks is also needed.  This computer takes care of piping the audio from the videoconferencing software to and from the rig.  A webcam can be connected to this computer to face the rig's VFO display.

## Hardware

A Raspberry Pi running Raspbian with Python installed is needed.  This application has been tested on a Raspberry Pi 4.

A relay board like the [ELEGOO 4 Channel Relay Module](https://www.amazon.com/ELEGOO-Channel-Optocoupler-Arduino-Raspberry/dp/B01HEQF5HU/) works great.  This board has opto-isolators to isolate the Raspberry Pi's 3.3V signals from the relays and can be powered by the Raspberry Pi's 5VDC source.  Of course, you can roll your own if you want.  If you decide to use the ELEGOO (or clone) relay module, please be aware that a LOW signal triggers the relay while a HIGH signal puts the relay back in its "rest" state.

**Note:** This program is currently in beta and I am developing the ability for this program to change the frequency on ICOM radios that have a USB connector.  Right now, this functionality doesn't work.  In the future I will also add remote CW keying capabilities.

You will have to look up the pinouts on your radio for the mic jack to see which pins are used for PTT, PTT Ground, Audio In, and Audio Ground.  On a Kenwood 8-pin jack, PTT is pin 2, PTT Ground is pin 8, Audio In is pin 1 and Audio Ground is pin 7.  On a Kenwood 4-pin jack, PTT is pin 3, Audio In is pin 2, and both PTT Ground and Audio Ground are pin 1.  This will vary, of course, from rig brand to brand.

You can wire the audio straight from your computer's audio out jack to your rig's mic in and from your rig's headphones out to your computer's audio in jack.  You just need to be careful of your audio levels on the computer and rig so you are not overdriving your audio circuits.  Eventually, I'll post a schematic for using isolation transformers and trimmer pots to adjust the audio levels.  For the mute control to work, your rig's audio output (e.g., the headphones jack) will connect to the mute relay first and then go on to the line in jack on your computer's sound card.  That way the "Mute" button in the rig control app can mute the rig's audio when pressed.  (Muting just connects the audio line to ground.)

The wiring diagram below shows how the Raspberry Pi is connected to the relay board:
![W1TTL Rig Control_bb](https://user-images.githubusercontent.com/12022870/104232978-18b27500-541f-11eb-8e22-2233f2646915.jpg)

## Software

As root, install Flask and Flask-SocketIO with the following commands:

    sudo pip install flask
    sudo pip install flask-socketio

Create a user called "rig" and clone the W1TTL Rig Control repository into the home directory of rig (or another directory of your choice).  Then, while logged into rig, you can run the application with:

    python rig.py
  
And now W1TTL rig control should be listening on port 5000 and you can connect to it on your browser with http://hostname:5000/

## Files

`rig.py`: The main application file

`motd.txt`: The message of the day -- a file with a single line.  This appears at the top of the web page and cannot be changed by students.

`message.txt`: A message that can be edited within the webpage by anyone.  I usually put a QSO script in here like, "CQ CQ CQ this is W1HLO calling CQ."

`log.csv`: The QSO log in csv format.

`export_log.py`: This will export the QSO log in Cabrillo format with the information needed for submitting directly to SCR.  The exported file will be saved as `log.txt`.

## Configuration

Editing `rig.py` or `export_log.py`, you will see where you can change the relay GPIO pins (if needed) as well as any file names at the top of the program.

