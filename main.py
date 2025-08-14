# LIBRARIES
import os 

from loaders import get_all_papers

from threading import Thread

from gui_params import *
from params import *
from funcs import *

from reader import Reader
from scorer import Scorer
import tkinter as tk

import traceback

try: 
    if not os.path.exists(os.path.join(os.getenv("HOME"), ".abstract-aggregator")):
        os.makedirs(os.path.join(os.getenv("HOME"), ".abstract-aggregator"))

    window = tk.Tk()

    window_width = 800
    window_height = 600

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (window_width/2)
    y = (screen_height/2) - (window_height/2)

    window.title("Abstract Aggregator")
    window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))
    window.attributes("-topmost", 1)
    window.attributes("-topmost", 0)

    window.configure(bg=BG_COLOR)

    load_txt = tk.Label(window, text="Loading papers...", bg=BG_COLOR, fg=TXT_COLOR, font="helvetica 20 bold", justify="center", pady = 20)
    load_txt.pack()

    window.update()

    scorer = Scorer()

    papers = get_all_papers(scorer)
    
    Reader = Reader(window, papers, scorer)

    daemon = Thread(target=lambda : background_load(Reader), daemon=True, name='Loader')
    daemon.start()

    load_txt.pack_forget()


    Reader.start()

except: 
    with open(os.path.join(os.path.expanduser("~"), "Documents", "fun", "programming", "abstract-aggregator", "error.log"), "a") as f:
        f.write(traceback.format_exc())