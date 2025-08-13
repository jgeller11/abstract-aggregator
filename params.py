import os

# TODO: package this up in some nicer way perhaps?

# PARAMETERS

# number of recent papers to request in arxiv feed (can filter out how many are displayed in other ways)
NUM_PAPERS = 200

# dict of categories to read, paired with a corresponding score
CATEGORIES = {"cond-mat.stat-mech": 0, "cond-mat.other": 0, "cond-mat.str-el": 1, "cond-mat.mtrl-sci": 2, "cond-mat.supr-con": 1}
# if a paper is listed in these categories, penalize (or boost) it
CATEGORY_PENALTIES = {"hep-th" : -4, "cond-mat.soft" : -2, "physics.ins-det" : 1, "physics.optics" : 2}

# dict of keywords with a bonus to score
KEYWORDS = {"floquet": 4, "light-induced": 3, "topolog": 1, "laser" : 1, "band": 1, "ultrafast": 2, "time-resolved": 2, "dressed": 1, "arpes": 2, "momentum microsc": 4, "phase transition": 2, "density wave": 2, "density-wave": 2}
# other potential keywords; time-resolved

# give key authors a bonus to score
KEYAUTHORS = {"gedik": 20, "cavalleri": 10}

JOURNALS = {"arxiv": 0, "prb": 1, "prl": 1, "npjqm": 4, "nphys": 4, "nmat": 4, "nphoton": 4, "nnano": 2, "ncomms": 1}

# path to directory where downloaded pdfs should be saved
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Documents", "mit", "gedik_group", "reading", "")
# path to .bib file where citations should be written
BIB_DIR = os.path.join(os.path.expanduser("~"), "Documents", "mit", "gedik_group", "reading", "bibliography.bib")
# path to seendois.txt file which holds info about papers already read
SEEN_DOIS_FILEPATH = os.path.join(os.path.expanduser("~"), "Documents", "fun", "programming", "abstract-aggregator", "seendois.txt")

# minimum score to display a paper, currently not used
MIN_SCORE = 0

# continuous scale promoting papers with more authors (to bias in favor of experimental papers)
# this sets how the rewards scales. 
AUTHOR_SCALE = 10
# and this sets weight of reward (set to 0 to disable this)
NUM_AUTHOR_BIAS = 2

# for web scraping for abstracts
HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246", 'Accept-Encoding': 'gzip'}