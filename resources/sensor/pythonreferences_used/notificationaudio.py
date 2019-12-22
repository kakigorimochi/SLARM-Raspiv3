import vlc
import time

flood_h = vlc.MediaPlayer("resources/audio/f_heavy.wav")
flood_m = vlc.MediaPlayer("resources/audio/f_moderate.wav")
flood_l = vlc.MediaPlayer("resources/audio/f_light.wav")

FLOODHEIGHT = "moderate"
    
while True:
    if FLOODHEIGHT == "heavy":
        flood_h.play()
        print ("heavy")
    if FLOODHEIGHT == "moderate":
        flood_m.play()
        print ("moderate")
    if FLOODHEIGHT == "light":
        flood_l.play()
        print ("light")
        
    time.sleep(10)
    