import re
from urllib import response

import requests
from bs4 import BeautifulSoup

class ArquivoPT:

    def fetch_summary(self, link):

        url = link.replace("/wayback/", "/wayback/")
        url = re.sub(
            r"/wayback/(\d+)/",
            r"/wayback/\1mp_/",
            url
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                return meta["content"].strip()

            blurb = soup.find("div", class_="story__blurb")
            if blurb:
                return blurb.get_text(" ", strip=True)

            return ""

        except Exception:
            return ""
        
        
    def fetch_many(self, articles):

        summaries = []

        for article in articles:

            summary = self.fetch_summary(article["Link"])

            summaries.append({
                "title": article["Title"],
                "date": article["ExtractionDate"],
                "summary": summary
            })

        return summaries