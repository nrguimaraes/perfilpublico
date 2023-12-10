from dataExtraction.PastURLs import getPastURLs
import requests
from bs4 import BeautifulSoup
import json

from PIL import Image

"""
Get author meta-data (description, photo, email , role)
Works with publico.pt . Needs to be adapted for other sources (if this information is available)

#author_url="www.publico.pt/autores"
"""

def getAuthorInfo(author_name, author_url,page_URL, output_folder ):
    page = requests.get(author_url)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="UTF-8")
    filename=""
    description=""
    author_role=""
    """
    Photo Extraction
    """
    photo=soup.find("span", class_="avatar__pad").find("img")

    prefix_url="http"+page_URL.split("http")[1]
    image_url=photo["data-interchange"][1:].split(",")[0]

    image_url=prefix_url+image_url


    img = Image.open(requests.get(image_url, stream=True).raw)
    filename=output_folder+"/"+author_name+'.jpeg'
    img.save(filename)

    """
    Description Extraction
    """

    description=soup.find(class_="page__blurb").find("p").text



    author_role=soup.find(class_="author__role").text
    try:
        email=soup.find(class_="social-links__item social-tools__item--email").text.replace("\n","")[::-1]
    except:
        print("email not found for" + author_name)

    result={"filename":filename,
            "description":description,
            "author_role": author_role,
            "email": email
            }

    return(result)



"""
Function to extract all authors from the page. Alternative to get all authors from the DB.
"""
def extractAuthorNames(page_URL,authors_names):


    page = requests.get(page_URL)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="UTF-8")
    ListOfTagContents = soup.find_all("li", class_="grid__item index-list__item")



    authors_data=list()
    for li in ListOfTagContents:
        author_name=li.text
        if(author_name not in authors_names):
            author_url="https://arquivo.pt"+li.find("a").get("href")
            author_info=getAuthorInfo(author_name,author_url,page_URL)
            authors_data.append(author_info)
            authors_names.append(author_name)

    return(authors_names,authors_data)

def getPublicoAuthors(authors_url,output_folder,year_range=[2013,2023]):
    years=list(range(year_range[0],year_range[1]))
    years.sort(reverse=True)
    authors_names=[]
    data=list()


    for year in years:
        authors_URLS=getPastURLs(year=year,newspaper_url=authors_url)
        for url in authors_URLS:
            authors_names,data_temp=extractAuthorNames(url,authors_names)
            data=data+data_temp

        output_filename=output_folder+"/"+"authors_metadata_"+str(year)+".json"
        with open(f'{output_filename}', 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=4, ensure_ascii=False)




from google_images_search import GoogleImagesSearch


import os
from dotenv import load_dotenv

load_dotenv()
# you can provide API key and CX using arguments,
# or you can set environment variables: GCS_DEVELOPER_KEY, GCS_CX
gis = GoogleImagesSearch(os.getenv('GCS_DEVELOPER_KEY'), os.getenv('GCS_CX'))


def getGooglePhotoAuthorPhotos(authors_name, output_folder,site,limit=100):
    for author in authors_name:
        filename=author.replace(" ","").replace("/","_")
        #if a photo already exists we do nothing
        if((os.path.exists(output_folder+"/"+filename +".png") ) or
                (os.path.exists(output_folder+"/"+filename +".jpeg")) or
                 (os.path.exists(output_folder+"/" + filename + ".jpg")
                 )):
            print("exists : " + filename)

        else:
            _search_params = {
                'q': author + ' site:'+site,
                'num': 1,
            }
            count=count+1



            # this will search, download and resize:
            gis.search(search_params=_search_params, path_to_dir='data/google_f', width=171, height=171,custom_image_name=filename)

            if(count==limit):
                break


