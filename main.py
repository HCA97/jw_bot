import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

DEBUG = True
shooting_zone = (230, 720, 10, 440)
launch_button_loc = (650, 712, 132, 310)
supply_drop_text_loc = (92, 132, 110, 330)
map_button_loc = (786, 222)


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

def shoot_dino():
    pass

def draw_rectangles():
    pass


print('Press Ctrl-C to quit.')

# fig1 = plt.figure(figsize=(4, 8))
# fig2 = plt.figure()

x, y, w, h = -1, -1, -1, -1

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
                plt.plot(map_button_loc[1], map_button_loc[0], "x", color="k", markersize=15)

        
                plt.tight_layout()
                plt.pause(1)
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

        time.sleep(0.1)
except KeyboardInterrupt:
    print('\n')
