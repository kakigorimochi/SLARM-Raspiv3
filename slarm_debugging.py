#!/usr/bin/python3
### Speed Limit Auditory Reminder for Motorcycles ###
###################################################
## libraries to be imported to the project

import RPi.GPIO as GPIO
import cv2 as cam
import numpy as np
import serial as ard
import time as thread
import simpleaudio as audio


###################################################
##global variables

#ultrasonic
ULTRASONIC_TRIG = 23
ULTRASONIC_ECHO = 24
ULTRASONIC_TOUT = 0.04

#waterdata
FLOODDATA_RESULT = ["OO","LO","MI","HI"]
FLOODDATA_STRICT = 50
FLOODDATA_HI = 12
FLOODDATA_MI = 21
FLOODDATA_LO = 30

#rainintensity
RAININTENSITY_OFFSET = 50
RAININTENSITY_HI = 45
RAININTENSITY_MI = 65
RAININTENSITY_LO = 70

#floodheight audio
FLOOD_H = ("resources/audio/f_heavy.wav")
FLOOD_M = ("resources/audio/f_moderate.wav")
FLOOD_L = ("resources/audio/f_light.wav")

#rainintensity audio
RAININT_H = ("resources/audio/r_heavy.wav")
RAININT_M = ("resources/audio/r_moderate.wav")
RAININT_L = ("resources/audio/r_light.wav")

#speedlimit audio
SPEED_50 = ("resources/audio/w_50kph.wav")
SPEED_40 = ("resources/audio/w_40kph.wav")
SPEED_30 = ("resources/audio/w_30kph.wav")
SPEED_20 = ("resources/audio/w_20kph.wav")
SPEED_10 = ("resources/audio/w_10kph.wav")

#roadtype
ROADTYPE_ASPHALT = ["(0, 0, 4)", "(255, 255, 255)", "(85, 85, 85)", "(32, 30, 29)", "(46, 44, 44)", "(83, 79, 78)", "(51, 49, 48)", "(31, 28, 27)", "(57, 55, 54)", "(46, 44, 43)", "(29, 27, 26)", "(57, 54, 53)"]
ROADTYPE_CEMENT = ["(0, 0, 0)","(220, 216, 215)", "(103, 103, 103)", "(178, 190, 181)", "(184, 182, 182)", "(184, 180, 179)", "(231, 230, 229)", "(204, 204, 204)", "(136, 134, 133)", "(176, 172, 171)", "(174, 168, 167)"]
ROADTYPE_TYPES = ["UNKNOWN", "ASPHALT", "CEMENT"]


###################################################
##program settings

#show camera on desktop
SHOWCAMERA = 0
#number of camera color scans before skipping if none matched
NOSCAN_CAMERA = 30
#seconds before re-scan of slarm
SECONDS_INB4 = 0
#averages floodheight value for accuracy reasons
AVERAGE_NUM = 100

###################################################
## FUNCTIONS / PROGRAMME LOGIC

def ULTRASONIC_SCAN():
    #init ultrasonic pins on every function call to have fresh data
    GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)

    #fires a pulse wave to be recorded for distance from the road to the motorcycle
    GPIO.output(ULTRASONIC_TRIG, False)
    thread.sleep(0.01)
    GPIO.output(ULTRASONIC_TRIG, True)
    thread.sleep(0.00001)
    GPIO.output(ULTRASONIC_TRIG, False)

    #records pulsewave activity from start to finish
    pulseStart = thread.time()
    pauseTime = pulseStart + ULTRASONIC_TOUT    
    while GPIO.input(ULTRASONIC_ECHO) == 0 and pulseStart < pauseTime:
        pulseStart = thread.time()

    pulseStops = thread.time()
    pauseTime = pulseStops + ULTRASONIC_TOUT   
    while GPIO.input(ULTRASONIC_ECHO) == 1 and pulseStops < pauseTime:
        pulseStops = thread.time()

    #time difference from start to finish and applies a formula to calculate total distance
    pulseDuration = pulseStops - pulseStart
    totalDistance = pulseDuration * 17000
    totalDistance = round(totalDistance, 0)
    
    return totalDistance


