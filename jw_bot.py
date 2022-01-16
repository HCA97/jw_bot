import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time
import pytesseract
from skimage import measure, morphology, feature, color, filters


# https://stackoverflow.com/questions/50655738/how-do-i-resolve-a-tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class Bot:

    def __init__(self):
        # stores location of the app
        self.x, self.y, self.w, self.h = -1, -1, -1, -1
        self.loc = False

        # pos - x and y change due to image (row = y, col = x)
        # (y_min, y_max, x_min, x_max)
        # (y, x)
        self.shooting_zone = (230, 720, 10, 440)
        self.launch_button_loc = (650, 712, 132, 310)
        self.supply_drop_text_loc = (92, 132, 110, 330)
        self.map_button_loc = (786, 222)
        # self.supply_drop_text_loc = (170, 217, 140, 310)

        # color
        # (R_min, G_min, B_min, R_max, G_max, B_max)
        # (R, G, B)
        self.special_event_color = (0, 180, 0, 50, 255, 30)
        self.supply_drop_color = (200, 100, 0, 255, 160, 60)
        self.x_button_color = (117, 10, 10)
        self.gmap_loc_color = (200, 0, 0, 255, 70, 60)  
        self.coin_color = (180, 160, 100, 240, 220, 120)

        # other
        self.max_click = 4

    def set_app_loc(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.loc = True

    # detection

    def locate_x_button(self, background, button_color=None, shift=712):
        """Locate x button to go back to map"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        if button_color is None:
            button_color = self.x_button_color
            
        button = (background[shift:,:,0] == button_color[0]) * \
                (background[shift:,:,1] == button_color[1]) * \
                (background[shift:,:,2] == button_color[2])

        if np.sum(button) > 0:
            y, x = np.where(button)
            return shift + int(np.mean(y)), int(np.mean(x))
        return None
    
    def detect_supply_drop(self, background):
        """Finds supply drop by simply thresholding, but there might be false positives"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        pos = []

        # threshold + clean up
        background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
                                        self.shooting_zone[2]:self.shooting_zone[3]]
        t1 = (background_cropped[:,:,0] >= self.supply_drop_color[0]) * \
            (background_cropped[:,:,1] >= self.supply_drop_color[1]) * \
            (background_cropped[:,:,2] >= self.supply_drop_color[2]) * \
            (background_cropped[:,:,0] <= self.supply_drop_color[3]) * \
            (background_cropped[:,:,1] <= self.supply_drop_color[4]) * \
            (background_cropped[:,:,2] <= self.supply_drop_color[5])
        t2 = (background_cropped[:,:,0] >= self.special_event_color[0]) * \
            (background_cropped[:,:,1] >= self.special_event_color[1]) * \
            (background_cropped[:,:,2] >= self.special_event_color[2]) * \
            (background_cropped[:,:,0] <= self.special_event_color[3]) * \
            (background_cropped[:,:,1] <= self.special_event_color[4]) * \
            (background_cropped[:,:,2] <= self.special_event_color[5])
        mask = np.logical_or(t1, t2).astype(np.uint8)
        mask = morphology.binary_closing(mask, np.ones((5,5)))
        
        # connected components
        labels = measure.label(mask, background=0, connectivity=2)

        # find center of mass
        for label in range(1, labels.max()+1):
            rows, cols = np.where(labels == label)
            if len(rows) > 20:
                pos.append([self.shooting_zone[0] + int(np.mean(rows)), self.shooting_zone[2] + int(np.mean(cols))])

        return pos

    def detect_coins(self, background):
        """Detects coin chests, but there might be false positives"""
        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        pos = []

        # threshold + clean up
        background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
                                        self.shooting_zone[2]:self.shooting_zone[3]]
        mask = (background_cropped[:,:,0] >= self.coin_color[0]) * \
                (background_cropped[:,:,1] >= self.coin_color[1]) * \
                (background_cropped[:,:,2] >= self.coin_color[2]) * \
                (background_cropped[:,:,0] <= self.coin_color[3]) * \
                (background_cropped[:,:,1] <= self.coin_color[4]) * \
                (background_cropped[:,:,2] <= self.coin_color[5])
        mask = morphology.binary_opening(mask, np.ones((3,3)))
        mask = morphology.binary_closing(mask, np.ones((5,5)))
        # connected components
        labels = measure.label(mask, background=0, connectivity=2)


        # import matplotlib.pyplot as plt
        # plt.figure(2)
        # plt.imshow(labels)
        # plt.show()

        # find center of mass
        for label in range(1, labels.max()+1):
            rows, cols = np.where(labels == label)
            if len(rows) > 20:
                pos.append([self.shooting_zone[0] + int(np.mean(rows)), self.shooting_zone[2] + int(np.mean(cols))])

        return pos

    def detect_dino(self, background):
        """Finds the location of dino but there are false positives need more cleaning"""
        return []   


    def determine_state(self, background):
        """After you click determine is this supply drop/dino/coin chase etc."""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        custom_config = r'--oem 3 --psm 1'
    
        launch_button = background[self.launch_button_loc[0]:self.launch_button_loc[1], 
                                self.launch_button_loc[2]:self.launch_button_loc[3]].astype(np.uint8)
        
        supply_drop = background[self.supply_drop_text_loc[0]:self.supply_drop_text_loc[1],
                                self.supply_drop_text_loc[2]:self.supply_drop_text_loc[3]]

        text1 = "".join(pytesseract.image_to_string(launch_button).split())
        text2 = "".join(pytesseract.image_to_string(supply_drop, config = custom_config).split())

        # print(text1, " - ", text2)
        if text1 == "LAUNCH":
            return "dino"
        elif text2 == "SPECIALEVENT" or text2 == "SUPPLYDROP":
            return "supply"
        elif "COIN" in text2 or "CHASE" in text2:
            return "coin"
        # elif text2 
        return ""

    def change_location(self, r=300):
        """Randomly change location"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        # press ctrl + shift + k to open the map
        pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
        time.sleep(0.5)

        pyautogui.keyDown('ctrl') 
        time.sleep(0.1)

        pyautogui.keyDown('shift') 
        time.sleep(0.1)

        pyautogui.press('k')
        time.sleep(0.1)

        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')
        time.sleep(2) 

        
        # detect current location
        background = np.array(pyautogui.screenshot())
        mask = (background[:,:,0] >= self.gmap_loc_color[0]) * \
                (background[:,:,1] >= self.gmap_loc_color[1]) * \
                (background[:,:,2] >= self.gmap_loc_color[2]) * \
                (background[:,:,0] <= self.gmap_loc_color[3]) * \
                (background[:,:,1] <= self.gmap_loc_color[4]) * \
                (background[:,:,2] <= self.gmap_loc_color[5])
        labels = measure.label(mask)
        mask = labels == np.argmax(np.bincount(labels[labels != 0].flatten()))
        
        # move randomly
        if np.sum(mask) > 0:
            y_, x_ = np.where(mask)
            pos = (y_.mean(), x_.mean())
            
            ang = np.random.uniform(0, 2*np.pi)
            dx = r*np.cos(ang)
            dy = r*np.sin(ang)

            pyautogui.click(x=pos[1] + dx, y=pos[0] + dy)
            time.sleep(2) 

        # press ctrl + shift + 2 to go back to game
        pyautogui.keyDown('ctrl') 
        time.sleep(0.1)

        pyautogui.keyDown('shift') 
        time.sleep(0.1)

        pyautogui.press('2')
        time.sleep(0.1)

        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')
        time.sleep(2)

        # click launch button incase we move so far
        if self.moved_too_far():
            pos = ((self.launch_button_loc[1] + self.launch_button_loc[0])/2, (self.launch_button_loc[3] + self.launch_button_loc[2])/2)
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)

    def moved_too_far(self):
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        color = background[551, 165, :]
        # print(color)
        if 120 > color[0] > 100 and \
           10 > color[1] > 0 and \
           10 > color[2] > 0:
           return True
        return False

    def shoot_dino():
        pass

    def background_changed(self, b1, b2):
        diff = (b1.astype(np.float) - b2.astype(np.float))**2
        print(np.mean(diff))
        return np.mean(diff) > 10000

    def collect_supply_drop(self):

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        background_old= np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        supply_drop_pos = self.detect_supply_drop(background_old)
        something_there = False
        for pos in supply_drop_pos:
            # pos = supply_drop_pos[0]
            
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)

            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)
            count = 0
            if state == "supply":
                print("--"*10)
                print("CLICKING SUPPLY DROP")
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)  
                time.sleep(2) 
                background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

                print(self.background_changed(background_old, background_new))
                while self.max_click >= count and \
                      self.background_changed(background_old, background_new):
                    print("--"*10)
                    print("CLICK")
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    time.sleep(1.5) 
                    background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                    count += 1

                if count > self.max_click:
                    pos = self.locate_x_button(background_new)
                    if pos:
                        pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                        time.sleep(1) 

                something_there = True
            else:
                pos = self.locate_x_button(background_new)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)                                       

        return something_there