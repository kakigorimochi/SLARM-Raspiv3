import time as thread
import serial as ard

arduino = ard.Serial('/dev/ttyACM0', 9600)
thread.sleep(1)

while True:
    #waits for the arduino to send something
    if (arduino.in_waiting > 0):
        AVERAGE_RAININTENSITY = float(arduino.readline().decode('utf-8'))
        AVERAGE_RAININTENSITY = int(AVERAGE_RAININTENSITY - 50)
        
        print ("D. AVERAGE RAININTENSITY: ", AVERAGE_RAININTENSITY)
        ##if no data is received the loop restarts
        #if not AVERAGE_RAININTENSITY:
        #    continue
        #else:
        #    break

#print ("D. AVERAGE RAININTENSITY: ", AVERAGE_RAININTENSITY)
#return AVERAGE_RAININTENSITY