def GET_FLOODHEIGHT():
    FLOODHEIGHT = 0
    DISPOSABLE_VAR = 0
    
    #this runs for x times define in program settings AVERAGE NUM
    while DISPOSABLE_VAR < AVERAGE_NUM:
        FLOODHEIGHT = FLOODHEIGHT + ULTRASONIC_SCAN()
        DISPOSABLE_VAR += 1
    
    #averages and return of value
    AVG_FLOODHEIGHT = int(FLOODHEIGHT / AVERAGE_NUM)
    print ("A. FLOODHEIGHT: ", AVG_FLOODHEIGHT)
    
    return AVG_FLOODHEIGHT


def GET_FLOODDATA(FLOODDATA):
    print ("B. FLOODDATA RETURN")
    
    #check if the data received is not greater than the limit
    #0 - NONE | 1 - LIGHT | 2 - MODERATE | 3 - HEAVY | 4 - ERROR
    if FLOODDATA <= FLOODDATA_STRICT:       
        if FLOODDATA <= FLOODDATA_HI:
            return 3
        elif FLOODDATA <= FLOODDATA_MI:
            return 2
        elif FLOODDATA <= FLOODDATA_LO:
            return 1
        elif FLOODDATA > FLOODDATA_LO:
            return 0  
        else:
            return 4
    else:
        return 4 
    

def GET_RAININTENSITY():
    #makes arduino re-init after powering for data accuracy and not prone to errors
    arduino = ard.Serial('/dev/ttyACM0', 9600)
    thread.sleep(1)
    
    while True:
        #waits for the arduino to send something
        if (arduino.in_waiting > 0):
            AVERAGE_RAININTENSITY = float(arduino.readline().decode('latin1'))
            AVERAGE_RAININTENSITY = int(AVERAGE_RAININTENSITY - RAININTENSITY_OFFSET)
            
            #if no data is received the loop restarts
            if not AVERAGE_RAININTENSITY:
                continue
            else:
                break
    
    print ("D. AVERAGE RAININTENSITY: ", AVERAGE_RAININTENSITY)
    return AVERAGE_RAININTENSITY


def GET_FLOODHEIGHTNINTENSITYFORRAIN(ROADTYPE_VALUE, FLOODTYPE_VALUE):
    #fetch rainintensity and display useful info for debugging
    INTENSITYDATA = GET_RAININTENSITY()
	RAININTPERCNT = (INTENSITYDATA / 127) * 100
			
    print ("E. SELECTING AUDIO FOR RESULT! RAIN INTENSITY: ", "{:.0%}".format(RAININTPERCNT),"| TYPE: ", ROADTYPE_VALUE,"| HEIGHT: ", FLOODDATA_RESULT[FLOODTYPE_VALUE], " | AVAILABLE: ", ROADTYPE_TYPES[0], ROADTYPE_TYPES[1], ROADTYPE_TYPES[2])
    
    #if flood height is light/moderate/heavy
    if FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI":           
        GET_NOTIFICATIONAUDIO("F_HEAVY")
    elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI":
        GET_NOTIFICATIONAUDIO("F_MODERATE")
    elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO":            
        GET_NOTIFICATIONAUDIO("F_LIGHT")

    #if rain intensity is light/moderate/heavy
    if INTENSITYDATA <= RAININTENSITY_HI:           
        GET_NOTIFICATIONAUDIO("R_HEAVY")
    elif INTENSITYDATA <= RAININTENSITY_MI:
        GET_NOTIFICATIONAUDIO("R_MODERATE")
    elif INTENSITYDATA <= RAININTENSITY_LO:            
        GET_NOTIFICATIONAUDIO("R_LIGHT")
    
    #speed limit to be applied overall to the data collected
    # asphalt road
    if ROADTYPE_TYPES[1] == ROADTYPE_VALUE:
        if FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI" and INTENSITYDATA <= RAININTENSITY_HI:
            GET_NOTIFICATIONAUDIO("SPD10")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI" and INTENSITYDATA <= RAININTENSITY_MI:
            GET_NOTIFICATIONAUDIO("SPD20")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI" and INTENSITYDATA <= RAININTENSITY_LO:
            GET_NOTIFICATIONAUDIO("SPD30")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI" and INTENSITYDATA <= RAININTENSITY_HI:
            GET_NOTIFICATIONAUDIO("SPD20")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI" and INTENSITYDATA <= RAININTENSITY_MI:
            GET_NOTIFICATIONAUDIO("SPD30")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI" and INTENSITYDATA <= RAININTENSITY_LO:
            GET_NOTIFICATIONAUDIO("SPD40")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO" and INTENSITYDATA <= RAININTENSITY_HI:
            GET_NOTIFICATIONAUDIO("SPD30")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO" and INTENSITYDATA <= RAININTENSITY_MI:
            GET_NOTIFICATIONAUDIO("SPD40")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO" and INTENSITYDATA <= RAININTENSITY_LO:
            GET_NOTIFICATIONAUDIO("SPD50")

    # cement / undefined road
    elif ROADTYPE_TYPES[2] == ROADTYPE_VALUE or ROADTYPE_TYPES[0] == ROADTYPE_VALUE:
        if FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI" and INTENSITYDATA <= RAININTENSITY_HI:
            GET_NOTIFICATIONAUDIO("SPD20")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI" and INTENSITYDATA <= RAININTENSITY_MI:
            GET_NOTIFICATIONAUDIO("SPD30")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "HI" and INTENSITYDATA <= RAININTENSITY_LO:
            GET_NOTIFICATIONAUDIO("SPD40")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI" and INTENSITYDATA <= RAININTENSITY_HI:
            GET_NOTIFICATIONAUDIO("SPD30")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI" and INTENSITYDATA <= RAININTENSITY_MI:
            GET_NOTIFICATIONAUDIO("SPD40")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "MI" and INTENSITYDATA <= RAININTENSITY_LO:
            GET_NOTIFICATIONAUDIO("SPD50")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO" and INTENSITYDATA <= RAININTENSITY_HI:
            GET_NOTIFICATIONAUDIO("SPD30")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO" and INTENSITYDATA <= RAININTENSITY_MI:
            GET_NOTIFICATIONAUDIO("SPD40")
        elif FLOODDATA_RESULT[FLOODTYPE_VALUE] == "LO" and INTENSITYDATA <= RAININTENSITY_LO:
            GET_NOTIFICATIONAUDIO("SPD50")


