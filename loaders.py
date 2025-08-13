import os
from params import *
from funcs import *
from feedparser import parse
import datetime
import time
from paper import *

# returns list of "entry"-formatted objects from feedparser
def get_rss_feed(url):
    feed_obj = parse(url)
    return feed_obj.entries

def load_arxiv() -> list[ArxivPaper]:
    os.system('cls' if os.name == 'nt' else 'clear')

    cat_str = ""
    for cat in CATEGORIES:
        if cat_str != "":
            cat_str += "+OR+cat%3A"
        cat_str += cat
    # url formatting here: https://ronpay.github.io/arxiv-rss-feed-generator/
    url = f"http://export.arxiv.org/api/query?search_query=cat%3A{cat_str}&sortBy=submittedDate&sortOrder=descending&start=0&max_results={NUM_PAPERS}"

    feed = get_rss_feed(url)

    papers = []

    for paper in feed:
        authors = [author.name for author in paper.authors]
        arxiv_id = paper.link[paper.link.rfind("/")+1:]

        fulltime = paper["published_parsed"]
        
        paper_date = datetime.datetime.fromtimestamp(time.mktime(fulltime))
        
        extra_days = (fulltime.tm_hour >= 18)

        temp = (fulltime.tm_hour >= 18) + fulltime.tm_wday

        # make approximately correct adjustments to match arxiv's "publishing" schedule
        if temp == 4:
            extra_days += 3
        elif temp == 5:
            extra_days += 3
        elif temp == 6:
            extra_days += 2
        elif temp == 7:
            extra_days += 1
        else:
            extra_days += 1
        
        paper_date += datetime.timedelta(days=extra_days)

        mod_arxiv_id = arxiv_id[:arxiv_id.index("v")]

        website_url = paper['links'][0]['href']

        papers.append(ArxivPaper(paper.title, authors, "https://arxiv.org/pdf/"+arxiv_id, "https://doi.org/10.48550/arXiv."+mod_arxiv_id, "arxiv", paper.updated, paper.summary, paper.tags, publish_date=paper_date.date(), website_url = website_url))

    return papers

def load_prb() -> list[PhysicalReviewPaper]:

    feed = get_rss_feed("https://feeds.aps.org/rss/recent/prb.xml")

    #keys: ['id', 'title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'content', 'authors', 'author', 'author_detail', 'updated', 'updated_parsed', 'rights', 'rights_detail', 'dc_source', 'dc_type', 'dc_identifier', 'prism_doi', 'prism_publicationname', 'prism_volume', 'prism_number', 'prism_publicationdate', 'prism_url', 'prism_startingpage', 'tags', 'prism_section']

    papers = []

    for entry in feed:
        title = entry['title_detail']['value']
        author_str = entry['authors'][0]['name']
        authors_temp = (author_str.replace(", and ",", ").replace(" and ", ", ")).split(",")
        authors = [author[1:] if author[0]==" " else author for author in authors_temp]
        tags = entry['tags']
        temp_sum = entry['summary']
        if ("<p>" in temp_sum) and ("</p>" in temp_sum):
            summary = scrub_html_tags(temp_sum[temp_sum.index("<p>")+3:temp_sum.index("</p>")])
        else:
            summary = scrub_html_tags(temp_sum)
        doi = entry['dc_identifier']
        download_link = "https://journals.aps.org/prb/pdf/"+entry['dc_identifier'][4:]
        website_url = entry['prism_url']
        updated = entry['prism_publicationdate']

        papers.append(PhysicalReviewPaper(title, authors, download_link, doi, "prb", updated, summary, tags, website_url = website_url))

    return papers

def load_prl_cdm() -> list[PhysicalReviewPaper]:
    feed = get_rss_feed("https://feeds.aps.org/rss/tocsec/PRL-CondensedMatterStructureetc.xml")

    #keys: ['id', 'title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'content', 'authors', 'author', 'author_detail', 'updated', 'updated_parsed', 'rights', 'rights_detail', 'dc_source', 'dc_type', 'dc_identifier', 'prism_doi', 'prism_publicationname', 'prism_volume', 'prism_number', 'prism_publicationdate', 'prism_url', 'prism_startingpage', 'tags', 'prism_section']

    papers = []

    
    for entry in feed:
        title = entry['title_detail']['value']
        author_str = entry['authors'][0]['name']
        authors_temp = (author_str.replace(", and ",", ").replace(" and ", ", ")).split(",")
        authors = [author[1:] if author[0]==" " else author for author in authors_temp]
        tags = entry['tags']
        temp_sum = entry['summary']
        if ("<p>" in temp_sum) and ("</p>" in temp_sum):
            summary = scrub_html_tags(temp_sum[temp_sum.index("<p>")+3:temp_sum.index("</p>")])
        else:
            summary = scrub_html_tags(temp_sum)
        doi = entry['dc_identifier']
        download_link = "https://journals.aps.org/prl/pdf/"+entry['dc_identifier'][4:]
        updated = entry['prism_publicationdate']
        website_url = entry['prism_url']

        papers.append(PhysicalReviewPaper(title, authors, download_link, doi, "prl", updated, summary, tags, website_url = website_url))

    return papers

