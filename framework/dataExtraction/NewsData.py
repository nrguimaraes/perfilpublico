import spacy
import json
from date_guesser_rc import guess_date
from yake import KeywordExtractor as YakeKW
import requests
from bs4 import BeautifulSoup
import os
from requests.exceptions import Timeout
import justext


"""
use for the extraction of the body of the news. use the argument get_corpus to try to get the body of the article
"""
def getNewsData(input_filename, output_filename, get_corpus=True):


    jsonFile = open(input_filename, encoding="utf8")
    data = json.load(jsonFile)
    model = 'pt_core_news_lg'
    nlp = spacy.load(model, disable=['tagger', 'parser'])

    sample = YakeKW(lan="pt")
    count=0
    for newsarticle in data:

        #check if it is wayback and if so replace by noFrame/replay

        if newsarticle["Link"].find("wayback")!=-1:
            newsarticle["Link"]=newsarticle["Link"].replace("wayback","noFrame/replay")
        count=count+1
        print("Done:"+str(round(count/len(data)*100,4)))
        try:
            response = requests.get(newsarticle["Link"])
        except Exception as e:
            print(e)
        # Get corpus
        try:
            if(get_corpus):
                corpus=getNewsCorpus(response,newsarticle["Link"])
                newsarticle["Body"]=corpus
                newsarticle.update(getSocialScore(response))






            # Try guess the  date of publication
            guess = guess_date(newsarticle['Link'])
            date = str(guess.date)[:10]
            newsarticle['Date'] = date

            # Get Keywords
            text = newsarticle['Title'] + ". " + newsarticle['Snippet']
            keywords = sample.extract_keywords(text)
            newsarticle['Keywords'] = keywords
            if(newsarticle["Title"]==newsarticle["Snippet"]):
                newsarticle["Snippet"]=""
            #save a variable to see if the paper is exclusive (i.e. behind paywall). Still in development. May change from year to year
            if(newsarticle["Title"]).startswith("Exclusivo para assinantes"):
                newsarticle["Tile"]=newsarticle["Title"].replace("Exclusivo para assinantes","")
                newsarticle["Exclusivo"]=True
            else:
                newsarticle["Exclusivo"]=False
            # Get Locations, Organizations and People
            doc = nlp(newsarticle['Title'] + " " + newsarticle['Snippet'])
            Locations = []
            Organizations = []
            People = []

            for ent in doc.ents:
                if ent.label_ == 'LOC':
                    Locations.append(ent.text)
                elif ent.label_ == 'ORG':
                    Organizations.append(ent.text)
                elif ent.label_ == 'PER':
                    People.append(ent.text)

            newsarticle['Locations'] = Locations
            newsarticle['Organizations'] = Organizations
            newsarticle['People'] = People

            # Get Image
            searchItem = ""
            if len(Organizations) > 0:
                searchItem = Organizations[0]
            elif len(People) > 0:
                searchItem = People[0]
            elif len(Locations) > 0:
                searchItem = Locations[0]
            elif len(keywords) > 0:
                searchItem = keywords[0][0]

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0 "}
            url_api = 'https://arquivo.pt/imagesearch'

            if len(date) > 0:
                fromDate = f'{date[:4]}0101000000'
                toDate = f'{date[:4]}1231235959'
                payload = {'q': searchItem, 'from': fromDate, 'to': toDate}
            else:
                payload = {'q': searchItem}
            try:
                r = requests.get(url_api, params=payload, headers=headers, timeout=60)
            except Timeout:
                print('Timeout has been raised.')

            content = r.json()

            try:
                img = content['responseItems'][0]['imgLinkToArchive']
                newsarticle['Image'] = img
            except:
                newsarticle['Image'] = ''
        except Exception as e:
            print(e)


    with open(f'{output_filename}', 'w', encoding='utf-8') as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)




from newspaper import Article

"""
Get the news corpus of the article based on the response of Beautiful soup
"""

def getNewsCorpus(response,url):


    paragraphs = justext.justext(response.content)
    text=""
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            text=text+" "+paragraph.text

    """
    if justtex fails tries with newspaper
    """

    if len(text)<=3:
        article = Article(url)
        article.download()
        article.parse()
        text=article.text

    return text





"""
Retrieve likes and comments from the article (must be modified for other sources)
"""
def getSocialScore(response):

    soup = BeautifulSoup(response.content, 'html.parser', from_encoding="UTF-8")

    ncomments = 0
    nshares=0
    for s in soup.findAll("span", class_="stat-tab__number"):
        if(len(s.text)!=0):
            nshares=int(s.text)+nshares

    #2015 span class="icon icon-share" class="icon icon-comment"

    for s in soup.findAll("span", class_="icon icon-share"):
        if (len(s.text) != 0):
            nshares=int(s.text)+nshares
            break

    for s in soup.findAll("span", class_="icon icon-comment"):
        if (len(s.text) != 0):
            ncomments=int(s.text)+ncomments
            break

    for s in soup.findAll("li",class_="entry-action-comment"):
        if (len(s.text) != 0):
            ncomments=int(s.text)+ncomments
            break

    return({"popularity_score":ncomments+nshares})