def GET_NOTIFICATIONAUDIO(PLAYAUDIO):
    print ("F. PLAYING AUDIO: ", PLAYAUDIO)
    
    #plays audio requested by the program
    if PLAYAUDIO == "F_LIGHT":
        session = audio.WaveObject.from_wave_file(FLOOD_L)       
    elif PLAYAUDIO == "F_MODERATE":
        session = audio.WaveObject.from_wave_file(FLOOD_M)
    elif PLAYAUDIO == "F_HEAVY":
        session = audio.WaveObject.from_wave_file(FLOOD_H)
    elif PLAYAUDIO == "R_LIGHT":
        session = audio.WaveObject.from_wave_file(RAININT_L)
    elif PLAYAUDIO == "R_MODERATE":
        session = audio.WaveObject.from_wave_file(RAININT_M)
    elif PLAYAUDIO == "R_HEAVY":
        session = audio.WaveObject.from_wave_file(RAININT_H)
    elif PLAYAUDIO == "SPD50":
        session = audio.WaveObject.from_wave_file(SPEED_50)    
    elif PLAYAUDIO == "SPD40":
        session = audio.WaveObject.from_wave_file(SPEED_40)   
    elif PLAYAUDIO == "SPD30":
        session = audio.WaveObject.from_wave_file(SPEED_30)    
    elif PLAYAUDIO == "SPD20":
        session = audio.WaveObject.from_wave_file(SPEED_20)    
    elif PLAYAUDIO == "SPD10":
        session = audio.WaveObject.from_wave_file(SPEED_10)
    
    #display if there is something wrong
    else:
        print ("G. PLAYING AUDIO ERROR!")
        
    notif = session.play()
    notif.wait_done()
    

