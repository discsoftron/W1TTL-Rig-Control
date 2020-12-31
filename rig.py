#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
import RPi.GPIO as GPIO
from flask import request
import datetime, csv, os.path
import serial

# Set up GPIO stuff
relay1 = 16 # Pin 16 / GPIO 23
relay2 = 18 # Pin 18 / GPIO 24
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(relay2, GPIO.OUT)

# Set the rig hardware details
rigSerial = serial.Serial('/dev/ttyUSB1', 19200) 
rigType = "ICOM"

# Set file names
configFileName = "rigControl.cfg"
logFile = "log.csv"
tempFileName = "tempFile.txt"

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# Initialize relays
GPIO.output(relay1, GPIO.HIGH)
GPIO.output(relay2, GPIO.HIGH)

def shutdown_server():
    GPIO.cleanup()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#def background_thread():
#    count = 0
#    while True:
#        socketio.sleep(10)
#        count += 1
#        socketio.emit('my_response',
#                      {'data': 'Server generated event', 'count': count},
#                      namespace='/rig')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/shutdown')
def shutdown():
    # Initialize relays
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.HIGH)
    shutdown_server()
    return "server shutdown"

@socketio.on('get_freq', namespace='/rig')
def getFreq(message):
    if (message['data'] == "True"):
        if (rigType == "ICOM"):
            # frequency = rigSerial.write("\xfe\xfe\x80\x00\x03\xfd")
            print "Frequency is: " + str(frequency)
            emit('push_set_freq', {'data': frequency})

@socketio.on('ptt_control', namespace='/rig')
def ptt(message):
    if (message['data'] == "transmit"):
        # The PTT key was clicked
        print "The PTT key was clicked..."
        GPIO.output(relay1, GPIO.LOW)
        emit('ptt_control_response',
             {'data': "transmit"},
             broadcast=True)
    elif (message['data'] == "receive"):
        # The PTT was unclicked
        print "The PTT key was unclicked..."
        GPIO.output(relay1, GPIO.HIGH)
        emit('ptt_control_response',
             {'data': "receive"},
             broadcast=True)
        
@socketio.on('mute_control', namespace='/rig')
def mute(message):
    print "Mute control: " + str(message['data'])
    if (message['data'] == "mute"):
        print "Mute relay is set to: " + str(GPIO.input(relay2))
        # The mute button was clicked
        if (GPIO.input(relay2) == 1):
            # Turn the mute on if it was previously off
            print "Muting..."
            GPIO.output(relay2, GPIO.LOW)
            emit('mute_control_response', {'data': "mute_on"}, broadcast=True)
        elif (GPIO.input(relay2) == 0):
            # Turn off the mute relay if it was previously on
            print "Unmuting..."
            GPIO.output(relay2, GPIO.HIGH)
            emit('mute_control_response', {'data': "mute_off"}, broadcast=True)
        
@socketio.on('push_call', namespace='/rig')
def pushCall(message):
    # send the call sign to the form
    emit('push_call_form', {'callSignPush': message['callSign']}, broadcast=True)
    
@socketio.on('submit_msg', namespace='/rig')
def pushMessageBox(message):
    # Write the message to the message box file

    # send the message to the form
    emit('push_msg_box', {'messageBox': message['messageBox']}, broadcast=True)

@socketio.on('submit_entry', namespace='/rig')
def entry(message):
    freq = message['freq']
    mode = message['mode']
    call = message['call']
    rst_sent = message['rst_sent']
    rst_rcvd = message['rst_rcvd']
    station_class = message['station_class']
    qth = message['qth']
    name = message['name']
    op = message['op']
    
    nowtime = datetime.datetime.now().replace(microsecond=0)
    # Prepend a zero to the hour or minute if needed
    hour = str(nowtime.hour)
    if (len(hour) == 1):
        hour = "0" + hour
    
    minute = str(nowtime.minute)
    if (len(minute) == 1):
        minute = "0" + minute
    
    hourMin = hour + minute
    date = nowtime.date()
    localCall = "W1HLO"
    localClass = "S"
    localQth = "CT"
    
    # Append log entry to text file
    logRow = [freq, mode, date, hourMin, localCall, rst_sent, localClass, localQth, call, rst_rcvd, station_class, qth, name, op]
    
    with open(logFile, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(logRow)
    fd.close()
    
    # Read whole text file and format to html table
    logLines = []
    
    with open(logFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logLines.append(row)
    fd.close()
    
    # Reformat the log table in html with the most recent entry at the top
    logTable = "<table class=\"table\"><tr><th>Frequency</th><th>Mode</th><th>Date</th><th>Time</th><th>Call</th><th>RST Sent</th><th>RST Received</th><th>Class</th><th>QTH</th><th>Received Name</th><th>Operator</th></tr>\n"
    logCount = 0
    rowCount = 1
    for row in reversed(logLines):
        newTime = row[3][:2] + ":" + row[3][2:]
        # Fix for old db format that didn't have name and op
        if (len(row) == 12):
            row.append("")
            row.append("")
        qrzCallURL = "<a href=\"https://www.qrz.com/lookup/" + row[8] + "\" target=\"_blank\" rel=\"noopener noreferrer\">" + row[8] + "</a>"
        logTable = logTable + "<tr id=\"logRow-" + str(rowCount) + "\"><td>" + row[0] + "</td><td>" + row[1] + "</td><td>" + row[2] + "</td><td>" + newTime + "</td><td>" + qrzCallURL + "</td><td>" + row[5] + "</td><td>" + row[9] + "</td><td>" + row[10] + "</td><td>" + row[11] + "</td><td>" + row[12] + "</td><td>" + row[13] + "</td></tr>\n"
        logCount = logCount + 1
        rowCount = rowCount + 1
    logTable = logTable + "</table>\n"
    
    emit('update_log', {'logTable': logTable, 'logCount': logCount}, broadcast=True)
    
@socketio.on('get_log', namespace='/rig')
def getLog(message):
    # Get the message from the message box file

    # Get the log file and return it to the user
    logLines = []
    with open(logFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logLines.append(row)
    fd.close()
    
    # Reformat the log table in html with the most recent entry at the top
    logCount = 0
    rowCount = 1
    logTable = "<table class=\"table\"><tr id=\"logTableHead\"><th>Frequency</th><th>Mode</th><th>Date</th><th>Time</th><th>Call</th><th>RST Sent</th><th>RST Received</th><th>Class</th><th>QTH</th><th>Received Name</th><th>Operator</th></tr>\n"
    for row in reversed(logLines):
        newTime = row[3][:2] + ":" + row[3][2:]
        # Fix for old db format that didn't have name and op
        if (len(row) == 12):
            row.append("")
            row.append("")
        qrzCallURL = "<a href=\"https://www.qrz.com/lookup/" + row[8] + "\" target=\"_blank\" rel=\"noopener noreferrer\">" + row[8] + "</a>"
        logTable = logTable + "<tr id=\"logRow-" + str(rowCount) + "\"><td>" + row[0] + "</td><td>" + row[1] + "</td><td>" + row[2] + "</td><td>" + newTime + "</td><td>" + qrzCallURL + "</td><td>" + row[5] + "</td><td>" + row[9] + "</td><td>" + row[10] + "</td><td>" + row[11] + "</td><td>" + row[12] + "</td><td>" + row[13] + "</td></tr>\n"
        logCount = logCount + 1
        rowCount = rowCount + 1
    logTable = logTable + "</table>\n"
    
    emit('load_log', {'logTable': logTable, 'logCount': logCount})
    
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
    
