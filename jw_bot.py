import time

import matplotlib.pyplot as plt
import pyautogui
import keyboard
import numpy as np
from PIL import Image
import pytesseract
from skimage import measure, morphology, filters, feature, color, transform
from scipy import ndimage

# CHANGE THIS!
# https://stackoverflow.com/questions/50655738/how-do-i-resolve-a-tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class Bot:

    def __init__(self):
        # stores location of the app
        self.x, self.y, self.w, self.h = -1, -1, -1, -1
        self.loc = False


        # get the ratios (I get it from my PC to fit other screen sizes)
        self.shooting_zone_ratio = (230 / 831, 740 / 971, 10 / 481, 410 / 481)
        self.launch_button_loc_ratio = (650 / 831, 712 / 831, 132 / 481, 310 / 481)
        self.supply_drop_text_loc_ratio = (92 / 831, 132 / 831, 110 /481, 330 / 481)
        self.map_button_loc_ratio = (786 / 831, 222 / 481)
        self.battery_loc_ratio = (75 / 831, 76 / 831, 360 / 481, 420 / 481)
        self.dino_loading_screen_loc_ratio = (210 / 831, 230 / 481)  
        self.moved_too_far_loc_ratio = (551 / 831, 165 / 481)
        self.dino_shoot_loc_ratio = (250 / 831, 440 / 481)
        self.dart_loc_ratio = (428 / 831, 225 / 481)
        self.supply_drop_resources_text_loc_ratio = (170 / 890, 240 / 890, 110 / 515, 370 / 515)
        self.supply_drop_resources_amount_loc_ratio = (510 / 890, 565 / 890, 180 / 515, 310 / 515)
        self.dino_collected_text_loc_ratio = (160 / 891, 270 / 891, 50 / 513, 460 / 513)
        # self.dino_collected_text_loc_ratio = (160 / 891, 340 / 891, 50 / 513, 460 / 513)

        self.dino_collected_amount_loc_ratio = (280 / 891, 330 / 891, 210 / 513, 350 / 513)
        self.center_loc_ratio = (587 / 954, 257 / 550)

        # pos - x and y change due to image (row = y, col = x)
        # (y_min, y_max, x_min, x_max)
        # (y, x)
        self.shooting_zone = (230, 720, 10, 440)
        self.launch_button_loc = (650, 712, 132, 310)
        self.supply_drop_text_loc = (92, 132, 110, 330)
        self.map_button_loc = (786, 222)
        self.battery_loc = (75, 76, 360, 420)
        self.dino_loading_screen_loc = (210, 230)
        self.moved_too_far_loc = (551, 165)
        self.dino_shoot_loc = (250, 440)
        self.dart_loc = (428, 225)
        self.supply_drop_resources_text_loc = (170, 240, 110, 370)
        self.dino_collected_text_loc = (160, 270, 50, 460)
        self.dino_collected_amount_loc = (280, 330, 220, 350)
        self.center_loc = (587, 257)
        self.D = 10
        self.v_max = 10
        

        # color
        # (R_min, G_min, B_min, R_max, G_max, B_max)
        # (R, G, B)
        # normal
        self.special_event_color = (0, 160, 0, 50, 255, 50)
        self.supply_drop_color = (200, 100, 0, 255, 200, 60)
        # lunar new year
        # self.special_event_color = (170, 140, 50, 230, 190, 100)
        # self.supply_drop_color = (150, 120, 0, 255, 180, 60)
        # valentine
        # self.special_event_color = (0, 140, 0, 100, 255, 100)
        # self.supply_drop_color = (180, 0, 0, 255, 100, 120)        
        # st. petersburg
        #self.special_event_color = (0, 140, 0, 45, 255, 45)
        #self.supply_drop_color = (60, 60, 0, 210, 210, 120)      

        self.x_button_color = (117, 10, 10)
        self.gmap_loc_color = (200, 0, 0, 255, 70, 60)  
        # default
        self.coin_color = (180, 160, 100, 240, 220, 120)
        # lunar new year
        # self.coin_color = (200, 50, 20, 255, 140, 50)
        # winter games
        # self.coin_color = (20, 35, 130, 95, 95, 170)
        # valentine
        # self.coin_color = (180, 0, 0, 255, 100, 120) 
        # festival
        # self.coin_color = (20, 35, 130, 95, 95, 170)
        # something
        # self.coin_color = (130, 150, 150, 175, 175, 200)
        # self.coin_color = (175, 175, 150, 225, 225, 225)
        # st. petersburg
        # self.coin_color = (60, 60, 0, 210, 210, 120)   

        self.battery_color = (10, 30, 80)
        self.dino_loading_screen_color = (230, 230, 230)

        # other
        self.number_of_scrolls = 0
        self.max_click = 4
        self.custom_config = r'--oem 3 --psm 1'

        # extra stuff
        self.loading_screen_pic = Image.open(r'figs/loading_screen.png')
        #self.moved_too_far_pic = Image.open(r'figs/moved_too_far.PNG')

        # self.coin_chests = [
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_1.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_2.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_3.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_4.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_5.png')),
        # ]

        # self.default_size = ()

        # supply drop templates

        # 
        self.supply_collected = {}
        self.dino_collected = {}


    def set_app_loc(self, x, y, w, h):
        

        # background = np.array(pyautogui.screenshot())
        # fig = plt.figure()
        # plt.imshow(background)
        # plt.title("CLICK TOP RIGHT CORNER THEN BOTTOM LEFT", fontsize=15)


        # def onclick(event):
        #     # print(event)

        #     if self.x == -1 or self.y == -1:
        #         self.x, self.y = event.xdata, event.ydata
        #     elif self.w == -1 or self.h == -1:
        #         self.w = event.xdata - self.x
        #         self.h = event.ydata - self.y
        #         print("DONE")
        #         print("LOC :", self.x, self.y, "SIZE :", self.w, self.h)
        #         fig.canvas.mpl_disconnect(cid)
        #         plt.close()

        # cid = fig.canvas.mpl_connect('button_press_event', onclick)
        # plt.show()

        self.x, self.y, self.w, self.h = x, y, w, h
        print("LOC :", self.x, self.y, "SIZE :", self.w, self.h)

        self.loc = True

        # set location according to my screen little bit off is fine
        self.shooting_zone = (int(self.shooting_zone_ratio[0]*h), 
                              int(self.shooting_zone_ratio[1]*h), 
                              int(self.shooting_zone_ratio[2]*w), 
                              int(self.shooting_zone_ratio[3]*w))
        self.launch_button_loc = (int(self.launch_button_loc_ratio[0]*h), 
                                  int(self.launch_button_loc_ratio[1]*h),
                                  int(self.launch_button_loc_ratio[2]*w),
                                  int(self.launch_button_loc_ratio[3]*w))
        self.supply_drop_text_loc = (int(self.supply_drop_text_loc_ratio[0]*h),
                                     int(self.supply_drop_text_loc_ratio[1]*h),
                                     int(self.supply_drop_text_loc_ratio[2]*w),
                                     int(self.supply_drop_text_loc_ratio[3]*w))
        self.map_button_loc = (int(self.map_button_loc_ratio[0]*h), 
                               int(self.map_button_loc_ratio[1]*w))
        self.battery_loc = (int(self.battery_loc_ratio[0]*h),
                            int(self.battery_loc_ratio[1]*h),
                            int(self.battery_loc_ratio[2]*w),
                            int(self.battery_loc_ratio[3]*w))
        self.dino_loading_screen_loc = (int(self.dino_loading_screen_loc_ratio[0]*h), 
                                        int(self.dino_loading_screen_loc_ratio[1]*w))
        self.moved_too_far_loc = (int(self.moved_too_far_loc_ratio[0]*h), 
                                int(self.moved_too_far_loc_ratio[1]*w))
        self.dino_shoot_loc =(int(self.dino_shoot_loc_ratio[0]*h), 
                                int(self.dino_shoot_loc_ratio[1]*w))
        self.dart_loc = (int(self.dart_loc_ratio[0]*h), 
                        int(self.dart_loc_ratio[1]*w))
        self.supply_drop_resources_text_loc = (int(self.supply_drop_resources_text_loc_ratio[0]*h),
                                                int(self.supply_drop_resources_text_loc_ratio[1]*h),
                                                int(self.supply_drop_resources_text_loc_ratio[2]*w),
                                                int(self.supply_drop_resources_text_loc_ratio[3]*w))
        self.supply_drop_resources_amount_loc = (int(self.supply_drop_resources_amount_loc_ratio[0]*h),
                                                int(self.supply_drop_resources_amount_loc_ratio[1]*h),
                                                int(self.supply_drop_resources_amount_loc_ratio[2]*w),
                                                int(self.supply_drop_resources_amount_loc_ratio[3]*w))        
        self.dino_collected_text_loc = (int(self.dino_collected_text_loc_ratio[0]*h),
                                        int(self.dino_collected_text_loc_ratio[1]*h),
                                        int(self.dino_collected_text_loc_ratio[2]*w),
                                        int(self.dino_collected_text_loc_ratio[3]*w))
        self.dino_collected_amount_loc = (int(self.dino_collected_amount_loc_ratio[0]*h),
                                            int(self.dino_collected_amount_loc_ratio[1]*h),
                                            int(self.dino_collected_amount_loc_ratio[2]*w),
                                            int(self.dino_collected_amount_loc_ratio[3]*w))  
        self.center_loc = (int(self.center_loc_ratio[0]*h), int(self.center_loc_ratio[1]*w))
        self.D = 7 * h / 831 # 10 * h / 831
        self.v_max = 10 * h / 831

        # scroll down
        # pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
        # time.sleep(1)

        # background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        # pos = self.locate_x_button(background)
        # if pos:
        #     pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
        #     time.sleep(1)  

        # pyautogui.moveTo(self.x+self.w//2, self.y+self.h//2, 0.1)
        # pyautogui.keyDown('ctrl') 
        # time.sleep(0.1)
        # for _ in range(5):
        #     pyautogui.scroll(-90)
        #     time.sleep(0.5)
        # pyautogui.keyUp('ctrl')

    # ----------------------------------------------------------
    #   DETECTION
    # ----------------------------------------------------------

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
            if len(rows) > 15:
                pos.append([self.shooting_zone[0] + int(np.mean(rows)), self.shooting_zone[2] + int(np.mean(cols))])

        return pos

    # def detect_coins(self, background):
    #     """Detects coin chests, but there might be false positives"""
    #     if keyboard.is_pressed("q"):
    #         raise KeyboardInterrupt

    #     pos = []
    #     background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
    #                                     self.shooting_zone[2]:self.shooting_zone[3]]
    #     background_cropped_gray = color.rgb2gray(background_cropped)
    #     # import matplotlib.pyplot as plt

    #     pos = []
    #     corr = np.zeros_like(background_cropped_gray)
    #     for template in self.coin_chests:
    #         # for ang in [0, 90, 180, 270]:
    #             # template_gray = color.rgb2gray(transform.rotate(template, ang))
    #         template_gray = color.rgb2gray(template)
    #         # result = feature.match_template(feature.canny(background_cropped_gray, sigma=2), 
    #         #                                 feature.canny(template_gray, sigma=2), mode="reflect")
    #         result = feature.match_template(filters.sobel(background_cropped_gray), 
    #                                         filters.sobel(template_gray), pad_input=True, mode="reflect")
    #         corr += transform.resize(result, corr.shape, anti_aliasing=True)
    #         # corr += feature.match_template(filters.sobel(background_cropped_gray), 
    #         #                                 filters.sobel(template_gray), pad_input=True, mode="reflect")
    #     corr = corr / len(self.coin_chests)
    #     coordinates = feature.peak_local_max(corr, min_distance=50, threshold_abs=0.1)
    #     import matplotlib.pyplot as plt
    #     plt.figure(2)
    #     plt.imshow(corr, vmax=1, vmin=-1)
    #     plt.figure(3)
    #     plt.imshow(background_cropped)
    #     plt.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
    #     plt.figure(4)
    #     plt.imshow(filters.sobel(template_gray))
    #     plt.show()

    #     # # find center of mass
    #     # for label in range(1, labels.max()+1):
    #     #     rows, cols = np.where(labels == label)
    #     #     if len(rows) > 15:
    #     #         pos.append([self.shooting_zone[0] + int(np.mean(rows)), self.shooting_zone[2] + int(np.mean(cols))])

    #     return pos

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

    # ----------------------------------------------------------
    #   OCR
    # ----------------------------------------------------------

    def determine_dino_collected(self, background):
        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        type_text = background[self.dino_collected_text_loc[0]:self.dino_collected_text_loc[1], 
                                self.dino_collected_text_loc[2]:self.dino_collected_text_loc[3]].astype(np.uint8)
        
        amount_text = background[self.dino_collected_amount_loc[0]:self.dino_collected_amount_loc[1],
                                self.dino_collected_amount_loc[2]:self.dino_collected_amount_loc[3]]

        config = '--oem 1 --psm 4'
        key = pytesseract.image_to_string(type_text).split() # "".join(pytesseract.image_to_string(type_text).split()) # , config = self.custom_config).split())
        number = "".join(pytesseract.image_to_string(amount_text, config = config).split())

        print(key, number) 

    def determine_supply_collected(self, background):
        """"Determines which supply collected and how much"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        type_text = background[self.supply_drop_resources_text_loc[0]:self.supply_drop_resources_text_loc[1], 
                                self.supply_drop_resources_text_loc[2]:self.supply_drop_resources_text_loc[3]].astype(np.uint8)
        
        amount_text = background[self.supply_drop_resources_amount_loc[0]:self.supply_drop_resources_amount_loc[1],
                                self.supply_drop_resources_amount_loc[2]:self.supply_drop_resources_amount_loc[3]]

        key = "".join(pytesseract.image_to_string(type_text).split()) # , config = self.custom_config).split())
        number = "".join(pytesseract.image_to_string(amount_text).split()) #, config = self.custom_config).split())

        print(key, number) 
        # don't think about the case when it fails right now  

        try:
            number = int(number[1:])
        except ValueError:
            number = None

        if key and number:
            return key, number
            

    def determine_state(self, background):
        """After you click determine is this supply drop/dino/coin chase etc."""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        state = ""

        
    
        launch_button = background[self.launch_button_loc[0]:self.launch_button_loc[1], 
                                self.launch_button_loc[2]:self.launch_button_loc[3]].astype(np.uint8)
        
        supply_drop = background[self.supply_drop_text_loc[0]:self.supply_drop_text_loc[1],
                                self.supply_drop_text_loc[2]:self.supply_drop_text_loc[3]]

        text1 = "".join(pytesseract.image_to_string(launch_button, config = self.custom_config).split())
        text2 = "".join(pytesseract.image_to_string(supply_drop, config = self.custom_config).split())

        print(text1, " - ", text2)
        if "LAUNCH" in text1:
            state = "dino"
        elif "EVENT" in text2 or \
            "PECIALEVENT" in text2 or \
            text2 == "SPECIALEVENT" or \
            "DROP" in text2 or \
            text2 == "SUDDLYDROD" or \
            'SUPPLY' in text2 or \
            'DROD' in text2 or \
            text2 == "SUPPLYDROP":
            state = "supply"
        elif "COIN" in text2 or "CHASE" in text2 or "NEW" in text2 or \
            "YEAR" in text2 or "TINE" in text2 or "DAY" in text2 or "GOLD" in text2:
            state = "coin"
        # elif text2 
        return state

    # ----------------------------------------------------------
    #   CHANGE LOCATION
    # ----------------------------------------------------------

    def change_location(self, r=300):
        """Randomly change location"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        time.sleep(1)

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
        time.sleep(25)
        # time.sleep(7.5)

        # click launch button incase we move so far
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        if self.moved_too_far(background):
            print("--"*10)
            print("MOVED TO FAR")
            pos = ((self.launch_button_loc[1] + self.launch_button_loc[0])/2, 
                   (self.launch_button_loc[3] + self.launch_button_loc[2])/2)
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)

    def change_view(self):
        """"Rotates the screen after everthing is collected"""
        print("--"*10)
        print("CHANGING VIEW")
        
        pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
        time.sleep(1)

        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        pos = self.locate_x_button(background)
        if pos:
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)  

        pyautogui.moveTo(self.x+self.w//2, self.y+self.h//2, 0.1)
        pyautogui.scroll(90)
        time.sleep(1)

    def moved_too_far(self, background):
        """"Detects when we move to far."""
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        color = background[self.moved_too_far_loc[0], 
                           self.moved_too_far_loc[1], :]
        # print(color)
        if 120 > color[0] > 100 and \
           10 > color[1] > 0 and \
           10 > color[2] > 0:
           return True
        return False

        # img = self.moved_too_far_pic.resize((self.w, self.h), Image.ANTIALIAS)
        # moved_too_far_resized = np.array(img)[:, :, :3]
        # print("DIST", np.mean((moved_too_far_resized.astype(np.float) - background.astype(np.float))**2))
        # return not self.background_changed(moved_too_far_resized, background, 2000)

    # ----------------------------------------------------------
    #   DINO COLLECTION
    # ----------------------------------------------------------

    def is_dino_loading_screen(self, background):
        
        img = self.loading_screen_pic.resize((self.w, self.h), Image.ANTIALIAS)

        # some reason image become 4D 
        loading_screen_resized = np.array(img)[:, :, :3]
        return not self.background_changed(loading_screen_resized, background)


    def get_battery_left(self, background):
        """Returns how much battery left, betwen [0 (full), 1 (empty)]"""
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
        return line_length /  (self.battery_loc[2] - self.battery_loc[3])

    def shoot_dino(self):
        """Shoots the dino"""

        def dino_location(background, shift, D):
            """Find the critical point"""
            pos = []
            D_ = D


            mask = (background[:,:,0] >= 180) * \
                   (background[:,:,1] >= 180) * \
                   (background[:,:,2] >= 180)  

            mask = filters.median(mask, np.ones((3, 3)))
            mask = morphology.binary_opening(mask, np.ones((1, 5)))
            mask = morphology.binary_opening(mask, np.ones((5, 1)))

            dist = ndimage.distance_transform_edt(mask)
            if np.sum(mask) > 0:
                # labels = measure.label(mask)
                rows, cols = np.where(dist >= np.max(dist))
                pos = [shift + np.mean(rows), np.mean(cols)]
                D_ =  np.max(dist) if np.max(dist) - 5 > 0 else D
                # import matplotlib.pyplot as plt
                # plt.figure(1)
                # plt.imshow(mask)
                # plt.figure(2)
                # plt.imshow(dist)
                # plt.show()
            return pos, D_
        
        # hyper parameters
        D = 2*self.D
        v_max = self.v_max
        S = 4
        ms = 0.05
        h1, h2, h3 = 5, 2, 2, # 10, 2, 2
        
        # detect dart location 
        dart_loc = self.dart_loc 
        prev_dino_loc = None
        vel = [0, 0]
        buffer = 10
        

        cx = (self.launch_button_loc[2] + self.launch_button_loc[3]) / 2
        cy = (self.launch_button_loc[0] + self.launch_button_loc[1]) / 2
        pyautogui.moveTo(self.x+cx, self.y+cy, 1)  
        pyautogui.mouseDown()
        time.sleep(0.5)
        
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

        start = time.time()
        end = start

        while not self.is_dino_loading_screen(background) and end - start < 60:
            
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            # b_prev = background
            background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            background_cropped = background[self.dino_shoot_loc[0]:,:self.dino_shoot_loc[1],:]
            dino_loc, _ = dino_location(background_cropped, self.dino_shoot_loc[0], 2*self.D)
            
            end = time.time()

            if not dino_loc and prev_dino_loc:
                dino_loc = [prev_dino_loc[0] + vel[0],
                            prev_dino_loc[1] + vel[1]]
   
            if dino_loc:
                dino_2_dart = np.sqrt((dino_loc[0] - dart_loc[0])**2 + (dino_loc[1] - dart_loc[1])**2)
                battery_left = 1 - self.get_battery_left(background)

                # check if dino in dart range
                if np.sqrt((dino_loc[0] - dart_loc[0])**2 + (dino_loc[1] - dart_loc[1])**2) <= (D + h1*battery_left):
                    print("--"*10)
                    print("DINO CLOSE SHOOTING")
                    pyautogui.mouseUp()
                    time.sleep(0.25)
                    pyautogui.mouseDown()
                    time.sleep(0.5)
                else: # if not move screen to dino
                    v_max_new = v_max + h2*battery_left

                    # predict future location
                    dino_loc_pred = [dino_loc[0] + vel[0] * (dino_2_dart / v_max_new),  
                                    dino_loc[1] + vel[1] * (dino_2_dart / v_max_new)] 

                    # get direction and multiply with v_max
                    dino_pred_2_dart = np.sqrt((dino_loc_pred[0] - dart_loc[0])**2 + (dino_loc_pred[1] - dart_loc[1])**2)
                    x_v =  v_max_new * (dino_loc_pred[1] - dart_loc[1]) / dino_pred_2_dart
                    y_v =  v_max_new * (dino_loc_pred[0] - dart_loc[0]) / dino_pred_2_dart

                    # if we are to close move slower
                    slow_down_speed = min(1, (dino_2_dart/((S - h3*battery_left)*D)))
                    mouse_pos = pyautogui.position()

                    # don't go outside the screen
                    dx = min(max(mouse_pos[0] + x_v*slow_down_speed, self.x + buffer), self.x + self.w - 4*buffer)
                    dy = min(max(mouse_pos[1] + y_v*slow_down_speed, self.y + buffer), self.y + self.h - buffer)

                    pyautogui.moveTo(dx, dy, ms)
                
                if prev_dino_loc:
                    vel = [dino_loc[0] - prev_dino_loc[0], dino_loc[1] - prev_dino_loc[1]]
                prev_dino_loc = dino_loc

            else:
                # shoot to reset the dart circle
                pyautogui.mouseUp()
                time.sleep(0.5)
                pyautogui.moveTo(self.x+cx, self.y+cy, 0.1)  
                pyautogui.mouseDown() 
            # print("DIST", np.mean((b_prev.astype(np.float) - background.astype(np.float))**2))
        
        if end - start > 60:
            pyautogui.mouseUp()
            time.sleep(0.25)
            pyautogui.mouseDown()
            time.sleep(60)  

            pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
            time.sleep(1)           

        else:
            print("--"*10)
            print("DONE")
            while self.is_dino_loading_screen(background):
                background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                time.sleep(1)
            time.sleep(20) 
            # read how much and which dino we shoot it
            
            pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
            time.sleep(5) 

    def collect_dino(self):
        """"Finds and shoots the dino"""
        
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        dino_pos = self.detect_dino(background)
        
        print("--"*10)
        print("TOTAL NUMBER OF DINO", len(dino_pos))
        for i, pos in enumerate(dino_pos):
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.2)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # to many FPs so quick way to eliminate them
            if not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
                continue

            time.sleep(0.8)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)

            if state == "dino":
                cx = (self.launch_button_loc[2] + self.launch_button_loc[3]) / 2
                cy = (self.launch_button_loc[0] + self.launch_button_loc[1]) / 2
                pyautogui.click(x=self.x+cx, y=self.y+cy)  
                time.sleep(1)

                background_loading_screen = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                while self.is_dino_loading_screen(background_loading_screen):
                    background_loading_screen = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                    time.sleep(1)

                print("--"*10)
                print("TIME TO SHOOT")                
                
                time.sleep(2)
                self.shoot_dino()

                # there is some bug in JW which is expected when I shoot a dino it turn to original direction
                for _ in range(self.number_of_scrolls):
                    self.change_view()

            else:
                print("--"*10)
                print("NOT DINO")
                pos = self.locate_x_button(background_new)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)  

    # ----------------------------------------------------------
    #   COIN COLLECTION
    # ----------------------------------------------------------

    def collect_coin(self):
        """Collects coin chests"""
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        coin_pos = self.detect_coins(background)

        for pos in coin_pos:
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            if np.sqrt((pos[0] - self.center_loc[0])**2 + (pos[1] - self.center_loc[1])**2) < 30:
                continue

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.2)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # to many FPs so quick way to eliminate them
            if not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
                continue

            time.sleep(0.8)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)
            if state == "coin":
                print("--"*10)
                print("CLICKING COIN")
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
                time.sleep(2.5) 
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
                
                # sometimes clicks already opened coin chests
                background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                state = self.determine_state(background)
                if state == "coin":
                    pos = self.locate_x_button(background)
                    pos = pos if pos else self.map_button_loc
                    pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                    time.sleep(1)  
            else:
                print("--"*10)
                print("NOT COIN")
                pos = self.locate_x_button(background)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)     

    # ----------------------------------------------------------
    #   SUPPLY COLLECTION
    # ----------------------------------------------------------

    def collect_supply_drop(self):
        """"Collects supply drops"""

        # use old background to determine stop clicking
        background_old= np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))        
        supply_drop_pos = self.detect_supply_drop(background_old)
        
        # loop until you click supply drop
        for pos in supply_drop_pos:

            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.2)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # to many FPs so quick way to eliminate them
            if not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
                continue

            time.sleep(0.8)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            state = self.determine_state(background_new)
            if state == "supply":
                print("--"*10)
                print("CLICKING SUPPLY DROP")

                background_tmp = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                # activate the supply drop
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)  
                time.sleep(2) 
                background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                if not self.background_changed(background_new, background_tmp):
                    pos = self.locate_x_button(background_new)
                    if pos:
                        pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                        time.sleep(1) 

                count = 0
                # loop until max click is reached or we are in the old background
                while self.max_click >= count and \
                      self.background_changed(background_old, background_new):
                    print("--"*10)
                    print("CLICK")
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    # time.sleep(1.5) 
                    time.sleep(2.5) 
                    background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                    # print()
                    # collected = self.determine_supply_collected(background_new)
                    # if collected:
                    #     key, number = collected
                    #     tmp = self.supply_collected.get(key, 0)
                    #     self.supply_collected[key] = tmp + number
                    count += 1

                # if clicked more than max amount something is wrong
                if count > self.max_click:
                    pos = self.locate_x_button(background_new)
                    if pos:
                        pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                        time.sleep(1) 

            # elif not self.background_changed(background_old, background_new):
            #     print("--"*10)
            #     print("NOTHING THERE")
            else:
                print("--"*10)
                print("NOT SUPPLY DROP")
                # find x button if not there click on map button
                pos = self.locate_x_button(background_new)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)                                       

    # ----------------------------------------------------------
    #   HELPER
    # ----------------------------------------------------------

    def background_changed(self, b1, b2, threshold=2000):
        """Compare difference between two frames"""
        diff = (b1.astype(float) - b2.astype(float))**2
        print("DIFF", np.mean(diff))
        return np.mean(diff) > threshold