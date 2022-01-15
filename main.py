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

# https://stackoverflow.com/questions/50655738/how-do-i-resolve-a-tesseractnotfounderror
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

DEBUG = False

# for changing location
something_there = False
number_of_scrolls = 0

# stores location of the app
x, y, w, h = -1, -1, -1, -1

# pos - x and y change due to image (row = y, col = x)
# (y_min, y_max, x_min, x_max)
# (y, x)
shooting_zone = (230, 720, 10, 440)
launch_button_loc = (650, 712, 132, 310)
supply_drop_text_loc = (92, 132, 110, 330)
map_button_loc = (786, 222)

# color
# (R_min, G_min, B_min, R_max, G_max, B_max)
# (R, G, B)
special_event_color = (0, 180, 0, 50, 255, 30)
supply_drop_color = (200, 100, 0, 255, 160, 60)
x_button_color = (117, 10, 10)
gmap_loc_color = (200, 0, 0, 255, 70, 60)

def locate_x_button(background, button_color=None, shift=712):
    """Locate x button to go back to map"""
    if button_color:
        button_color = x_button_color
        
    button = (background[shift:,:,0] == x_button_color[0]) * \
             (background[shift:,:,1] == x_button_color[1]) * \
             (background[shift:,:,2] == x_button_color[2])

    if np.sum(button) > 0:
        y, x = np.where(button)
        return shift + int(np.mean(y)), int(np.mean(x))
    return None

def detect_supply_drop(background):
    """Finds supply drop by simply thresholding, but there might be false positives"""
    
    pos = []

    # threshold + clean up
    background_cropped = background[shooting_zone[0]:shooting_zone[1],
                                    shooting_zone[2]:shooting_zone[3]]
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
        plt.imshow(labels)

    # find center of mass
    for label in range(1, labels.max()+1):
        rows, cols = np.where(labels == label)
        if len(rows) > 20:
            pos.append([shooting_zone[0] + int(np.mean(rows)), shooting_zone[2] + int(np.mean(cols))])

    return pos

def detect_coins(background):
    """Detects coin chests, but there might be false positives"""
    return []

def detect_dino(background):
    """Finds the location of dino but there are false positives need more cleaning"""
    
    # edges = feature.canny(color.rgb2gray(background))
    edges = filters.sobel(color.rgb2gray(background))



    # mask = morphology.binary_opening(edges, np.ones((3,3)))
    # mask = morphology.binary_closing(mask, np.ones((5,5)))
    if DEBUG:
        plt.figure(5, figsize=(4, 8))
        # plt.clf()
        # plt.cla()
        plt.imshow(edges) 

    return []   

def determine_state(background):
    """After you click determine is this supply drop/dino/coin chase etc."""
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
        return "dino"
    elif text2 == "SPECIALEVENT" or text2 == "SUPPLYDROP":
        return "supply"
    # elif text2 
    return ""

