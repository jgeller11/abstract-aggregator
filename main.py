# LIBRARIES
import os 

from loaders import get_all_papers

from threading import Thread

from gui_params import *
from params import *
from funcs import *

from reader import Reader
import tkinter as tk

import traceback

try: 
    window = tk.Tk()

    window_width = 800
    window_height = 600

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (window_width/2)
    y = (screen_height/2) - (window_height/2)

    window.title("Abstract Aggregator")
    window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))
    window.geometry("800x500")
    window.attributes("-topmost", 1)
    window.attributes("-topmost", 0)

    window.configure(bg=BG_COLOR)

    load_txt = tk.Label(window, text="Loading papers...", bg=BG_COLOR, fg=TXT_COLOR, font="helvetica 20 bold", justify="center", pady = 20)
    load_txt.pack()

    window.update()

    papers = get_all_papers()

    # testing directories
    # dir_1 = picture_path = os.path.join(os.path.expanduser("~"), "Documents", "fun", "programming", "arxiv_reader", "downloads","")
    # dir_2 = picture_path = os.path.join(os.path.expanduser("~"), "Documents", "fun", "programming", "arxiv_reader", "downloads", "bibliography.bib")

    # operating directories
    
    Reader = Reader(window, papers, download_directory=DOWNLOAD_DIR, bib_directory=BIB_DIR, load_each_day = False, load_all = False, load_none = False, seen_dois_directory = SEEN_DOIS_FILEPATH)


    daemon = Thread(target=lambda : background_load(Reader), daemon=True, name='Loader')
    daemon.start()

    load_txt.pack_forget()


    Reader.start()

except: 
     with open("/Users/jonathangeller/Documents/fun/programming/arxiv_reader/error.log", "w") as f:
        f.write(traceback.format_exc())