def load_ncomms() -> list[NaturePaper]:

    feed = get_rss_feed("https://www.nature.com/subjects/physical-sciences/ncomms.rss")

    papers = []

    
    for entry in feed:
        title = entry['title_detail']['value'].replace("<sub>", "_").replace("</sub>","").replace("<i>","").replace("</i>","")
        authors_temp = [author['name'] for author in entry['authors']] if 'authors' in entry else []
        authors_temp2 = [author[1:] if author[0]==" " else author for author in authors_temp]
        authors = [author[:-1] if author[-1]==" " else author for author in authors_temp2]
        tags = [] 
        summary = "No abstract available from this RSS feed"
        doi = entry['id'].replace("https://www.nature.com/articles","doi.org/10.1038")
        download_link = entry['id']+".pdf"
        updated = time.strftime("%Y-%m-%d", entry["published_parsed"])
        website_url = entry['id']

        papers.append(NaturePaper(title, authors, download_link, doi, "ncomms", updated, summary, tags, website_url = website_url, author_class="c-article-author-list--short"))

    return papers

def load_nature(journal_short, journal_rss) -> list[NaturePaper]:
    
    feed = get_rss_feed(f"https://www.nature.com/{journal_rss}.rss")

    papers = []

    for entry in feed:
        title = entry['title_detail']['value'].replace("<sub>", "_").replace("</sub>","").replace("<i>","").replace("</i>","")
        if 'authors' in entry:
            authors = [author['name'] for author in entry['authors']]
        else:
            authors = []
        
        doi = entry['prism_doi']
        download_link = entry['prism_url']+".pdf"
        updated = entry['updated']

        if "</p>" in entry['summary']:
            summary = entry['summary'][entry['summary'].index("</p>")+4:]
        else:
            summary = "No abstract available from this RSS feed"

        papers.append(NaturePaper(title, authors, download_link, doi, journal_short, updated, summary, [], website_url = entry['id']))

    return papers


def load_acs(journal_short, journal_rss) -> list[ACSPaper]:
    
    feed = get_rss_feed(f"https://pubs.acs.org/action/showFeed?type=axatoc&feed=rss&jc={journal_rss}")

    papers = []

    
    for entry in feed:
        title = entry['title_detail']['value'].replace("<sub>", "_").replace("</sub>","").replace("<i>","").replace("</i>","").replace("[ASAP] ","")
        if 'authors' in entry:
            authors = entry['author'].replace(", and ",", ").split(", ")
        else:
            authors = []

        
        fulltime = entry["published_parsed"]
        
        paper_date = datetime.datetime.fromtimestamp(time.mktime(fulltime)).date()
        
        doi = entry['id']

        papers.append(ACSPaper(title, authors, "", doi, journal_short, [], website_url = entry['id'], publish_date=paper_date))

    return papers

def load_pnas(journal_short, journal_rss) -> list[PNASPaper]:
    
    feed = get_rss_feed(f"https://www.pnas.org/action/showFeed?type=searchTopic&taxonomyCode=topic&tagCode={journal_rss}")

    papers = []

    for entry in feed:

        summary = "No abstract available from this RSS feed"
        if "summary" in entry:
            summary = entry["summary"]
            if "Significance" in summary:
                summary = summary[summary.index("Significance")+len("Significance"):]


        title = entry['title_detail']['value'].replace("<sub>", "_").replace("</sub>","")
        if 'authors' in entry:
            authors = entry['author'].replace(", and ",", ").split(", ")
        else:
            authors = []

        paper_date = datetime.date.today()
        if "published_parsed" in entry:
            fulltime = entry["published_parsed"]
            paper_date = datetime.datetime.fromtimestamp(time.mktime(fulltime)).date()
        elif "updated_parsed" in entry:
            fulltime = entry["updated_parsed"]
            paper_date = datetime.datetime.fromtimestamp(time.mktime(fulltime)).date()

        doi = entry['id']

        papers.append(PNASPaper(title, authors, summary, "", doi, journal_short, [], website_url = entry['id'], publish_date=paper_date))

    return papers

def get_all_papers() -> list[Paper]:
    papers = []
    papers += load_arxiv()
    papers += load_ncomms()
    papers += load_prl_cdm()
    papers += load_prb()
    papers += load_nature("npjqm", "npjquantmats")
    papers += load_nature("nphoton", "nphoton")
    papers += load_nature("nmat", "nmat")
    papers += load_nature("nphys", "nphys")
    papers += load_nature("nnano", "nnano")
    papers += load_acs("acs applied nano", "aanmf6")
    papers += load_acs("acs nano letters", "nalefd")
    papers += load_acs("acs applied optical materials", "aaoma6")
    papers += load_pnas("pnas applied phys", "app-phys")
    papers += load_pnas("pnas applied phys", "phys")
    papers.sort()
    return papers