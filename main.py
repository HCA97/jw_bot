import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

import numpy as np
import time

from jw_bot import Bot

if __name__ == "__main__":
    print('Press Ctrl-C to quit.')
    DEBUG = False

    # for changing location
    something_there = False
    number_of_scrolls = 0
    max_scrolls = 10

    x, y, w, h = -1, -1, -1, -1
    bot = Bot()
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
                    bot.set_app_loc(x, y, w, h)

            # take photo
            if bot.loc:
                
                if keyboard.is_pressed("q"):
                    raise KeyboardInterrupt

                something_there = False

                # get coins
                background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                coin_pos = bot.detect_coins(background)
                for pos in coin_pos:
                    pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                    time.sleep(1)

                    background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                    state = bot.determine_state(background)
                    if state == "coin":
                        print("--"*10)
                        print("CLICKING COIN")
                        pyautogui.click(x=bot.x+bot.w//2, y=bot.y+bot.h//2) 
                        time.sleep(2.5) 
                        pyautogui.click(x=bot.x+bot.w//2, y=bot.y+bot.h//2) 
                        
                        background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                        state = bot.determine_state(background)
                        if state == "coin":
                            pos = bot.locate_x_button(background)
                            pos = pos if pos else bot.map_button_loc
                            pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                            time.sleep(1)  
                        else:
                            something_there = True
                    else:
                        pos = bot.locate_x_button(background)
                        pos = pos if pos else bot.map_button_loc
                        pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                        time.sleep(1)     

                # get supply drops
                something_there = bot.collect_supply_drop() or something_there                                   


                # get dinos
                background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                dino_pos = bot.detect_dino(background)
                for pos in dino_pos:
                    # pos = dino_pos[0]
                    pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                    time.sleep(1)
                    
                    background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                    state = bot.determine_state(background)
                    if state == "dino":
                        cx = (bot.launch_button_loc[2] + bot.launch_button_loc[3]) / 2
                        cy = (bot.launch_button_loc[0] + bot.launch_button_loc[1]) / 2
                        pyautogui.click(x=bot.x+cx, y=bot.y+cy)  
                        time.sleep(3)
                        bot.shoot_dino()
                        something_there = True
                        break
                    else:
                        pos = bot.locate_x_button(background)
                        pos = pos if pos else bot.map_button_loc
                        pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                        time.sleep(1)  

                if number_of_scrolls > max_scrolls:
                    # move location
                    print("--"*10)
                    print("CHANGING LOCATION")
                    bot.change_location()
                    number_of_scrolls = 0
                    
                if not something_there:
                    print("--"*10)
                    print("CHANGING VIEW")
                    # print("--"*10)
                    pyautogui.click(x=bot.x+bot.w//2, y=bot.y+bot.h//2)
                    time.sleep(1)

                    background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                    pos = bot.locate_x_button(background)
                    if pos:
                        pyautogui.click(x=bot.x+pos[1], y=bot.y+pos[0])
                        time.sleep(1)  


                    pyautogui.moveTo(bot.x+bot.w//2, bot.y+bot.h//2, 0.1)
                    pyautogui.scroll(90)
                    time.sleep(1)
                    number_of_scrolls += 1
                

            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n')
