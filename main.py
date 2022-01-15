import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time
import pytesseract
from skimage import measure, morphology, feature, color, filters

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

DEBUG = True
shooting_zone = (230, 720, 10, 440)
launch_button_loc = (650, 712, 132, 310)
supply_drop_text_loc = (92, 132, 110, 330)
map_button_loc = (786, 222)

special_event_color = (0, 180, 0, 50, 255, 30)
supply_drop_color = (200, 100, 0, 255, 160, 60)



def supply_drop_or_dino(background):

    custom_config = r'--oem 3 --psm 1'
 
    launch_button = background[launch_button_loc[0]:launch_button_loc[1], 
                               launch_button_loc[2]:launch_button_loc[3]].astype(np.uint8)
    
    supply_drop = background[supply_drop_text_loc[0]:supply_drop_text_loc[1],
                             supply_drop_text_loc[2]:supply_drop_text_loc[3]]

    text1 = "".join(pytesseract.image_to_string(launch_button).split())
    text2 = "".join(pytesseract.image_to_string(supply_drop, config = custom_config).split())

    if DEBUG:
        print(text1, " - ", text2)
        plt.figure(2, figsize=(4, 4))
        plt.imshow(launch_button)

        plt.figure(3, figsize=(4, 4))
        plt.imshow(supply_drop)

    # print(text1, " - ", text2)
    if text1 == "LAUNCH":
        return 1
    elif text2 == "SPECIALEVENT" or text2 == "SUPPLYDROP":
        return 2
    # elif text2 
    return 0

def locate_x_button(background):
    button = (background[712:,:,0] == 117) * \
            (background[712:,:,1] == 10) * \
            (background[712:,:,2] == 10)

    if np.sum(button) > 0:
        y, x = np.where(button)
        return 712 + int(np.mean(y)), int(np.mean(x))
    return None

def detect_supply_drop(background):
    """Finds supply drop by simply thresholding it but there might be false positives"""
    
    pos = []

    # threshold + clean up
    background_cropped = background[shooting_zone[0]:shooting_zone[1],
                                    shooting_zone[2]:shooting_zone[3]]
    print(background_cropped.shape)
    t1 = (background_cropped[:,:,0] >= supply_drop_color[0]) * \
        (background_cropped[:,:,1] >= supply_drop_color[1]) * \
        (background_cropped[:,:,2] >= supply_drop_color[2]) * \
        (background_cropped[:,:,0] <= supply_drop_color[3]) * \
        (background_cropped[:,:,1] <= supply_drop_color[4]) * \
        (background_cropped[:,:,2] <= supply_drop_color[5])
    t2 = (background_cropped[:,:,0] >= special_event_color[0]) * \
        (background_cropped[:,:,1] >= special_event_color[1]) * \
        (background_cropped[:,:,2] >= special_event_color[2]) * \
        (background_cropped[:,:,0] <= special_event_color[3]) * \
        (background_cropped[:,:,1] <= special_event_color[4]) * \
        (background_cropped[:,:,2] <= special_event_color[5])
    mask = np.logical_or(t1, t2).astype(np.uint8)
    mask = morphology.binary_closing(mask, np.ones((5,5)))
    
    # connected components
    labels = measure.label(mask, background=0, connectivity=2)
    if DEBUG:
        print(labels.max(), labels.min())
        plt.figure(4, figsize=(4, 8))
        # plt.clf()
        # plt.cla()
        plt.imshow(labels)

    # find center of mass
    for label in range(1, labels.max()+1):
        rows, cols = np.where(labels == label)
        if len(rows) > 20:
            pos.append([shooting_zone[0] + int(np.mean(rows)), shooting_zone[2] + int(np.mean(cols))])

    return pos

def detect_dino(tmp, background):
    """Finds the location of dino but there are false positives need more cleaning"""
    
    # edges = feature.canny(color.rgb2gray(background))
    edges = filters.sobel(color.rgb2gray(background))

    gray1 = color.rgb2gray(background).astype(float)
    gray2 = color.rgb2gray(tmp).astype(float)

    diff = np.abs(gray1 - gray2)
    diff[diff < 0.1] = 0

    # mask = morphology.binary_opening(edges, np.ones((3,3)))
    # mask = morphology.binary_closing(mask, np.ones((5,5)))
    if DEBUG:
        plt.figure(5, figsize=(4, 8))
        # plt.clf()
        # plt.cla()
        plt.imshow(diff)    

