#!/usr/bin/env python3
from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
import RPi.GPIO as GPIO
from flask import request
import datetime, csv, os.path
import serial
import configparser

# Set up GPIO pins on Raspberry Pi
relay1 = 16 # Pin 16 / GPIO 23
relay2 = 18 # Pin 18 / GPIO 24
GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay1, GPIO.OUT)
GPIO.setup(relay2, GPIO.OUT)

# Set file names.
configFileName = "rigControl.ini"
logCatalogFile = "logCatalog.csv"
tempFileName = "tempFile.txt"

config = configparser.ConfigParser()
config.read(configFileName)
motd = config['Messages']['motd']
logFileID = config['Log']['LastLogID']
rigType = config['rig']['rigType']
rigUSB = config['rig']['rigUSB']
rigBaudRate = config['rig']['rigBaudRate']

# Open the serial port
rigOK = "False"
rigUSB = "/dev/ttyUSB1"
rigBaudRate = "19200"
if (rigType != "None"):
    try:
        rigSerial = serial.Serial(rigUSB, rigBaudRate) 
        rigOK = "True"
    except:
        print ("Could not open serial port.")

if (rigOK == "True"):
    if (rigType == "ICOM"):
        rigSerial.setDTR(False) # Prevent the rig from transmitting if DTR is used for transmit
        rigSerial.setRTS(False) # Prevent the rig from transmitting if RTS is used for transmit

