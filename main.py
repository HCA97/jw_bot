import pyautogui
import keyboard
import time

from jw_bot import Bot

if __name__ == "__main__":
    print("Press 'q' to quit.")
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

                # get coins
                bot.collect_coin()

                # get supply drops
                bot.collect_supply_drop()                                 


                # get dinos
                bot.collect_dino()

                if bot.number_of_scrolls > max_scrolls:
                    # move location
                    print("--"*10)
                    print("CHANGING LOCATION")
                    bot.change_location()
                    bot.number_of_scrolls = 0
                    
                # if not something_there:
                bot.change_view()
                bot.number_of_scrolls += 1
                

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("--"*10)
        print("COLLECTED RESOURCES")
        for key, value in bot.supply_collected.items():
            print(key, " -- ", value)
        for key, value in bot.dino_collected.items():
            print(key, " -- ", value)        
        print('\n')
