from params import *
from funcs import *

import requests
import bs4
import datetime

import webbrowser

class Paper:
    def __init__(self, title: str = "No papers for this day", authors: list[str] = [], download_link: str = "", doi:str = "", journal:str = "", updated:str = "", summary:str = "No abstract available from this RSS feed", tags: list[str] = [], loaded: bool = True, loader: tuple = None, author_class = None, publish_date : datetime.date = None, website_url : str = None):
        self.title = title
        self.summary = summary
        self.authors = authors
        self.download_link = download_link
        self.doi = doi
        self.score = -1
        self.journal = journal
        self.tags = tags
        self.website_url = website_url if website_url != None else doi
        if self.website_url[:2] == "10":
            self.website_url = "https://www.doi.org/" + self.website_url
        elif self.website_url[:2] == "do":
            self.website_url = "https://www." + self.website_url

        # self.updated = updated #replace with real date format
        if (publish_date == None) and (updated != ""):
            self.publish_date = datetime.date(year=int(updated[0:4]), month=int(updated[5:7]), day=int(updated[8:10]))
        else:
            self.publish_date = publish_date
        
        # if self.publish_date > datetime.datetime.now():
            # self.publish_date = datetime.datetime.now()
        if self.publish_date != None and self.publish_date > datetime.date.today():
            self.publish_date = datetime.date.today()

        self.loaded = loaded
        self.loader = loader
        self.author_class = author_class

        self.update_score()

    # used for sorting entries by score
    def _is_valid_operand(self, other):
        return (hasattr(other, "score") and
                hasattr(other, "score"))

    # used for sorting entries by score
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.score) == (other.score)

    # used for sorting entries by score
    def __gt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.score) < (other.score)

    def load(self) -> bool:
        if self.loaded: 
            return False
        elif self.loader == None:
            return False
        
        url, div_id = self.loader

        r = requests.get(url=url, headers=HEADERS)
        soup = bs4.BeautifulSoup(r.content, 'html5lib')
        abs = str(soup.find('div', attrs = {'id':div_id}) )

        if ("<p>" in abs) and ("</p>" in abs):
            self.summary = scrub_html_tags(abs[abs.index("<p>")+3:abs.index("</p>")].replace("<sub>", "_").replace("</sub>","").replace("<i>","").replace("</i>",""))

        if self.author_class != None:
            authors_str = scrub_html_tags(str(soup.find('ul', attrs = {'class':self.author_class})).replace("</a>", ","))
            authors = authors_str.split(",")
            counter = 0
            while counter < len(authors):
                if ("ORCID" in authors[counter]) or ("&amp" in authors[counter]) or ("1" in authors[counter]) or (len(authors[counter]) < 5):
                    authors.pop(counter)
                else:
                    counter += 1
            self.authors = authors
            
        self.loaded = True

        self.update_score()

        return True

    def open(self) -> None:
        webbrowser.open(self.website_url, new = 2)

    def update_score(self) -> None:
        score = 0

        # JOURNAL SCORE BONUS

        if self.journal in JOURNALS:
            score += JOURNALS[self.journal]

        # CATEGORY SCORE BONUS

        maxbonus = 0
        for tag in self.tags:
            if tag.term in CATEGORIES:
                if maxbonus < CATEGORIES[tag.term]:
                    maxbonus = CATEGORIES[tag.term]
            if tag.term in CATEGORY_PENALTIES:
                score += CATEGORY_PENALTIES[tag.term]
        score += maxbonus

        # AUTHOR SCORE BONUS

        total_authors = " ".join(self.authors).lower()
        for keyauthor in KEYAUTHORS:
            if keyauthor in total_authors:
                score += KEYAUTHORS[keyauthor]
        

        # NUM AUTHORS BONUS
        num_authors = len(self.authors)
        score += NUM_AUTHOR_BIAS * min(1,(num_authors-1)/(AUTHOR_SCALE-1))

        # KEYWORD SCORE BONUS

        total_text = (self.title + " " + self.summary).replace("\n", " ").lower()
        for keyword in KEYWORDS:
            if keyword in total_text:
                score += KEYWORDS[keyword]
        
        self.score = score

class NaturePaper(Paper):

    def __init__(self, title = "No papers for this day", authors: str = [], download_link:str = "", doi: str = "", journal: str = "", updated: str = "", summary: str = "", tags: list[str] = [], publish_date: datetime.date = None, website_url = None, author_class = None):
        super().__init__(title, authors, download_link, doi, journal, updated, summary, tags, False, None, None, publish_date, website_url)

    def load(self) -> bool:
        if self.loaded:
            return False
        
        url = self.website_url
        div_id = "Abs1-content"

        r = requests.get(url=url, headers=HEADERS)
        soup = bs4.BeautifulSoup(r.content, 'html5lib')
        abs = str(soup.find('div', attrs = {'id':div_id}) )

        if ("<p>" in abs) and ("</p>" in abs):
            self.summary = scrub_html_tags(abs[abs.index("<p>")+3:abs.index("</p>")].replace("<sub>", "_").replace("</sub>","").replace("<i>","").replace("</i>",""))

        if self.author_class is not None:
            authors_str = scrub_html_tags(str(soup.find('ul', attrs = {'class':self.author_class})).replace("</a>", ","))
            authors = authors_str.split(",")
            counter = 0
            while counter < len(authors):
                if ("ORCID" in authors[counter]) or ("&amp" in authors[counter]) or ("1" in authors[counter]) or (len(authors[counter]) < 5):
                    authors.pop(counter)
                else:
                    counter += 1
            self.authors = authors
            
        self.loaded = True

        self.update_score()

        return True

class PhysicalReviewPaper(Paper):

    def __init__(self, title = "No papers for this day", authors = [], download_link = "", doi = "", journal = "", updated = "", summary = "", tags = [], loaded = False, publish_date = None, website_url = None):
        super().__init__(title, authors, download_link, doi, journal, updated, summary, tags, True, None, None, publish_date, website_url)

    def load(self):
        return True
    
class ArxivPaper(Paper):
    def __init__(self, title = "No papers for this day", authors = [], download_link = "", doi = "", journal = "", updated = "", summary = "", tags = [], loaded = True, loader = None, author_class=None, publish_date = None, website_url = None):
        super().__init__(title, authors, download_link, doi, journal, updated, summary, tags, loaded, loader, author_class, publish_date, website_url)
    def load(self):
        return True
    

class ACSPaper(Paper):

    def __init__(self, title: str, authors: str = [], download_link:str = "", doi: str = "", journal: str = "", tags: list[str] = [], publish_date: datetime.date = None, website_url = None):
        super().__init__(title, authors, None, doi, journal, None, "No abstract available from this RSS feed", tags, True, None, None, publish_date, website_url)

    def load(self) -> bool:
        return True

class PNASPaper(Paper):

    def __init__(self, title: str, authors: str = [], summary: str = "No abstract available from this RSS feed", download_link:str = "", doi: str = "", journal: str = "", tags: list[str] = [], publish_date: datetime.date = None, website_url = None):
        super().__init__(title, authors, None, doi, journal, None, summary, tags, True, None, None, publish_date, website_url)

    def load(self) -> bool:
        return True