logFile = logFileID + ".csv"
if not os.path.isfile(logFile):
    # Check if the log catalog exists.  If not, create it...
    if not os.path.isfile(logCatalogFile):
        open(logCatalogFile, 'a').close()
    # Check if the log is in the catalog...
    logFound = False
    with open(logCatalogFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logNameID = row[0]
            logName = row[1]
            if (logNameID == logFileID):
                logFound = True
    fd.close()
    # If the log file was found in the catalog, create it...
    if (logFound == True):
        open(logFile, 'a').close()
    else:
        # If the log file was not in the catalog, add it to the catalog and create the log...
        with open(logCatalogFile, 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(logFileID,"General")
        fd.close()
        open(logFile, 'a').close()

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# Initialize relays (setting the GPIO pin LOW will energize the relays)
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
    session['page'] = "home"
    if session.get('logFileID') is None:
        session['logFileID'] = logFileID
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/logs')
def logs():
    session['page'] = "logs"
    return render_template('logs.html', async_mode=socketio.async_mode)

@app.route('/settings')
def settings():
    session['page'] = "settings"
    
    return render_template('settings.html', async_mode=socketio.async_mode)

@app.route('/shutdown')
def shutdown():
    # Initialize relays
    GPIO.output(relay1, GPIO.HIGH)
    GPIO.output(relay2, GPIO.HIGH)
    shutdown_server()
    return "server shutdown"

@socketio.on('get_station_info', namespace='/rig')
def getStationInfo(message):
    config = configparser.ConfigParser()
    config.read(configFileName)
    
    callSign = config['Station']['callSign']
    name = config['Station']['name']
    club = config['Station']['club']
    address1 = config['Station']['address1']
    address2 = config['Station']['address2']
    city = config['Station']['city']
    stateProvince = config['Station']['stateProvince']
    postalCode = config['Station']['postalCode']
    country = config['Station']['country']
    arrlSection = config['Station']['arrlSection']
    gridLocator = config['Station']['gridLocator']
    soapbox = config['Station']['soapbox']
    motd = config['Messages']['motd']
    
    stationInfo = {'callSign': callSign, 'name': name, 'club': club, 'address1': address1, 'address2': address2, 'city': city, 'stateProvince': stateProvince, 'postalCode': postalCode, 'country': country, 'arrlSection': arrlSection, 'gridLocator': gridLocator, 'soapbox': soapbox, 'motd':motd}
    
    emit('station_info', stationInfo)
    
@socketio.on('update_station_info', namespace='/rig')
def updateStationInfo(message):
    callSign = message['callSign']
    name = message['name']
    club = message['club']
    address1 = message['address1']
    address2 = message['address2']
    city = message['city']
    stateProvince = message['stateProvince']
    postalCode = message['postalCode']
    country = message['country']
    arrlSection = message['arrlSection']
    gridLocator = message['gridLocator']
    soapbox = message['soapbox']
    motd = message['motd']
    
    # Write data to the config file
    config = configparser.ConfigParser()
    config.read(configFileName)
    config['Station']['callSign'] = callSign
    config['Station']['name'] = name
    config['Station']['club'] = club
    config['Station']['address1'] = address1
    config['Station']['address2'] = address2
    config['Station']['city'] = city
    config['Station']['stateProvince'] = stateProvince
    config['Station']['postalCode'] = postalCode
    config['Station']['country'] = country
    config['Station']['arrlSection'] = arrlSection
    config['Station']['gridLocator'] = gridLocator
    config['Station']['soapbox'] = soapbox
    config['Messages']['motd'] = motd
    
    with open(configFileName, 'w') as configFile:
        config.write(configFile)
    configFile.close()
    
    message = {'status': 'Success!'}
    emit('update_station_info_success', message)

@socketio.on('get_freq', namespace='/rig')
def getFreq(message):
    if (message['data'] == "True"):
        if (rigOK == "True"):
            if (rigType == "ICOM"):
                # frequency = rigSerial.write("\xfe\xfe\x80\x00\x03\xfd")
                frequency = rigSerial.write("\xfe\x70\xe0\x03\xfd")
                print ("Frequency is: " + str(frequency))
                emit('display_freq', {'freq': frequency})

@socketio.on('set_freq', namespace='/rig')
def setFreq(message):
    if (rigOK == "True"):
        if (rigType == "ICOM"):
            frequency = message['frequency']
            hex = itobcd(frequency)
            serialData = rigSerial.write("\xfe\xfe\x80\x00\x00"+hex.decode('string_escape')+"\xfd")
            print ("Frequency set to " + str(frequency))
            print ("Message echoed is " + str(serialData))
            
            emit('push_set_freq', {'freq': frequency})

@socketio.on('ptt_control', namespace='/rig')
def ptt(message):
    if (message['data'] == "transmit"):
        # The PTT key was clicked
        print ("The PTT key was clicked...")
        GPIO.output(relay1, GPIO.LOW)
        emit('ptt_control_response',
             {'data': "transmit"},
             broadcast=True)
    elif (message['data'] == "receive"):
        # The PTT was unclicked
        print ("The PTT key was unclicked...")
        GPIO.output(relay1, GPIO.HIGH)
        emit('ptt_control_response',
             {'data': "receive"},
             broadcast=True)
        
@socketio.on('mute_control', namespace='/rig')
def mute(message):
    print ("Mute control: " + str(message['data']))
    if (message['data'] == "mute"):
        print ("Mute relay is set to: " + str(GPIO.input(relay2)))
        # The mute button was clicked
        if (GPIO.input(relay2) == 1):
            # Turn the mute on if it was previously off
            print ("Muting...")
            GPIO.output(relay2, GPIO.LOW)
            emit('mute_control_response', {'data': "mute_on"}, broadcast=True)
        elif (GPIO.input(relay2) == 0):
            # Turn off the mute relay if it was previously on
            print ("Unmuting...")
            GPIO.output(relay2, GPIO.HIGH)
            emit('mute_control_response', {'data': "mute_off"}, broadcast=True)
        
@socketio.on('push_call', namespace='/rig')
def pushCall(message):
    print ("Push call...")
    # send the call sign to the form
    emit('push_call_form', {'callSignPush': message['callSign']}, broadcast=True)
    
@socketio.on('submit_msg', namespace='/rig')
def pushMessageBox(message):
    # Write the message to the message box file
    config = configparser.ConfigParser()
    config.read(configFileName)
    config['Messages']['broadcast'] = message['messageBox']
    with open(configFileName, 'w') as configFile:
        config.write(configFile)
    configFile.close()
    
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
    logFile = session['logFileID'] + ".csv"
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
    logTable = "<table class=\"table table-sm table-striped\"><tr><th>Frequency</th><th>Mode</th><th>Date</th><th>Time</th><th>Call</th><th>RST Sent</th><th>RST Rcv</th><th>Class</th><th>QTH</th><th>Rcv Name</th><th>Operator</th></tr>\n"
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
    # Get the log file and return it to the user
    logLines = []
    logFile = session['logFileID'] + ".csv"
    with open(logFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logLines.append(row)
    fd.close()
    
    # Reformat the log table in html with the most recent entry at the top
    logCount = 0
    rowCount = 1
    logTable = "<table class=\"table tabe-sm table-striped\"><tr id=\"logTableHead\"><th>Frequency</th><th>Mode</th><th>Date</th><th>Time</th><th>Call</th><th>RST Sent</th><th>RST Rcv</th><th>Class</th><th>QTH</th><th>Name Rcv</th><th>Operator</th></tr>\n"
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

@socketio.on('get_log_catalog', namespace='/rig')
def getLogCatalog(message):
    # Get the log catalog and send it back to the browser
    logNameLines = []
    with open(logCatalogFile, 'r') as fd:
        reader = csv.reader(fd, delimiter=',')
        for row in reader:
            logNameID = row[0]
            logName = row[1]
            logNameLines.append(logNameID + "," + logName)
    fd.close()
    
    emit('update_log_catalog', {'logCatalog': logNameLines})
    
@socketio.on('get_config', namespace='/rig')
def getConfig(message):
    # Get any configuration data
    
    config = configparser.ConfigParser()
    config.read(configFileName)
    messageBox = config['Messages']['broadcast']
    motd = config['Messages']['motd']
    rigType = config['rig']['rigType']
        
    # Return the rig usb type and motd
    emit('load_config', {'rigType': rigType, 'motd': motd, 'messageBox': messageBox})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
    