def determine_state():
    """After you click determine is this supply drop/dino/coin chase etc."""
    pass

def shoot_dino():
    pass


print('Press Ctrl-C to quit.')

# fig1 = plt.figure(figsize=(4, 8))
# fig2 = plt.figure()

x, y, w, h = -1, -1, -1, -1

tmp = None
try:
    while True:
        # set location of the app
        if keyboard.is_pressed('a'):
            print("KEY PRESSED") 
            if x == -1 or y == -1:
                x, y = pyautogui.position()
            elif w == -1 or h == -1:
                x_, y_ = pyautogui.position()
                w = abs(x - x_)
                h = abs(y - y_)

        # take photo
        if x != -1 and y != -1 and w != -1 and h != -1:
            # debug
            if DEBUG:
                background = np.array(pyautogui.screenshot(region=(x, y, w, h)))

                state = supply_drop_or_dino(background)
                if state == 1:
                    pass

                supply_drop_pos = detect_supply_drop(background)
                if tmp is not None:
                    dino_pos = detect_dino(tmp, background)

                plt.figure(1, figsize=(4, 8))
                plt.clf()
                plt.cla()
                plt.imshow(background, vmax=255, vmin=0)
                rect = patches.Rectangle((shooting_zone[2], shooting_zone[0]),
                                         shooting_zone[3] - shooting_zone[2],
                                         shooting_zone[1] - shooting_zone[0],
                                         linewidth=1,edgecolor='r',facecolor='none')
                plt.gca().add_patch(rect)
                rect = patches.Rectangle((supply_drop_text_loc[2], supply_drop_text_loc[0]),
                                         supply_drop_text_loc[3] - supply_drop_text_loc[2],
                                         supply_drop_text_loc[1] - supply_drop_text_loc[0],
                                         linewidth=1,edgecolor='g',facecolor='none')
                plt.gca().add_patch(rect)
                rect = patches.Rectangle((launch_button_loc[2], launch_button_loc[0]),
                                         launch_button_loc[3] - launch_button_loc[2],
                                         launch_button_loc[1] - launch_button_loc[0],
                                         linewidth=1,edgecolor='b',facecolor='none')
                plt.gca().add_patch(rect)
                pos = locate_x_button(background)
                if pos:
                    plt.plot(pos[1], pos[0], ".", color="k", markersize=15)
                if supply_drop_pos:
                    for p in supply_drop_pos:
                        plt.plot(p[1], p[0], "*", color="k", markersize=15)

                plt.plot(map_button_loc[1], map_button_loc[0], "x", color="k", markersize=15)


                plt.tight_layout()
                plt.pause(0.1)
                plt.draw()

            # move the mouse
            else:
                for yy in range(shooting_zone[0], shooting_zone[1], 20):
                    for xx in range(shooting_zone[2], shooting_zone[3], 20):
                        if keyboard.is_pressed("q"):
                            raise KeyboardInterrupt

                        background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                        
                        # determine state
                        state = supply_drop_or_dino(background)
                        button = locate_x_button(background)

                        if state == 1:
                            print(button)
                            if button is None:
                                raise KeyboardInterrupt
                            pyautogui.click(x=x+button[1], y=y+button[0])
                            time.sleep(1)
                        elif state == 2:
                            print(button)
                            if button is None:
                                raise KeyboardInterrupt

                            # click 4 times
                            pyautogui.click()  
                            time.sleep(2) 
                            pyautogui.click()  
                            pyautogui.click()  
                            pyautogui.click()  
                            pyautogui.click()  

                            # pyautogui.click(x=x+button[1], y=y+button[0])   
                            time.sleep(1)   
                        elif button:
                            pyautogui.click(x=x+button[1], y=y+button[0])   
                            time.sleep(1)  
                        else:
                            pyautogui.click(x=x+map_button_loc[1], y=y+map_button_loc[0])

                        # press x

                        pyautogui.moveTo(x + xx, y + yy)
                        pyautogui.click() 
                        time.sleep(1)
                        
                pyautogui.moveTo(x + w//2, y + h//2)
                pyautogui.scroll(180)

            tmp = background.copy()

        time.sleep(0.1)
except KeyboardInterrupt:
    print('\n')
