from params import *
from funcs import *

from paper import Paper

class Scorer:
    def __init__(self):
        pass

    def __call__(self, paper: Paper):
        score = 0

        # JOURNAL SCORE BONUS

        if paper.journal in JOURNALS:
            score += JOURNALS[paper.journal]

        # CATEGORY SCORE BONUS

        maxbonus = 0
        for tag in paper.tags:
            if tag.term in CATEGORIES:
                if maxbonus < CATEGORIES[tag.term]:
                    maxbonus = CATEGORIES[tag.term]
            if tag.term in CATEGORY_PENALTIES:
                score += CATEGORY_PENALTIES[tag.term]
        score += maxbonus

        # AUTHOR SCORE BONUS

        total_authors = " ".join(paper.authors).lower()
        for keyauthor in KEYAUTHORS:
            if keyauthor in total_authors:
                score += KEYAUTHORS[keyauthor]
        

        # NUM AUTHORS BONUS
        num_authors = len(paper.authors)
        score += NUM_AUTHOR_BIAS * min(1,(num_authors-1)/(AUTHOR_SCALE-1))

        # KEYWORD SCORE BONUS

        total_text = (paper.title + " " + paper.summary).replace("\n", " ").lower()
        for keyword in KEYWORDS:
            if keyword in total_text:
                score += KEYWORDS[keyword]
        
        return score