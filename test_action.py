"""THIS IS TESTING SCRIPTING"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import pyautogui
import keyboard

import numpy as np
import time

from jw_bot import Bot


def plot_pos(pos, marker=".", color="k"):
    if pos:
        # if len(pos) == 2:
        #     plt.plot(pos[1], pos[0], marker, color=color, markersize=15)

        # else:
        for p in pos:
            plt.plot(p[1], p[0], marker, color=color, markersize=15)

def show_regions(shooting_zone, supply_drop_text_loc, launch_button_loc, battery_loc, 
                supply_drop_resources_amount_loc, supply_drop_resources_text_loc,
                dino_collected_amount_loc, dino_collected_text_loc):
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
    rect = patches.Rectangle((battery_loc[2], battery_loc[0]),
                                battery_loc[3] - battery_loc[2],
                                battery_loc[1] - battery_loc[0],
                                linewidth=1,edgecolor='k',facecolor='none')
    plt.gca().add_patch(rect)
    # rect = patches.Rectangle((supply_drop_resources_amount_loc[2], supply_drop_resources_amount_loc[0]),
    #                             supply_drop_resources_amount_loc[3] - supply_drop_resources_amount_loc[2],
    #                             supply_drop_resources_amount_loc[1] - supply_drop_resources_amount_loc[0],
    #                             linewidth=1,edgecolor='y',facecolor='none')
    # plt.gca().add_patch(rect)
    # rect = patches.Rectangle((supply_drop_resources_text_loc[2], supply_drop_resources_text_loc[0]),
    #                             supply_drop_resources_text_loc[3] - supply_drop_resources_text_loc[2],
    #                             supply_drop_resources_text_loc[1] - supply_drop_resources_text_loc[0],
    #                             linewidth=1,edgecolor='y',facecolor='none')
    # plt.gca().add_patch(rect)
    # rect = patches.Rectangle((dino_collected_amount_loc[2], dino_collected_amount_loc[0]),
    #                             dino_collected_amount_loc[3] - dino_collected_amount_loc[2],
    #                             dino_collected_amount_loc[1] - dino_collected_amount_loc[0],
    #                             linewidth=1,edgecolor='c',facecolor='none')
    # plt.gca().add_patch(rect)
    # rect = patches.Rectangle((dino_collected_text_loc[2], dino_collected_text_loc[0]),
    #                         dino_collected_text_loc[3] - dino_collected_text_loc[2],
    #                         dino_collected_text_loc[1] - dino_collected_text_loc[0],
    #                         linewidth=1,edgecolor='c',facecolor='none')
    # plt.gca().add_patch(rect)


def show_points(moved_too_far_loc, dart_loc):
    plt.plot(moved_too_far_loc[1], moved_too_far_loc[0], "*", color="r", markersize=15)
    plt.plot(dart_loc[1], dart_loc[0], "*", color="r", markersize=15)


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

                print(w, h)

                background = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                # print(bot.determine_state(background))
                # print(bot.moved_too_far(background))
                if keyboard.is_pressed("0"):
                    bot.shoot_dino()
                if keyboard.is_pressed("9"):
                    bot.collect_supply_drop()

                print(bot.determine_supply_collected(background))
                print(bot.determine_dino_collected(background))
                    
                pos2 = bot.detect_supply_drop(background)
                pos = bot.detect_coins(background)
                pos1 = []
                # pos1 = bot.detect_dino(background)
                



                plt.figure(3)
                plt.clf()
                plt.cla()
                plt.imshow(background)
                plot_pos(pos + pos2 + pos1)
                show_regions(bot.shooting_zone, bot.supply_drop_text_loc, 
                            bot.launch_button_loc, bot.battery_loc, 
                            bot.supply_drop_resources_amount_loc, bot.supply_drop_resources_text_loc,
                            bot.dino_collected_amount_loc, bot.dino_collected_text_loc)
                show_points(bot.moved_too_far_loc, bot.dart_loc, )
                # plt.pause(0.01)
                # plt.draw()
                plt.show()



            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n')
