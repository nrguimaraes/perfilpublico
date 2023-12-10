import pandas as pd
import pymongo
import re
from bson.objectid import ObjectId

import os
from modules.mongov import client

#uri =os.environ.get("MONGO_URI")
#client = MongoClient(uri)

db = client.PerfilPublicoAll

author_collection = db.AuthorsFeaturesAll
author_metadata_collection= db.AuthorsMetadata
news_collection=db.NewsFeaturesAll
topics_collection = db.Topics
news_topic_collection=db.NewsTopics

def searchAuthor(name):
    results=author_collection.find({"Name":name},limit=2)
    return_list=list()
    for r in results:
        return_list.append(r)
    if(len(return_list)==1):
        return return_list[0]
    else:
        return_list=list()
        query = re.compile('.*' + name + '.*', re.IGNORECASE)  # compile the regex
        similar_results=author_collection.find({"Name":query},{"Name":1})
        for r in similar_results:
            return_list.append(r)
        return return_list
    return None



def getAuthorMetadata(name):
    result=author_metadata_collection.find_one({"name":name})
    if(result==None):
        result={}
    essential_keys=["author_role","description","newspaper"]
    for r in essential_keys:
        if r not in result:
            result[r]=""
    return result

def getAuthorByID(id):
    result=author_collection.find_one({"_id":ObjectId(id)})
    return result

def getAuthorNewsCount(name):
    years_in=[str(year) for year in range(2013,2023)]

    result_d=dict()
    for year in years_in:
        result_d.update({year:0})
    query= [
        {"$match": { "Author_clean": str(name) ,"Year":{"$in":years_in}}},
        {"$group": {
            "_id": {
                "Year":"$Year",
                "Title":"$Title",

            },
            "count": {"$sum": 1}}},

        {"$group": {
            "_id": {
                "Year": "$_id.Year",
                #"Title": "$_id.Title",

            },
            "totalCount": {"$sum": "$count"},
            "distinctCount": {"$sum": 1}
        }},

        { "$sort": {"Year": 1}}
         ]

    result=news_collection.aggregate(query)
    news_by_year=list()

    for r in result:
        result_d.update({r["_id"]["Year"]:r["distinctCount"]})
        #news_by_year.append({"Year":int(r["_id"]["Year"]),"Count":r["distinctCount"]})
    #for entry in result_d
    max_year=""
    max_value=0
    for key,value in result_d.items():
        news_by_year.append({"Year": int(key), "Count": value})
        if(value>max_value):
            max_year=key
            max_value=value

    return max_year,news_by_year

import pandas as pd
def getAuthorNewsByYear(name,year):
    year=str(year)
    results=news_collection.find({"Author_clean":name,"Year":year},{"Title":1,"Link":1,"ExtractionDate":1}).sort("ExtractionDate")
    return_list = list()
    for r in results:
        r["Link"]=r["Link"].replace("noFrame/replay","wayback")
        r["ExtractionDate"]=r["ExtractionDate"][0:4]+"-"+r["ExtractionDate"][4:6]+"-"+r["ExtractionDate"][6:8]
        return_list.append(r)
    result_df=pd.DataFrame.from_dict(return_list)
    result_df.drop_duplicates(subset=["Title"], keep="last",inplace=True)
    return result_df



def getAuthorNewsByYearAndTopic(name,year,topic):
    year=str(year)
    topic_query=re.compile('.*' + topic + '.*', re.IGNORECASE)
    results=news_topic_collection.find({"Author_clean":name,"Year":year,"Topics":topic_query},{"Title":1,"Link":1,"ExtractionDate":1}).sort("ExtractionDate")
    return_list = list()
    for r in results:
        r["Link"]=r["Link"].replace("noFrame/replay","wayback")
        r["ExtractionDate"]=r["ExtractionDate"][0:4]+"-"+r["ExtractionDate"][4:6]+"-"+r["ExtractionDate"][6:8]
        return_list.append(r)
    result_df=pd.DataFrame.from_dict(return_list)
    result_df.drop_duplicates(subset=["Title"], keep="last",inplace=True)
    return result_df




