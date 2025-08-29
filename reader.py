import tkinter as tk
import tkinter.font as font
from tkinter import ttk
import os
import datetime
import requests
import pathlib
import json

# local classes
from bib_from_doi import get_bib_from_doi
from gui_params import *
from params import *
from funcs import *
from paper import Paper 
from scorer import Scorer

class Reader:
    # unused
    def on_window_resize(self, event: tk.Event) -> None:
        if (datetime.datetime.now() - self.last_time).total_seconds() < 1:
            return
        self.last_time = datetime.datetime.now()
        self.update_window()
    
    # quits gui
    def exit(self, event: tk.Event = None) -> None:
        self.root.destroy()

    # buffers thus far unseen papers into self.feed to display
    # returns 1 if at least one paper is found, 0 otherwise
    def load_unseen(self) -> int:
        return_value = 1
        unseen_feed = []
        with open(self.seen_dois_filepath, 'a') as f:
            for paper in self.full_feed:
                if not (paper.doi in self.seen_dois):
                    unseen_feed.append(paper)
                    f.write(paper.doi + "\n")
                    
        
        if len(unseen_feed) == 0:
            unseen_feed.append(Paper())
            return_value = 0
        
        unseen_feed.sort()

        self.feed: list[Paper] = unseen_feed        
        self.total_papers = len(self.feed)
        self.current_paper = 0

        self.get_current_paper().load()
        return return_value

    # buffers paper from selected day to self.feed
    # returns 1 if at least one paper is found, 0 otherwise
    def load_today(self) -> int:
        return_value = 1

        today_feed = []
        for paper in self.full_feed:
            if self.is_today(paper):
                today_feed.append(paper)
        
        if len(today_feed) == 0:
            today_feed.append(Paper())
            return_value = 0

        today_feed.sort()

        self.feed = today_feed        
        self.total_papers = len(self.feed)
        self.current_paper = 0

        self.get_current_paper().load()

        return return_value

    # displays current paper and begins interactive features in gui
    def start(self) -> None:
        self.display_paper()

        self.root.mainloop()

    # records current window width and height, resizes various elements accordingly
    def update_window(self) -> None:
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()
        margin = 50
        self.title_txt.config(wraplength=max(self.width-margin, 100))
        self.author_txt.config(wraplength=max(self.width-margin, 100))
        self.abstract_txt.config(wraplength=max(self.width-margin, 100))
        self.status_bar_txt.config(wraplength=max(self.width-margin, 100))
        self.root.update()

    # moves to the previous paper in current feed
    def prev(self, event : tk.Event = None) -> None:
        if self.current_paper != 0:
            self.current_paper -= 1
        self.display_paper()
        
    # moves to the next paper in current feed
    def next(self, event : tk.Event = None) -> None:
        if self.current_paper != self.total_papers-1:
            self.current_paper += 1
        self.display_paper()

    # updates day to day before
    def yesterday(self, event = None) -> None:
        self.date -= datetime.timedelta(days=1)
        self.date_str = str(self.date.month).rjust(2,"0") + "/" + str(self.date.day).rjust(2,"0") + "/" + str(self.date.year)[2:]
        self.load_today()
        self.display_paper()
    
    # updates day to next day, or to New Papers feed if current day is today
    def tomorrow(self, event = None) -> None:
        self.date += datetime.timedelta(days=1)
        if self.date > datetime.date.today():
            self.load_unseen()
            self.date_str = "New Papers"
            self.date = datetime.date.today() + datetime.timedelta(days=1)
        else:
            self.date_str = str(self.date.month).rjust(2,"0") + "/" + str(self.date.day).rjust(2,"0") + "/" + str(self.date.year)[2:]
            self.load_today()
        self.display_paper()
        
    # returns Paper object for currently displayed paper
    def get_current_paper(self) -> Paper:
        return self.feed[self.current_paper]
    
    # finds next paper which is not loaded in feed, attempts to load it
    # returns True if an as of yet unloaded paper was successfully loaded
    def load_next_unloaded_paper(self) -> bool:
        counter = self.current_paper + 1
        while counter < self.total_papers:
            if not self.feed[counter].load():
                counter += 1
            else:
                if self.current_paper < self.total_papers - 2:
                    self.feed[self.current_paper+1:] = sorted(self.feed[self.current_paper+1:])
                return True
        counter = 0
        while counter < self.current_paper:
            if not self.feed[counter].load():
                counter += 1
            else:
                return True
        return False

    # returns if a paper is from the current day for the reader
    def is_today(self, paper : Paper = None) -> bool:
        if paper == None:
            paper = self.get_current_paper()

        return (paper.publish_date.day == self.date.day) and (paper.publish_date.month == self.date.month) and (paper.publish_date.year == self.date.year)

    # update GUI elements with details of current Paper object
    def display_paper(self):
        
        paper = self.get_current_paper()

        title_str = paper.title.replace("\n"," ").replace("  "," ").replace("  "," ").replace("\\textrm", "").replace("\\textsc", "").replace("\\text", "").replace("\\mathrm", "").replace("$", "") # TODO: clean this up a lot, implement function to fix up paper titles/abstracts
        self.title_txt.config(text = title_str)

        author_str = ", ".join(paper.authors)
        self.author_txt.config(text = author_str)

        abstract_str = paper.summary.replace("\n", " ")
        self.abstract_txt.config(text = abstract_str)

        self.update_window()
        self.status_bar()
        
    # update status bar
    # color currently unused
    def status_bar(self, color : int = 0):

        # # format:
        # #  journal  score  papernum    date
        # #  |arxiv|████------|3/46|04/28/25|

        current_paper = self.get_current_paper()
        
        date_str = self.date_str
        beginning_str = " " + "|" + current_paper.journal + "|" 
        end_str = "|" + str(self.current_paper+1) + "/" + str(self.total_papers) + "|" + date_str + "|"
        
        status_bar_width = int((self.width - 50) / (font.Font(family="courier").measure("AB") - font.Font(family="courier").measure("B") + 1)) # estimate number of characters

        len_score = status_bar_width - len(end_str)
        score_frac = max(0,min(1,current_paper.score / 11)) # 11 is some arbitrary great score
        score_val = round(score_frac * len_score)
        mid_str = ("█" * (score_val - len(beginning_str)) + "-" * (len_score - score_val)) if score_val > len(beginning_str) else ("-" * (len_score - len(beginning_str)))

        output = beginning_str + mid_str + end_str
        self.status_bar_txt.config(text = output)

    # return filepath where an entry will be written as pdf
    def download_path(self, in_dir : bool = False) -> str:
        entry = self.get_current_paper()
        download_path = fix_whitespace(entry.title.replace("\n"," ")).translate(str.maketrans("", "", "*^{}$")).replace(" ","_").replace(":","-").replace("/","-").replace("\\","-")
        if not in_dir:
            download_path = self.download_directory + "/" + download_path

        # ensure not overwriting
        i = 0
        output_path = download_path
        while os.path.isfile(output_path+".pdf"):
            i += 1
            output_path = download_path + "_" + str(i)

        return output_path+".pdf"

    # writes a citation to target .bib file
    # works kind of at bare minimum, idea is to fix everything else with doi lookup in jabref or similar
    def citation(self, downloaded : bool = True) -> str:
        paper = self.get_current_paper()

        key = paper.authors[0].split(" ")[-1] + str(paper.publish_date.year) if len(paper.authors) > 0 else paper.doi
        doi = paper.doi

        file_path =  (self.download_path(in_dir = True).replace("/",":")+":PDF")

        found, citation = get_bib_from_doi(doi)
        if found:
            spliceind = citation.index(",")
            return citation[:spliceind] + ",\n\tpriority\t= {prio3},\n\tfile\t= {:"+file_path+"}" + citation[spliceind:] + "\n\n"
        if downloaded:
            file_path =  (self.download_path(in_dir = True).replace("/",":")+":PDF")
            citation = "@Article{"+key+",\n\tpriority\t= {prio3},\n\tdoi\t= {"+doi+"},\n\tfile\t= {:"+file_path+"},\n}\n\n"
        else:
            citation = "@Article{"+key+",\n\tpriority\t= {prio3},\n\tdoi\t= {"+doi+"},\n}\n\n"
        return citation

    # attempt to download current paper and write citation
    # returns true if a file is downloaded
    def download(self, event = None) -> bool:

        # color currently unused, but eventually should give some visual indication of download in progress
        self.status_bar(color=5)

        entry = self.get_current_paper()

        url = entry.download_link

        downloaded = False

        if url != "":
            download_filename = self.download_path()
            bib_filename = self.bib_directory

            query_parameters = {"downloadformat": "pdf"}

            if url is not None:
                response = requests.get(url, params=query_parameters, headers=HEADERS)
            
                if len(response.content) > 10000:
                    with open(download_filename, mode="wb") as file:
                        file.write(response.content)
                    downloaded = True
           
        with open(bib_filename, mode="a") as file:
            file.write(self.citation(downloaded))

        self.status_bar(color=25)

        return downloaded

    # opens webpage associated with current paper
    def open_webpage(self, event : tk.Event = None) -> None:
        self.get_current_paper().open()

    # opens settings window if one does not exist
    # returns true if new window successfully opened
    def open_settings(self, event : tk.Event = None) -> bool:
        if self.settings_window is not None:
            return False
        
        self.settings_window = tk.Tk()
        def close_window(): 
            self.settings_window.destroy()
            self.settings_window = None
        self.settings_window.protocol("WM_DELETE_WINDOW", close_window)
        
        window_width = 500
        window_height = 600

        screen_width = self.settings_window.winfo_screenwidth()
        screen_height = self.settings_window.winfo_screenheight()
        x = (screen_width/2) - (window_width/2)
        y = (screen_height/2) - (window_height/2)

        self.settings_window.title("Abstract Aggregator")
        self.settings_window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))
        self.settings_window.attributes("-topmost", 1)
        self.settings_window.attributes("-topmost", 0)

        self.settings_window.configure(bg=BG_COLOR)

        self.settings_window.mainloop()
        
        return True

    # initialize gui_reader object
    # feed: list of papers to be potentially displayed
    def __init__(self, root, feed: list[Paper], scorer: Scorer): 
        self.root = root
        self.full_feed = feed
        self.settings_window = None
        self.date = datetime.date.today() + datetime.timedelta(days=1)
        self.date_str = "New Papers"
        self.current_paper = 0
        self.scorer = scorer
        
        ###################
        # set up seendois #
        ###################

        self.seen_dois = set()

        self.seen_dois_filepath = os.path.join(os.path.expanduser('~'), ".abstract-aggregator", "seendois.txt")

        # read from seendois.txt file if it exists
        if os.path.exists(self.seen_dois_filepath):
            with open(self.seen_dois_filepath, 'r') as f:
                for l in f.readlines():
                    self.seen_dois.add(l.replace("\n",""))
        # otherwise, create seendois.txt
        else:
            with open(self.seen_dois_filepath, 'w') as fout:
                fout.writelines([""])

        # cull first 200 entries of seendois.txt if too long
        if len(self.seen_dois) > 10000:
            with open(self.seen_dois_filepath, 'r') as fin:
                data = fin.read().splitlines(True)
            with open(self.seen_dois_filepath, 'w') as fout:
                fout.writelines(data[200:])


        ######################
        # set up directories #
        ######################

        directories_filepath = "directories.json"
        dirs = {"bib": DEFAULT_BIB_DIR, "downloads" : DEFAULT_DOWNLOAD_DIR}
        update_to_or_from_saved_json(directories_filepath, dirs)
        
        self.bib_directory = dirs["bib"]
        self.download_directory = dirs["downloads"]

        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)

        #################
        # set up window #
        #################    

        # initially update window
        self.width = 0
        self.height = 0

        self.last_time = datetime.datetime.now()

        self.title_txt = tk.Label(self.root, text="Example title", bg=BG_COLOR, fg=TXT_COLOR, font="helvetica 20 bold", wraplength=300, justify="left", pady = 20)
        self.author_txt = tk.Label(self.root, text="Example Authors", bg=BG_COLOR, fg=TXT_COLOR, font="helvetica 16 italic", wraplength=300, justify="left", pady=10)
        self.abstract_txt = tk.Label(self.root, text="Example Abstract", bg=BG_COLOR, fg=TXT_COLOR, font="helvetica 16", wraplength=300, justify="left")
        self.status_bar_txt = tk.Label(self.root, text="Example Status Bar", bg=BG_COLOR, fg=TXT_COLOR, font="courier 14", wraplength=300, justify="left")
        self.title_txt.pack()
        self.author_txt.pack()
        self.abstract_txt.pack()
        self.status_bar_txt.pack(padx = 5, pady = 20, side = tk.BOTTOM)
        
        ######################
        # set up keybindings #
        ######################

        keybindings_filepath = "keybindings.json"
        self.keybindings = DEFAULT_KEYBINDINGS
        update_to_or_from_saved_json(keybindings_filepath, self.keybindings)

        self.root.bind_all(self.keybindings["NEXT"], self.next)
        self.root.bind_all(self.keybindings["PREV"], self.prev)
        self.root.bind_all(self.keybindings["YESTERDAY"], self.yesterday)
        self.root.bind_all(self.keybindings["TOMORROW"], self.tomorrow)
        self.root.bind_all(self.keybindings["DOWNLOAD"], self.download)
        self.root.bind_all(self.keybindings["OPEN"], self.open_webpage)
        self.root.bind_all(self.keybindings["QUIT"], self.exit)
        self.root.bind_all(self.keybindings["SETTINGS"], self.open_settings)

        self.load_unseen()
        self.update_window()
