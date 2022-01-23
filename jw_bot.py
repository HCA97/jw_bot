from statistics import median
from turtle import pos
import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time
import pytesseract
from skimage import measure, morphology, feature, color, filters
from scipy import ndimage


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
        self.battery_loc = (75, 76, 360, 420)
        # self.supply_drop_text_loc = (170, 217, 140, 310)

        # color
        # (R_min, G_min, B_min, R_max, G_max, B_max)
        # (R, G, B)
        self.special_event_color = (0, 180, 0, 50, 255, 30)
        self.supply_drop_color = (200, 100, 0, 255, 160, 60)
        self.x_button_color = (117, 10, 10)
        self.gmap_loc_color = (200, 0, 0, 255, 70, 60)  
        self.coin_color = (180, 160, 100, 240, 220, 120)
        self.battery_color = (10, 30, 80)

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

        pos = []

        # convert background gray
        background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
                                        self.shooting_zone[2]:self.shooting_zone[3]]

        edges = filters.sobel(background_cropped)

        mask = (edges[:,:,0] <= 0.089) * \
                (edges[:,:,1] <= 0.089) * \
                (edges[:,:,2] <= 0.089) 
        mask = filters.median(mask, np.ones((3, 3)))
        mask = morphology.binary_closing(mask, np.ones((5, 5)))
        
        # connected components
        labels = measure.label(mask, background=0, connectivity=2)
        dist = ndimage.distance_transform_edt(mask)

        # find center of mass
        for label in range(1, labels.max()+1):
            label_dist = dist * (labels == label).astype(np.uint8)
            row, col = np.unravel_index(label_dist.argmax(), label_dist.shape)
            pos.append([self.shooting_zone[0] + row, 
                        self.shooting_zone[2] + col])

        # import matplotlib.pyplot as plt
        # plt.figure(1)
        # plt.imshow(dist)
        # plt.figure(4)
        # plt.imshow(labels)
        # plt.figure(5)
        # plt.imshow(mask)        

        # plt.figure(2)
        # plt.imshow(edges)
        
        # plt.show()
        return pos  


    def determine_state(self, background):
        """After you click determine is this supply drop/dino/coin chase etc."""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        state = ""

        custom_config = r'--oem 3 --psm 1'
    
        launch_button = background[self.launch_button_loc[0]:self.launch_button_loc[1], 
                                self.launch_button_loc[2]:self.launch_button_loc[3]].astype(np.uint8)
        
        supply_drop = background[self.supply_drop_text_loc[0]:self.supply_drop_text_loc[1],
                                self.supply_drop_text_loc[2]:self.supply_drop_text_loc[3]]

        text1 = "".join(pytesseract.image_to_string(launch_button, config = custom_config).split())
        text2 = "".join(pytesseract.image_to_string(supply_drop, config = custom_config).split())

        # print(text1, " - ", text2)
        if "LAUNCH" in text1:
            state = "dino"
        elif "EVENT" in text2 or \
            "PECIALEVENT" in text2 or \
            text2 == "SPECIALEVENT" or \
            "DROP" in text2 or \
            text2 == "SUPPLYDROP":
            state = "supply"
        elif "COIN" in text2 or "CHASE" in text2:
            state = "coin"
        # elif text2 
        return state

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
        else:
            raise KeyboardInterrupt("Cannot find google map location")

        # press ctrl + shift + 2 to go back to game
        pyautogui.keyDown('ctrl') 
        time.sleep(0.1)

        pyautogui.keyDown('shift') 
        time.sleep(0.1)

        pyautogui.press('2')
        time.sleep(0.1)

        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')
        time.sleep(5)

        # click launch button incase we move so far
        if self.moved_too_far():
            print("--"*10)
            print("MOVED TO FAR")
            pos = ((self.launch_button_loc[1] + self.launch_button_loc[0])/2, 
                   (self.launch_button_loc[3] + self.launch_button_loc[2])/2)
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)

    def moved_too_far(self):
        """"Detects when we move to far."""
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        color = background[551, 165, :]
        # print(color)
        if 120 > color[0] > 100 and \
           10 > color[1] > 0 and \
           10 > color[2] > 0:
           return True
        return False

    def get_battery_left(self, background):

        # crop battery
        battery = background[self.battery_loc[0]:self.battery_loc[1],
                             self.battery_loc[2]:self.battery_loc[3]]

        # get length
        mask = (battery[:,:,0] <= self.battery_color[0]) * \
                (battery[:,:,1] <= self.battery_color[1]) * \
                (battery[:,:,2] <= self.battery_color[2])
        line_length = 0
        if np.sum(mask) > 0:
            _, cols = np.where(mask)
            line_length = cols.max() - cols.min()

        # normalize as percentage
        return 1 - (line_length /  (self.battery_loc[2] - self.battery_loc[3]))

    def shoot_dino(self):

        def dino_location(background, shift):
            pos = []


            mask = (background[:,:,0] >= 100) * \
                   (background[:,:,1] >= 140) * \
                   (background[:,:,2] >= 180)  

            mask = morphology.binary_opening(mask, np.ones((1, 5)))
            mask = morphology.binary_opening(mask, np.ones((5, 1)))

            dist = ndimage.distance_transform_edt(mask)
            if np.sum(mask) > 0:
                # labels = measure.label(mask)
                rows, cols = np.where(dist >= np.max(dist))
                pos = [shift + np.mean(rows), np.mean(cols)]

                # import matplotlib.pyplot as plt
                # plt.figure(1)
                # plt.imshow(mask)
                # plt.figure(2)
                # plt.imshow(dist)
                # plt.show()


            return pos

        shift = 250
        D = 20
        S = 5
        v_max = 10
        ms = 0.1
        
        # detect dart location 
        dart_loc = [428, 225] # dart_location(background_cropped, shift)
        prev_dino_loc = None
        vel = [0, 0]


        b_curr = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        b_prev = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        

        cx = (self.launch_button_loc[2] + self.launch_button_loc[3]) / 2
        cy = (self.launch_button_loc[0] + self.launch_button_loc[1]) / 2
        pyautogui.moveTo(self.x+cx, self.y+cy, 1)  
        pyautogui.mouseDown()
        time.sleep(0.5)
        # pyautogui.mouseUp()
        # time.sleep(0.1)
        # pyautogui.mouseDown()

        while not self.background_changed(b_curr, b_prev, 2500):
            
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            b_prev = b_curr
            b_curr = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            

            # print(np.mean((b_prev.astype(np.float) - b_curr.astype(np.float))**2))
            background_cropped = b_curr[shift:,:440,:]
            dino_loc = dino_location(background_cropped, shift)

            # print(dino_loc)
            if not dino_loc:
                dino_loc = [prev_dino_loc[0] + vel[0],
                            prev_dino_loc[1] + vel[1]]
            
            dino_2_dart = np.sqrt((dino_loc[0] - dart_loc[0])**2 + (dino_loc[1] - dart_loc[1])**2)
            battery_left = self.get_battery_left(b_curr)

            # check if dino in dart range
            if np.sqrt((dino_loc[0] - dart_loc[0])**2 + (dino_loc[1] - dart_loc[1])**2) <= (D + 10*battery_left):
                print("--"*10)
                print("DINO CLOSE SHOOTING")
                pyautogui.mouseUp()
                time.sleep(0.5)
                pyautogui.moveTo(self.x+cx, self.y+cy, 0.1)  
                pyautogui.mouseDown()
                # time.sleep(0.1)
            else: # if not move screen to dino

                v_max_new = v_max + 5*battery_left

                # predict future location
                dino_loc_pred = [dino_loc[0] + vel[0] * (dino_2_dart / v_max_new),  
                                 dino_loc[1] + vel[1] * (dino_2_dart / v_max_new)] 

                # get direction and multiply with v_max
                dino_pred_2_dart = np.sqrt((dino_loc_pred[0] - dart_loc[0])**2 + (dino_loc_pred[1] - dart_loc[1])**2)
                x_v =  v_max_new * (dino_loc_pred[1] - dart_loc[1]) / dino_pred_2_dart
                y_v =  v_max_new * (dino_loc_pred[0] - dart_loc[0]) / dino_pred_2_dart

                # if we are to close move slower
                slow_down_speed = min(1, (dino_2_dart/(S*D)))
                mouse_pos = pyautogui.position()
                # print("vel", vel, "dino", dino_loc, 
                #         "dino_pred", dino_loc_pred, "dart", dart_loc, "dist", dino_2_dart)
                # don't go outside the screen
                # print(mouse_pos[0] + x_v*T, self.x, self.x + self.w)
                # print(mouse_pos[1] + y_v*T, self.y, self.y + self.h)

                dx = min(max(mouse_pos[0] + x_v*slow_down_speed, self.x), self.x + self.w)
                dy = min(max(mouse_pos[1] + y_v*slow_down_speed, self.y), self.y + self.h)

                # print(mouse_pos, (dx, dy))
                pyautogui.moveTo(dx, dy, ms)
            
            # time.sleep(0.25)

            if prev_dino_loc:
                vel = [dino_loc[0] - prev_dino_loc[0], dino_loc[1] - prev_dino_loc[1]]
            prev_dino_loc = dino_loc
            # print("DIST", np.mean((b_prev.astype(np.float) - b_curr.astype(np.float))**2))
        # print("DONE")

        time.sleep(10) 
        pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)  


        # pos2.append(pos)
        # print(pos2)
        # if pos2:
        #     pos = [pos] + [pos2]
        # else:
        #     pos =[pos]
        # print(pos)
        # return pos

        # curr_dart_loc = None
        # prev_dart_loc = None
        # dart_vel = None

        # curr_dino_loc = None
        # prev_dino_loc = None
        # dino_vel = None

        # mouse press on

        # detect dino


        # move there


        # shot when dart at dino location


        # repeat


    def background_changed(self, b1, b2, threshold=1000):
        """Compare difference between two frames"""
        diff = (b1.astype(np.float) - b2.astype(np.float))**2
        return np.mean(diff) > threshold

    def collect_coin(self):
        pass
    
    def collect_dino(self):
        """"Finds and shoots the dino"""
        
        something_there = False

        # get dinos
        background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        dino_pos = self.detect_dino(background_old)
        for pos in dino_pos:
            # pos = dino_pos[0]
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)
            
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)
            # print(state)
            if state == "dino":
                cx = (self.launch_button_loc[2] + self.launch_button_loc[3]) / 2
                cy = (self.launch_button_loc[0] + self.launch_button_loc[1]) / 2
                pyautogui.click(x=self.x+cx, y=self.y+cy)  
                time.sleep(7)
                self.shoot_dino()
                something_there = True
                # break
            elif not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
            else:
                pos = self.locate_x_button(background_new)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)  

        return something_there

    def collect_supply_drop(self):
        """"Collects supply drops"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        # return value
        something_there = False

        # use old background to determine stop clicking
        background_old= np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))        
        supply_drop_pos = self.detect_supply_drop(background_old)
        
        # loop until you click supply drop
        for pos in supply_drop_pos:
            
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)

            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)
            count = 0
            if state == "supply":
                print("--"*10)
                print("CLICKING SUPPLY DROP")

                # activate the supply drop
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)  
                time.sleep(2) 

                background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                # loop until max click is reached or we are in the old background
                while self.max_click >= count and \
                      self.background_changed(background_old, background_new):
                    print("--"*10)
                    print("CLICK")
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    time.sleep(1.5) 
                    background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                    count += 1

                # if clicked more than max amount something is wrong
                if count > self.max_click:
                    pos = self.locate_x_button(background_new)
                    if pos:
                        pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                        time.sleep(1) 
                    # else:
                    #     raise KeyboardInterrupt("Problem clicking on the supply drop")
                else:
                    something_there = True

            elif not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
            else:
                print("--"*10)
                print("NOT SUPPLY DROP")
                # find x button if not there click on map button
                pos = self.locate_x_button(background_new)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)                                       

        return something_there