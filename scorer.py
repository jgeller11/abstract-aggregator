from params import *
from funcs import *

from paper import Paper
import json

class Scorer:
    def __init__(self):
        journal_scores_filepath = os.path.join("scorer", "journal_scores.json")
        self.journal_scores = JOURNALS
        update_to_or_from_saved_json(journal_scores_filepath, self.journal_scores)

        keyword_scores_filepath = os.path.join("scorer", "keyword_scores.json")
        self.keyword_scores = KEYWORDS
        update_to_or_from_saved_json(keyword_scores_filepath, self.keyword_scores)

        author_scores_filepath = os.path.join("scorer", "author_scores.json")
        self.author_scores = KEYAUTHORS
        update_to_or_from_saved_json(author_scores_filepath, self.author_scores)

        tag_scores_filepath = os.path.join("scorer", "tag_scores.json")
        self.tag_scores = CATEGORY_PENALTIES
        update_to_or_from_saved_json(tag_scores_filepath, self.tag_scores)

        category_scores_filepath = os.path.join("scorer", "category_scores.json")
        self.category_scores = CATEGORIES
        update_to_or_from_saved_json(category_scores_filepath, self.category_scores)
        
        author_bias_filepath = os.path.join("scorer", "author_bias.json")
        author_bias_dict = AUTHOR_BIAS_INFO
        update_to_or_from_saved_json(author_bias_filepath, author_bias_dict)
        self.author_num_bias = author_bias_dict["bias"]
        self.author_scale = author_bias_dict["scale"]
        
        

    def __call__(self, paper: Paper):
        score = 0

        # JOURNAL SCORE BONUS

        if paper.journal in self.journal_scores:
            score += self.journal_scores[paper.journal]

        # CATEGORY SCORE BONUS

        maxbonus = 0
        for tag in paper.tags:
            if tag.term in self.category_scores:
                if maxbonus < self.category_scores[tag.term]:
                    maxbonus = self.category_scores[tag.term]
            if tag.term in self.tag_scores:
                score += self.tag_scores[tag.term]
        score += maxbonus

        # AUTHOR SCORE BONUS

        total_authors = " ".join(paper.authors).lower()
        for keyauthor in self.author_scores:
            if keyauthor in total_authors:
                score += self.author_scores[keyauthor]

        # NUM AUTHORS BONUS
        num_authors = len(paper.authors)
        score += self.author_num_bias * min(1,(num_authors-1)/(self.author_scale-1))

        # KEYWORD SCORE BONUS

        total_text = (paper.title + " " + paper.summary).replace("\n", " ").lower()
        for keyword in self.keyword_scores:
            if keyword in total_text:
                score += self.keyword_scores[keyword]
        
        return score