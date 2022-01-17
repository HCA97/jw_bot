import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

from jw_bot import Bot


def plot_pos(pos, marker=".", color="k"):
    if pos:
        for p in pos:
            plt.plot(p[1], p[0], marker, color=color, markersize=15)

def show_regions(shooting_zone, supply_drop_text_loc, launch_button_loc):
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

if __name__ == "__main__":
    print('Press Ctrl-C to quit.')
    DEBUG = False

    # for changing location
    something_there = False
    number_of_scrolls = 0
    x, y, w, h = -1, -1, -1, -1
    bot = Bot()
    pos = []
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
                background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                pos = bot.detect_supply_drop(background)
                # pos = bot.detect_coins(background)
                bot.collect_supply_drop()



                plt.figure(3)
                plt.imshow(background)
                plot_pos(pos)
                show_regions(bot.shooting_zone, bot.supply_drop_text_loc, bot.launch_button_loc)
                plt.show()


            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n')
