import requests
from bs4 import BeautifulSoup
import json
import os

"""
Original function from NewsPublicArchive
"""
def getNewsArticles(pastURLs, news_htmlTag, news_htmlClass, titles_htmlTag, titles_htmlClass, snippets_htmlTag, snippets_htmlClass,
             links_htmlTag, links_htmlClass, authors_htmlTag, authors_htmlClass, filename, debug=False):

    dictOfTags = {'Title': [titles_htmlTag, titles_htmlClass],
                  'Snippet': [snippets_htmlTag, snippets_htmlClass],
                  'Link': [links_htmlTag, links_htmlClass],
                  'Author': [authors_htmlTag, authors_htmlClass]}

    ListOfContents = []
    ListOfProcessedLinks = []

    for i in range(len(pastURLs)):
        page = requests.get(pastURLs[i])
        soup = BeautifulSoup(page.content, 'html.parser', from_encoding="UTF-8")
        ListOfTagContents = soup.find_all(news_htmlTag, class_=news_htmlClass)
        for content in ListOfTagContents:
            dictOfFeatures = {}
            for key in dictOfTags:
                try:
                    if key == "Link":
                        link = content.find(dictOfTags[key][0], class_=dictOfTags[key][1]).get("href").strip()
                        if link.startswith('/noFrame/replay/'):
                            link = link.replace('/noFrame/replay/', 'https://arquivo.pt/wayback/')
                        dictOfFeatures[key] = link
                    else:
                        dictOfFeatures[key] = content.find(dictOfTags[key][0], class_=dictOfTags[key][1]).get_text().strip()
                except:
                    dictOfFeatures[key] = ' '
            if link not in ListOfProcessedLinks:
                ListOfProcessedLinks.append(link)
                ListOfContents.append(dictOfFeatures)


        if debug == True:
            if i != 0 and i % 1 == 0:
                print(f"\r{100 * i / len(pastURLs):.2f}%", end='')
                if i == len(pastURLs) - 1:
                    print(f"\r100.00%", end='')
    path = "data_raw/"

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f'{path + filename}', 'w', encoding='utf-8') as fp:
        json.dump(ListOfContents, fp, indent=4, ensure_ascii=False)


"""
New function to search articles by configuration file
"""

def getNewsArticlesByConfig(pastURLs,config, filename, debug=False):




    dictOfTags = {'Title': [config["titles_htmlTag"], config["titles_htmlClass"]],
                  'Snippet': [config["snippets_htmlTag"], config["snippets_htmlClass"]],
                  'Link': [config["links_htmlTag"], config["links_htmlClass"]],
                  'Author':[config["authors_htmlTag"], config["authors_htmlClass"]]}

    if "topics_htmlTag" in config.keys():
        dictOfTags.update({"Topic":[config["topics_htmlTag"], config["topics_htmlClass"]]})

    if "shares_htmlTag" in config.keys():
        dictOfTags.update({"Shares": [config["shares_htmlTag"], config["shares_htmlClass"]]})

    if "comments_htmlTag" in config.keys():
        dictOfTags.update({"Comments": [config["comments_htmlTag"], config["comments_htmlClass"]]})

    ListOfContents = []
    ListOfProcessedLinks = []

    for i in range(len(pastURLs)):
        page = requests.get(pastURLs[i])
        soup = BeautifulSoup(page.content, 'html.parser', from_encoding="UTF-8")
        ListOfTagContents = soup.find_all(config["news_htmlTag"], class_=config["news_htmlClass"])
        for content in ListOfTagContents:
            dictOfFeatures = {}
            dictOfFeatures.update({"Year": config["Year"]})
            for key in dictOfTags:
                try:
                    if key == "Link":
                        link = content.find(dictOfTags[key][0], class_=dictOfTags[key][1]).get("href").strip()
                        if link.startswith('/noFrame/replay/'):
                            link = link.replace('/noFrame/replay/', 'https://arquivo.pt/wayback/')
                        dictOfFeatures[key] = link
                    else:
                        dictOfFeatures[key] = content.find(dictOfTags[key][0], class_=dictOfTags[key][1]).get_text().strip()
                except:
                    dictOfFeatures[key] = ' '
            if link not in ListOfProcessedLinks:
                ListOfProcessedLinks.append(link)
                ListOfContents.append(dictOfFeatures)

            dictOfFeatures["Shares"]=dictOfFeatures["Shares"].replace("partilhas","")
            dictOfFeatures["Comments"]=dictOfFeatures["Comments"].replace("comentários","")



        if debug == True:
            if i != 0 and i % 1 == 0:
                print(f"\r{100 * i / len(pastURLs):.2f}%", end='')
                if i == len(pastURLs) - 1:
                    print(f"\r100.00%", end='')
    path = "data_raw/"

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f'{path + filename}', 'w', encoding='utf-8') as fp:
        json.dump(ListOfContents, fp, indent=4, ensure_ascii=False)