def GET_CAMERACOLOR():
    TIMEOUT = 0

    #initialize camera for scanning
    frames = cam.VideoCapture(0)
    
    while True:
        ret, frame = frames.read()

        #reads camera resolution output  
        height, width, channels = frame.shape
        h_mid = int(height / 2)
        w_mid = int(width / 2)
        
        #camera displays on desktop if true(1) or hidden if false(0) in global settings SHOWCAMERA
        #useful for debugging
        if SHOWCAMERA:
            cam.imshow('frame', frame)

        #flips bgr value to rgb and is combined into a single string    
        rgb = cam.cvtColor(frame, cam.COLOR_RGB2BGR)        
        red, green, blue = (rgb[h_mid, w_mid])        
        COLORDATA = (red, green, blue)
        
        #rgb data parsed ready to be compared with data in array of ROADTYPE ASPHALT AND CEMENT
        COLORPARSED = str(COLORDATA)      
        print ("J. RGBHEX DATA: ", COLORPARSED)
        
        if COLORPARSED in ROADTYPE_ASPHALT or COLORPARSED in ROADTYPE_CEMENT:
            if COLORPARSED in ROADTYPE_CEMENT:
                ROADTYPE_DATA = ROADTYPE_TYPES[2]
                break
            if COLORPARSED in ROADTYPE_ASPHALT:
                ROADTYPE_DATA = ROADTYPE_TYPES[1]
                break

        #terminates scanning after x amount of time in globalsettings NOSCAN_CAMERA
        #prevents the module from scanning forever if no match in array was found    
        if TIMEOUT == NOSCAN_CAMERA:
            ROADTYPE_DATA = ROADTYPE_TYPES[0]
            break
        
        TIMEOUT = TIMEOUT + 1

    #closes camera to be light on power consumption, returns data and displays useful debbuging info    
    frames.release()
    cam.destroyAllWindows()    
    print ("C. FETCHED COLORDATA: ", COLORPARSED, "| ROADTYPE: ", ROADTYPE_DATA)   
    return ROADTYPE_DATA


def SLARM_MAINPROGRAMME():
    try:     
        print ("\n#####################################\nWELCOME TO SLARM: Starting in a bit..\n#####################################\n")

        #init GPIO pins of the raspberry pi
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)        
        thread.sleep(0.5)
        
        LOGNO = 0
        ISSUED_FLOODDATA = 0
        ROADTYPE_DETECTED = "UNKNOWN"
        
        while True:
            #first reading after init of program
            FLOODDATA = GET_FLOODHEIGHT()
            
            #if reading is greater than limit, program loops until below the limit
            while FLOODDATA > FLOODDATA_STRICT:
                FLOODDATA = GET_FLOODHEIGHT()
                
                #checks if data is less than limit before issuing floodheight data
                #then goes out of the loop
                if FLOODDATA <= FLOODDATA_STRICT:
                    ISSUED_FLOODDATA = GET_FLOODDATA(FLOODDATA)
                    break
                else:
                    continue
            
            #if there is no issued data yet, program issues one
            if ISSUED_FLOODDATA == 0:
                ISSUED_FLOODDATA = GET_FLOODDATA(FLOODDATA)

            #checks if issued data is not over the size of the available results for processing        
            if not ISSUED_FLOODDATA > len(FLOODDATA_RESULT):
                #having no flood below will result into the camera scanning the road type
                #before notifying user for the intensity of rain. otherwise, it will just
                #notifying user of how high the flood on the road is situated
                if FLOODDATA_RESULT[ISSUED_FLOODDATA] == ("OO"):
                    ROADTYPE_DETECTED = GET_CAMERACOLOR()
                    GET_FLOODHEIGHTNINTENSITYFORRAIN(ROADTYPE_DETECTED, ISSUED_FLOODDATA)
                                         
                elif FLOODDATA_RESULT[ISSUED_FLOODDATA] == ("LO") or FLOODDATA_RESULT[ISSUED_FLOODDATA] == ("MI") or FLOODDATA_RESULT[ISSUED_FLOODDATA] == ("HI"):         
                    GET_FLOODHEIGHTNINTENSITYFORRAIN(ROADTYPE_DETECTED, ISSUED_FLOODDATA)
                
                #applies little delay before logging the number of loop occured since the
                #program has ran and reset variables recorded for the next loop
                thread.sleep(1)                
                LOGNO = LOGNO + 1
                FLOODDATA = 0
                ISSUED_FLOODDATA = 0       

            #now that the program has logged the loop and is now ready for another loop
            #program will be idle for the next x seconds defined in global settings SECONDS_INB4    
            if ISSUED_FLOODDATA == 0 and LOGNO >= 1:
                print("H. TIMES LOOPED: ", LOGNO)

                thread.sleep(SECONDS_INB4)
                FLOODDATA = GET_FLOODHEIGHT()

            #only runs when something go wrong within the loop and re-loops back from where it started
            else:
                print ("I. WHILE PRELOOP")


    #quit program by pressing ctrl + c on the keyboard       
    except KeyboardInterrupt:
        print ("\n#####################################\nGOODBYE! Thanks for using this program..")
        GPIO.cleanup()


#calls and starts the whole program
if __name__ == '__main__':
    SLARM_MAINPROGRAMME()