def change_location(r=300):
    """Randomly change location"""
    
    # press ctrl + shift + k to open the map
    pyautogui.click(x=x+w//2, y=y+h//2)
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
    mask = (background[:,:,0] >= gmap_loc_color[0]) * \
            (background[:,:,1] >= gmap_loc_color[1]) * \
            (background[:,:,2] >= gmap_loc_color[2]) * \
            (background[:,:,0] <= gmap_loc_color[3]) * \
            (background[:,:,1] <= gmap_loc_color[4]) * \
            (background[:,:,2] <= gmap_loc_color[5])
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
    pos = ((launch_button_loc[1] + launch_button_loc[0])/2, (launch_button_loc[3] + launch_button_loc[2])/2)
    pyautogui.click(x=x+pos[1], y=y+pos[0])
    time.sleep(1)

def shoot_dino():
    pass


print('Press Ctrl-C to quit.')

# fig1 = plt.figure(figsize=(4, 8))
# fig2 = plt.figure()



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

                # state = supply_drop_or_dino(background)
                # if state == 1:
                #     pass

                supply_drop_pos = detect_supply_drop(background)

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
                pos = locate_x_button(background, gmap_loc_color, 0)
                if pos:
                    plt.plot(pos[1], pos[0], ".", color="k", markersize=15)
                if supply_drop_pos:
                    for p in supply_drop_pos:
                        plt.plot(p[1], p[0], "*", color="k", markersize=15)

                plt.plot(map_button_loc[1], map_button_loc[0], "x", color="k", markersize=15)


                plt.tight_layout()
                plt.pause(5)
                plt.draw()

            # move the mouse
            else:
                if keyboard.is_pressed("q"):
                        raise KeyboardInterrupt

                # change_location()
                # raise Exception

                something_there = False

                if number_of_scrolls > 10:
                    # move location
                    print("--"*10)
                    print("CHANGING LOCATION")
                    change_location()
                    number_of_scrolls = 0
                
                else:
                    # get coins
                    background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                    coin_pos = detect_coins(background)
                    for pos in coin_pos:
                        # pos = coin_pos[0]
                        pyautogui.click(x=x+pos[1], y=y+pos[0])
                        time.sleep(1)

                        background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                        state = determine_state(background)
                        if state == "coin":
                            pyautogui.click()  
                            time.sleep(1) 
                            pyautogui.click()                            
                            something_there = True
                            break
                        else:
                            pos = locate_x_button(background)
                            pos = pos if pos else map_button_loc
                            pyautogui.click(x=x+pos[1], y=y+pos[0])
                            time.sleep(1)     

                    # get supply drops
                    background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                    supply_drop_pos = detect_supply_drop(background)
                    for pos in supply_drop_pos:
                        # pos = supply_drop_pos[0]
                        
                        pyautogui.click(x=x+pos[1], y=y+pos[0])
                        time.sleep(1)

                        background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                        state = determine_state(background)
                        if state == "supply":
                            print("--"*10)
                            print("CLICKING SUPPLY DROP")
                            pyautogui.click(x=x+w//2, y=y+h//2)  
                            time.sleep(2) 
                            print("FIRST CLICK")
                            pyautogui.click(x=x+w//2, y=y+h//2)
                            time.sleep(1) 
                            print("SECOND CLICK")  
                            pyautogui.click(x=x+w//2, y=y+h//2)  
                            time.sleep(1)   
                            print("THIRD CLICK")
                            pyautogui.click(x=x+w//2, y=y+h//2)  
                            time.sleep(1)   
                            print("FOURTH CLICK")
                            # print("--"*10)

                            pyautogui.click(x=x+w//2, y=y+h//2)  
                            time.sleep(1)   

                            something_there = True
                            break
                        else:
                            pos = locate_x_button(background)
                            pos = pos if pos else map_button_loc
                            pyautogui.click(x=x+pos[1], y=y+pos[0])
                            time.sleep(1)                                                  


                    # get dinos
                    background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                    dino_pos = detect_dino(background)
                    for pos in dino_pos:
                        # pos = dino_pos[0]
                        pyautogui.click(x=x+pos[1], y=y+pos[0])
                        time.sleep(1)
                        
                        background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                        state = determine_state(background)
                        if state == "dino":
                            cx = (launch_button_loc[2] + launch_button_loc[3]) / 2
                            cy = (launch_button_loc[0] + launch_button_loc[1]) / 2
                            pyautogui.click(x=x+cx, y=y+cy)  
                            time.sleep(3)
                            shoot_dino()
                            something_there = True
                            break
                        else:
                            pos = locate_x_button(background)
                            pos = pos if pos else map_button_loc
                            pyautogui.click(x=x+pos[1], y=y+pos[0])
                            time.sleep(1)   
                    if not something_there:
                        print("--"*10)
                        print("CHANGING VIEW")
                        # print("--"*10)
                        pyautogui.click(x=x+w//2, y=y+h//2)
                        time.sleep(1)

                        background = np.array(pyautogui.screenshot(region=(x, y, w, h)))
                        pos = locate_x_button(background)
                        if pos:
                            pyautogui.click(x=x+pos[1], y=y+pos[0])
                            time.sleep(1)  
                        
                        pyautogui.scroll(90)
                        time.sleep(1)
                        number_of_scrolls += 1
                

        time.sleep(0.1)
except KeyboardInterrupt:
    print('\n')
