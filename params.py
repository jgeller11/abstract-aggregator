import os

# TODO: package this up in some nicer way perhaps?

# PARAMETERS

# number of recent papers to request in arxiv feed (can filter out how many are displayed in other ways)
NUM_PAPERS = 200

# dict of categories to read, paired with a corresponding score
CATEGORIES = {"cond-mat.stat-mech": 0, "cond-mat.mtrl-sci": 1}
# if a paper is listed in these categories, penalize (or boost) it
CATEGORY_PENALTIES = {"hep-th" : -4}

# dict of keywords with a bonus to score
KEYWORDS = {"unicorn": 1, "hamburger": 2}

# give key authors a bonus to score
KEYAUTHORS = {"example_author": 1}

JOURNALS = {"arxiv": 0}

# gives up to bias points to papers with more authors, up to scale authors
AUTHOR_BIAS_INFO = {"scale" : 10, "bias" : 2}

# default absolute path to directory where downloaded pdfs should be saved
DEFAULT_DOWNLOAD_DIR = os.path.join(os.getenv("HOME"), ".abstract-aggregator", "downloads")
# default absolute path to .bib file where citations should be written
DEFAULT_BIB_DIR = os.path.join(os.getenv("HOME"), ".abstract-aggregator", "bibliography.bib")


# for web scraping for abstracts
HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246", 'Accept-Encoding': 'gzip'}

# KEYBINDINGS (using tk keycodes)
DEFAULT_KEYBINDINGS = {
            "NEXT" : "<Right>",
            "PREV" : "<Left>",
            "YESTERDAY" : "<.>",
            "TOMORROW" : "<Return>",
            "DOWNLOAD" : "<Down>",
            "OPEN" : "<Up>",
            "QUIT" : "<q>",
            "SETTINGS" : "<Control-s>"
        }