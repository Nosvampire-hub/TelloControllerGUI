import threading
import pygame
from djitellopy import Tello
import cv2
import time

tello = Tello()
backgroundColour = (0, 0, 0)
textColour2 = (30, 30, 30)
textColour = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)
analog_keys = {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -1}
button_keys = {"cross": 0, "circle": 1, "square": 2, "triangle": 3, "share": 4, "PS": 5, "options": 6, "L3": 7, "R3": 8,
               "L1": 9, "R1": 10, "up": 11, "down": 12, "left": 13, "right": 14, "touch": 15}
running = True
speed = 10

speedMode = "Cruise"
moveMultiplier = 1
pygame.init()
win = pygame.display.set_mode((1200, 720))
pygame.display.set_caption("Tello Pro")
joysticks = []
landed = True
lr, fb, ud, yv = 0, 0, 0, 0
statFont = pygame.font.Font(None, 64)
menuFont = pygame.font.Font(None, 32)
headingFont = pygame.font.Font(None, 96)
menu = True
readoutmenu = headingFont.render("Tello Pro", True, textColour, )
readoutmenuin = headingFont.render("Tello Pro", True, textColour2,)

class button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        if self.text != '':
            font = pygame.font.Font(None, 60)
            text = font.render(self.text, 1, textColour)
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


def connectPs4Cont():
    for i in range(pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i))
    for joystick in joysticks:
        joystick.init()
    print("ye")


def connectTello():
    tello.connect()
    tello.streamon()


ps4Button = button(backgroundColour, 370, 350, 400, 20, 'Connect Controller')
droneButton = button(backgroundColour, 370, 200, 400, 20, 'Connect Tello')
startButton = button(backgroundColour, 450, 500, 250, 20, 'Start!')


def startMenu():
    menu = True
    move = 1
    while menu == True:
        contStat = ""
        telloStat = ""
        win.blit(readoutmenu, (50, 50))
        win.blit(readoutmenuin, (48,48))
        droneButton.draw(win, None)
        ps4Button.draw(win, None)
        startButton.draw(win, None)
        pygame.display.update()
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if ps4Button.isOver(pos):
                    connectPs4Cont()
                if pygame.joystick.get_count() == 0:
                    contStat = ""
                    ps4Button.text = "Try Again"
                else:
                    contStat = "Connected"
                    ps4Button.text = "Connected"

                if droneButton.isOver(pos):
                    try:
                        connectTello()
                        droneButton.text = "Connected"
                        telloStat = "Connected"
                    except:
                        telloStat = ""
                        droneButton.text = "Try Again"
                if startButton.isOver(pos):
                    if telloStat != "Connected":
                        menu = False

                    else:
                        startButton.text = "Please Connect Devices"
                        start = int(startButton.x) - 10

            if event.type == pygame.MOUSEMOTION:
                if ps4Button.isOver(pos):
                    ps4Button.color = red
                else:
                    ps4Button.color = backgroundColour
                if droneButton.isOver(pos):
                    droneButton.color = red
                else:
                    droneButton.color = backgroundColour
                if startButton.isOver(pos):
                    startButton.color = green
                else:
                    startButton.color = backgroundColour
        win.fill(backgroundColour)


def vidstream():
    while running:
        img = tello.get_frame_read().frame
        img = cv2.resize(img, (1200, 600))
        cv2.imwrite("IMG/video.jpg", img)
        img2 = pygame.image.load(r'IMG/video.jpg')
        win.blit(img2, (0, 0))
        pygame.display.update()
        cv2.waitKey(1)


def loadstats():
    while running:
        battery = str(tello.get_battery())
        speedx = str(tello.get_speed_x() * 10)
        speedy = str(tello.get_speed_y() * 10)
        speedz = str(tello.get_speed_z() * 10)
        pygame.draw.rect(win, backgroundColour, pygame.Rect(0, 600, 1200, 120))
        readoutbat = statFont.render("batt= " + battery + "%", True, textColour, backgroundColour)
        win.blit(readoutbat, (100, 601))
        readoutspeed = statFont.render("X= " + speedx + " Y= " + speedy + " Z=" + speedz, True, textColour,
                                       backgroundColour)
        win.blit(readoutspeed, (100, 645))
        readoutMode = statFont.render("Mode= " + speedMode, True, textColour, backgroundColour)
        win.blit(readoutMode, (600, 620))
        pygame.display.update()
        time.sleep(0.1)


refreshstat = threading.Thread(target=loadstats)
playvideo = threading.Thread(target=vidstream)

startMenu()

playvideo.start()

refreshstat.start()


while running:

    for event in pygame.event.get():

        if event.type == pygame.JOYBUTTONDOWN:

            print(event.button)

            if event.button == button_keys["touch"]:
                if landed == True:
                    tello.takeoff()
                    landed = False
                    textColour = (0, 150, 0)
                else:
                    tello.land()
                    landed = True
                    textColour = (255, 255, 255)
            if event.button == button_keys["PS"]:
                tello.land()
                tello.streamoff()
                pygame.quit()
                quit()

            if event.button == button_keys["up"]:
                speed = 100
                speedMode = "Sport"
                tello.set_speed(speed)
                moveMultiplier = 2
                print("speed changed")
                print(speed)

            if event.button == button_keys["down"]:
                speed = 10
                speedMode = "Cruise"
                tello.set_speed(speed)
                moveMultiplier = 1
                print("speed changed")
                print(speed)

            if event.button == button_keys["R1"]:
                tello.flip("r")

            if event.button == button_keys["L1"]:
                tello.flip("l")

        if event.type == pygame.JOYAXISMOTION:

            analog_keys[event.axis] = event.value
            lr = int(analog_keys[0] * 100)  # left right movement int
            fb = int(-analog_keys[1] * 100)  # forward back movement int
            yv = int(analog_keys[2] * 100)  # turn left and right
            L2raw = (int(analog_keys[4] * 100) / 2) + 50
            R2raw = (int(analog_keys[5] * 100) / 2) + 50
            ud = int(R2raw - L2raw)

    if landed == False:
        tello.send_rc_control(lr, fb, ud, yv)
    time.sleep(0.1)
