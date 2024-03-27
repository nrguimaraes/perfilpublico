#https://arquivo.pt/wayback/cdx?url=publico.pt/*&from=20140302000000&to=20140301000000
#https://arquivo.pt/wayback/cdx?url=publico.pt/*&filter=collection:IA&from=1997&to=1998



#por ano, por source

#https://arquivo.pt/wayback/cdx?url=publico.pt/*&from=1997&to=1998

#https://arquivo.pt/wayback/cdx?url=publico.pt&filter=collection:IA&from=1997&to=1998

import requests
import json
import cdx_config






def getUrlList(url,year):
    api_url = 'https://arquivo.pt/wayback/cdx'
    print(year)
# Define query parameters
    params = {'url': url,
              #'filter': 'collection:IA',
              'from:':year,
              'to':year,
              'fields':'url,timestamp,status',
              'output':'json'
              #'limit':10
              }
    print(params)
# Make a GET request with parameters
    entries=[]
    try:
        response = requests.get(api_url, params=params)
        entries = response.text.split("\n")
    except Exception as e:
        print("ERROR GETTING URL LIST FOR: " + url + "::" +str(e) )

    result=[]
    for e in entries:
        #print(e)
        try:
            json_dict = json.loads(e)
            result.append(json_dict)
        except Exception as e:
            print("ERROR "  + str(e))
    return result
import os
import string

translator = str.maketrans('', '', string.punctuation)


def main():
    directory="cdxURLS"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created successfully.")
    else:
        print(f"Directory '{directory}' already exists.")

    for url in cdx_config.NEWS_PAPER_URLS:
        for year in cdx_config.YEARS:
            result=getUrlList(url,year)
            json_file = json.dumps(result, indent=4)

            filename=url.translate(translator)+"_"+str(year)+".json"
            file_path = os.path.join(directory,filename)
            # Write JSON string to the file
            with open(file_path, 'w') as f:
                f.write(json_file)



def countCrawledUrls(url):
    import os
    import json
    directory = "framework/cdxURLS"

    # Iterate through all files in the folder
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if the current item is a file
        if os.path.isfile(file_path):
            # Open the file
            with open(file_path, 'r') as file:
                # Do something with the file, for example, print its content
                print(file_path)
                json_data = json.load(file)
                print(len(json_data))


if __name__ == "__main__":
    main()