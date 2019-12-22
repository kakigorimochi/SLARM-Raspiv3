import numpy as np
import cv2
import os as eng

eng.environ['SDL_VIDEO_CENTERED'] = '1'

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('frame', frame)
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    height, width, channels = frame.shape
    rs, gs, bs = (rgb[int(height/2), int(width/2)])
    
    clr = (rs ,gs ,bs)
    tng = str(clr)
    print (tng)
    
    if tng == "(240, 255, 255)":
        print ("zoinks")
    
    #print (int(height/2) , int(width/2))
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()