#!/usr/bin/env python
import csv, re
from datetime import datetime, timezone

inputFile = "log.csv"
outputFile = "log.adif"

contest = "ARRL-SCR"
# "CLASS-I" for individual.
# "CLASS-C" for club (non-school).
# "CLASS-S-EL" for elementary school.
# "CLASS-S-JH" for middle/intermediate/junior high school.
# "CLASS-S-HS" for senior high school.
# "CLASS-S-UN" for college/university.
category_station = "CLASS-S-HS"
callsign = "W1HLO"
arrl_section = "CT"
email = "girasolia@nfaschool.org"
grid_locator = "FN31xm"
name = "Anthony Girasoli"
club = "Norwich Free Academy Amateur Radio and Engineering Club"
address_1 = "Norwich Free Academy"
address_2 = "305 Broadway"
address_city = "Norwich"
address_state_province = "CT"
address_postalcode = "06360"
address_country = "US"
operators = "W1TTL"
soapbox = "W1HLO -- Calling CQ Since 1944.  Go Wildcats!"

nowtime = datetime.now(timezone.utc).replace(microsecond=0)
hour = str(nowtime.hour)
if (len(hour) == 1):
    hour = "0" + hour

minute = str(nowtime.minute)
if (len(minute) == 1):
    minute = "0" + minute
    
second = str(nowtime.second)
if (len(second) == 1):
    second = "0" + second

todayDate = nowtime.date()

current_zulu_time = hour + ":" + minute + ":" + second + "Z"

# Read log file
logLines = []
    
with open(inputFile, 'r') as fd:
    reader = csv.reader(fd, delimiter=',')
    for row in reader:
        logLines.append(row)
fd.close()

# Write the new log file
logFile = open(outputFile, "w")
logFile.write("Generated on " + str(todayDate) + " at " + current_zulu_time + "\n")
logFile.write("<adif_ver:5>3.1.2\n")
logFile.write("<programid:21>W1TTL Rig Control 1.0\n")
logFile.write("<USERDEF1:1:S>class_sent\n")
logFile.write("<USERDEF2:1:S>class_rcv\n")
logFile.write("<USERDEF3:50:S>qth_sent\n")
logFile.write("<EOH>\n\n")

for logLine in logLines:
    freq = str(logLine[0])
    mo = logLine[1]
    date = str(logLine[2])
    time = str(logLine[3])
    sent_call = logLine[4]
    sent_rst = str(logLine[5])
    sent_class = logLine[6]
    sent_qth = logLine[7]
    rcv_call = logLine[8]
    rcv_rst = str(logLine[9])
    rcv_class = logLine[10]
    rcv_qth = logLine[11]
    
    # Remove the decimal from the frequency
    freq = re.sub('[.]', '', freq)
    
    # Remove the dashes from date
    date = re.sub('[-]', '', date)
    
    logFile.write("<qso_date:" + str(len(date)) + ">" + date + "\n")
    logFile.write("<time_on:" + str(len(time)) + ">" + time + "\n")
    logFile.write("<operator:" + str(len(sent_call)) + ">" + sent_call + "\n")
    logFile.write("<rst_sent:" + str(len(sent_rst)) + ">" + sent_rst + "\n")
    logFile.write("<class_sent:" + str(len(sent_class)) + ">" + sent_class + "\n")
    logFile.write("<qth_sent:" + str(len(sent_qth)) + ">" + sent_qth + "\n")
    logFile.write("<call:" + str(len(rcv_call)) + ">" + rcv_call + "\n")
    #logFile.write("<band:" + str(len(band)) + ">" + band)
    logFile.write("<mode:" + str(len(mo)) + ">" + mo + "\n")
    logFile.write("<freq:" + str(len(freq)) + ">" + freq + "\n")
    logFile.write("<rst_rcvd:" + str(len(rcv_rst)) + ">" + rcv_rst + "\n")
    logFile.write("<class_rcv:" + str(len(rcv_class)) + ">" + rcv_class + "\n")
    logFile.write("<qth:" + str(len(rcv_qth)) + ">" + rcv_qth + "\n")
    
    logFile.write("<eor>\n\n")


logFile.close()