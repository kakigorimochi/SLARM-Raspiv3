import sys
import time
import pygame
import pygame.camera

COLORVAL_ASPHALT = (0, 0, 0)
COLORVAL_CEMENT = (168, 161, 206)
COLORVAL_DIRT = (102, 51, 0)
COLORVAL_SAND = (255, 230, 179)

pygame.init()
pygame.camera.init()

monitor = pygame.display.set_mode((352,288),0)
xhair = pygame.image.load("resources/image/crosshair.png")

x = 0
y = 0
f = 0

cam_list = pygame.camera.list_cameras()
webcam = pygame.camera.Camera(cam_list[0],(32,24))
webcam.start()

while True:
    frames = webcam.get_image()
    
    livefeed = pygame.transform.scale(frames,(352,288))
    xhairscaled = pygame.transform.scale(xhair,(50,50))
    
    monitor.blit(livefeed,(0,0))
    monitor.blit(xhairscaled, ((monitor.get_width() // 2) - 25, (monitor.get_height() // 2) - 25))
    
    pygame.display.update()
    
    COLORVAL = monitor.get_at((monitor.get_width() // 2, monitor.get_height() // 2))[:3]
    
    print (COLORVAL)
    
    f = f + 1
    
    if COLORVAL == COLORVAL_ASPHALT:
        print (f, ". Asphalt Road")
        time.sleep(5)
        
    if COLORVAL == COLORVAL_CEMENT:
        print (f, ". Cement Road")
        time.sleep(5)
        
    time.sleep(0.01)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            webcam.stop()
            pygame.quit()
            sys.exit()