def getAuthorTopicNewsCount(name,topic):
    years_in=[str(year) for year in range(2013,2023)]
    topic_query = re.compile('.*' + topic + '.*', re.IGNORECASE)
    result_d=dict()
    for year in years_in:
        result_d.update({year:0})
    query= [
        {"$match": { "Author_clean": str(name) ,"Year":{"$in":years_in},"Topics":topic_query}},
        {"$group": {
            "_id": {
                "Year":"$Year",
                "Title":"$Title",

            },
            "count": {"$sum": 1}}},

        {"$group": {
            "_id": {
                "Year": "$_id.Year",
                #"Title": "$_id.Title",

            },
            "totalCount": {"$sum": "$count"},
            "distinctCount": {"$sum": 1}
        }},

        { "$sort": {"Year": 1}}
         ]

    result=news_topic_collection.aggregate(query)
    news_by_year=list()

    for r in result:
        result_d.update({r["_id"]["Year"]:r["distinctCount"]})
        #news_by_year.append({"Year":int(r["_id"]["Year"]),"Count":r["distinctCount"]})
    #for entry in result_d
    max_year=""
    max_value=0
    for key,value in result_d.items():
        news_by_year.append({"Year": int(key), "Count": value})
        if(value>max_value):
            max_year=key
            max_value=value

    return max_year,news_by_year









def getAllNewsEntities(limit):

    results=news_collection.find({},{"Locations":1,"Organizations":1,"People":1}).limit(limit)
    return_list = list()
    for r in results:
        return_list.append(r)

    return return_list




def getMetricsByAuthor():
    results=author_collection.find({},{"Name":1,
                                       "norm_Readibility_log":1,
                                       #"norm_Average_Entities":1,
                                       "norm_EntityDiversityScore_log":1,
                                      # "norm_Avg_quotes":1,
                                       "norm_Avg_word_count_log":1})

    return_list = list()
    for data in results:
        reading_value = round(data["norm_Readibility_log"] * 100,2)
        factual_value = round( data["norm_EntityDiversityScore_log"]  * 100,2)
        length = round(data["norm_Avg_word_count_log"] * 100,2)
        return_list.append({"id":data["_id"],"author":data["Name"],"reading_value":reading_value,"factual_value":factual_value,"length":length})

    return pd.DataFrame.from_dict(return_list)


def getRecommendationAuthors(range_read,range_opinion,range_length):
    results = author_collection.find( {"norm_Readibility_log": {
                                            "$gte":range_read[0]/100 ,
                                            "$lte": range_read[1]/100
                                                            },
                                        "norm_EntityDiversityScore_log": {
                                            "$gte": range_opinion[0] / 100,
                                            "$lte": range_opinion[1] / 100
                                        },

                                        "norm_Avg_word_count_log": {
                                            "$gte": range_length[0] / 100,
                                            "$lte": range_length[1] / 100
                                        },
    }, {"Name": 1})
    return_list=list()
    for r in results:
        return_list.append((r["_id"],r["Name"]))
    return return_list





def searchTopic(search_query):
    results = topics_collection.find({"topic":  re.compile(search_query, re.IGNORECASE)}).sort([("value",pymongo.DESCENDING)])
    return_list = list()
    for r in results:
        return_list.append(r)
    return return_list


def searchSimilarTopics(search_query):
    return_list=list()
    query = re.compile('.*' + search_query + '.*', re.IGNORECASE)  # compile the regex
    similar_results = topics_collection.find({"topic": query})
    ids=list()
    for r in similar_results:
        if r["author_id"] not in ids:
            ids.append(r["author_id"])
            return_list.append(r)
    return return_list



def countAuthors():
    return(author_collection.count_documents({}))


def countNews():
    return (author_collection.count_documents({}))
#def insertMetaDataAuthors():

