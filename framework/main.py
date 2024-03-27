import os

from dataExtraction.NewsArticles import getNewsArticlesByConfig
from dataExtraction.publico_scrapper_configs import PUBLICO_CONFIGURATIONS
from dataExtraction.PastURLs import getPastURLs

urls=getPastURLs(2013,"http://www.publico.pt",1,12)
urls=getPastURLs(2013,"http://www.dn.pt",1,12)


for config in PUBLICO_CONFIGURATIONS:
    getNewsArticlesByConfig(urls,config,debug=True)