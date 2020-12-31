#!/usr/bin/env python
import csv, re

inputFile = "log.csv"
outputFile = "log.txt"

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

# Read log file
logLines = []
    
with open(inputFile, 'r') as fd:
    reader = csv.reader(fd, delimiter=',')
    for row in reader:
        logLines.append(row)
fd.close()

# Write the new log file
logFile = open(outputFile, "w")
logFile.write("START-OF-LOG: 3.0\n")
logFile.write("CREATED-BY: W1TTL Rig Control 1.0\n")
logFile.write("CONTEST: " + contest + "\n")
logFile.write("CALLSIGN: " + callsign + "\n")
logFile.write("ARRL-SECTION: " + arrl_section + "\n")
logFile.write("GRID-LOCATOR: " + grid_locator + "\n")
logFile.write("CATEGORY-STATION: " + category_station + "\n")
logFile.write("NAME: " + name + "\n")
logFile.write("OPERATORS: " + operators + "\n")
logFile.write("CLUB: " + club + "\n")
logFile.write("ADDRESS: " + address_1 + "\n")
logFile.write("ADDRESS: " + address_2 + "\n")
logFile.write("ADDRESS-CITY: " + address_city + "\n")
logFile.write("ADDRESS-STATE-PROVICE: " + address_state_province + "\n")
logFile.write("ADDRESS-POSTALCODE: " + address_postalcode + "\n")
logFile.write("ADDRESS-COUNTRY: " + address_country + "\n")
logFile.write("EMAIL: " + email + "\n")
logFile.write("SOAPBOX: " + soapbox + "\n")

totalCount = 0
phCount = 0
cwCount = 0
ryCount = 0
clubs = 0
schools = 0
individuals = 0
numOfStates = 0
numOfProvinces = 0
numOfDX = 0
SCRpoints = 0

CanadianProvinces = ["AB", "BC", "MB", "NB", "NL", "NT", "NS", "NU", "ON", "PE", "QC", "SK", "YT"]
USStates = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
confirmedStates = []
confirmedProvinces = []
confirmedDX = []


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
    
    if (mo == "PH"):
        phCount = phCount + 1
    elif (mo == "CW"):
        cwCount = cwCount + 1
    elif (mo == "RY"):
        ryCount = ryCount + 1
    
    if (rcv_qth in USStates) and (rcv_qth not in confirmedStates):
        confirmedStates.append(rcv_qth)
    elif (rcv_qth in CanadianProvinces) and (rcv_qth not in confirmedProvinces):
        confirmedProvinces.append(rcv_qth)
    elif (rcv_qth == "DX") and (rcv_qth not in confirmedDX):
        confirmedDX.append("DX")
        
    if (rcv_class == "C"):
        clubs = clubs + 1;
    elif (rcv_class == "S"):
        schools = schools + 1
    elif (rcv_class == "I"):
        individuals = individuals + 1
    
    # Remove the decimal from the frequency
    freq = re.sub('[.]', '', freq)
    
    # Pad any needed spacing
    freq = freq.rjust(5)
    sent_call = sent_call.ljust(13)
    sent_rst = sent_rst.ljust(3)
    rcv_call = rcv_call.ljust(13)
    rcv_rst = rcv_rst.ljust(3)
    
    logFile.write("QSO: " + freq + " " + mo + " " + date + " " + time + " " + sent_call + " " + sent_rst + " " + sent_class + 
                  " " + sent_qth + " " + rcv_call + " " + rcv_rst + " " + rcv_class + " " + rcv_qth + "\n")

logFile.write("END-OF-LOG: \n")
logFile.close()

totalCount = phCount + cwCount + ryCount
numOfStates = len(confirmedStates)
numOfProvinces = len(confirmedProvinces)
numOfDX = len(confirmedDX)

SCRpoints = ((2 * (cwCount + ryCount)) + (phCount)) * (numOfStates + numOfProvinces + numOfDX + (2 * clubs) + (5 * schools))

print " "
print "Wrote " + str(totalCount) + " QSOs to " + outputFile
print " "
print "CW QSOs: " + str(cwCount)
print "Digital QSOs: " + str(ryCount)
print "Phone QSOs: " + str(phCount)
print " "
print "Number of States: " + str(numOfStates)
print "Number of Provinces: " + str(numOfProvinces)
print "Number of DX: " + str(numOfDX)
print " "
print "Number of Individuals: " + str(individuals)
print "Number of Clubs: " + str(clubs)
print "Number of Schools: " + str(schools)
print " "
print "Total score: " + str(SCRpoints)
print " "
 