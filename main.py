import pyautogui
import matplotlib.pyplot as plt
import sys
import keyboard
import numpy as np
import time
import cv2
from skimage import draw
from scipy import ndimage

print('Press Ctrl-C to quit.')

times = 4
counter = 0

x, y, w, h = -1, -1, -1, -1
img = None
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
            img = np.array(pyautogui.screenshot(region=(x, y, w, h)))
            # img = img[270:, :, :]
            # mask = np.zeros((h, w))
            # mask[2]
            # mask[507, 221] = 0
            # dist = ndimage.distance_transform_edt(mask)
            # mask = dist > 287

            # # rr, cc = draw.disk((507, 221), 287, shape=None)
            # # f1 = np.logical_and(rr >= 0, rr < h)
            # # f2 = np.logical_and(cc >= 0, cc < w)
            # # f = np.logical_and(f1, f2)
            # # print(img.shape, mask.shape, w, h)
            # # print(rr.max(), rr.min(), cc.max(), cc.min())
            # # mask[rr[f], cc[f]] = 1
            # img[mask] = 0
            # imgs[counter % max_size] = img
            
            # compute delta
            # plt.clf()
            # plt.cla()
            # plt.imshow(img)
            # plt.show()

        # move the mouse
        if img is not None and times > 0:
            for yy in range(300, 720, 20):
                for xx in range(20, 460, 20):
                    if keyboard.is_pressed("q"):
                        raise KeyboardInterrupt
                    pyautogui.moveTo(x + xx, y + yy)
        
            times -= 1
        time.sleep(0.1)
except KeyboardInterrupt:
    print('\n')