# Jurassic World Alive Bot

It detects and collects supply drops, coin chests and dinos.

## Setup 

1. Install the latest version of the [BlueStacks](https://www.bluestacks.com/download.html)
    1. Set `Set location` short cut to `Ctrl+Shift+K`
    2. Set  `Back` short cut to `Ctrl+Shift+2`
    3. Install `Jurassic World Alive` 
2. Install [Python](https://www.python.org/downloads/) and add Python to PATH variables (when you install it will ask for it). If forget to do it, you can do it manually [link](https://www.educative.io/edpresso/how-to-add-python-to-path-variable-in-windows).
3. Install the required packages open commend line and type:
    ```bash
    pip install -r requirements.txt
    ```
    **Note** If you have problem installing any package visit [https://www.lfd.uci.edu/~gohlke/pythonlibs/](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
4. Install tesseract binaries for Python package [see](https://stackoverflow.com/questions/50655738/how-do-i-resolve-a-tesseractnotfounderror) and specified the  tesseract binary in `jw_bot.py` this line:
    ```python
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    ```
5. Almost there type ```python main.py```. Move the app in the middle of the screen because when we open the map screen expands. Then you need to specify the position of the app. Move your mouse to top left corner and press `key a` until you see `KEY PRESSED` text then move the mouse to bottom right corner and press `key a` again. And Done.

## TODO
- [ ] Test on other PCs more, different app size work on my computer
- [ ] Remove FP in dino (optional) plus no idea how to do it
- [ ] better moved far away checker use some sort of template
- [ ] logging to track what we collected
- [ ] do easy incubators (optional)
- [ ] shoot dino make it more adaptive (move faster or slower, shoot sooner etc. for different rarities)
- [ ] explain how to use it more detailed way
- [ ] get rid of the ocr (optional)