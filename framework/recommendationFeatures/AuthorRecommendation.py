import os

import numpy as np
import pandas as pd
from pymongo import MongoClient


client = MongoClient(os.getenv("MONGO_URI"))

db = client.PerfilPublicoAll

author_collection = db.AuthorsFeaturesAll
author_metadata_collection= db.AuthorsMetadata
news_collection=db.NewsFeaturesAll
topics_collection = db.Topics


def getMetricsByAuthor():
    results=author_collection.find({},{"Name":1,
                                       "norm_Readibility_log":1,
                                       "norm_EntityDiversityScore_log":1,
                                       "norm_Avg_word_count_log":1})

    return_list = list()
    for data in results:
        reading_value = round(data["norm_Readibility_log"] * 100,2)
        factual_value = round( data["norm_EntityDiversityScore_log"]  * 100,2)
        length = round(data["norm_Avg_word_count_log"] * 100,2)
        return_list.append({"id":data["_id"],"author":data["Name"],"reading_value":reading_value,"factual_value":factual_value,"length":length})

    return pd.DataFrame.from_dict(return_list)



def getRelatedAuthorsByMetric(author,limit=10):
    reading_value = round(author["norm_Readibility_log"] * 100,2)
    factual_value = round(author["norm_EntityDiversityScore_log"] * 100,2)
    length = round(author["norm_Avg_word_count_log"] * 100,2)
    scores=np.array([reading_value,factual_value,length])
    df=getMetricsByAuthor()
    results=list()
    for index,row in df.iterrows():
        if(row["author"]!=author["Name"]):
            scores_compare=np.array([row["reading_value"],row["factual_value"],row["length"]])
            dist = np.linalg.norm(scores_compare - scores)
            results.append({"id":row["id"],"author":row["author"],"sim":dist})
    results_df=pd.DataFrame.from_dict(results)
    results_df.sort_values(by="sim",inplace=True)
    results_df.dropna(inplace=True)
    results_df=results_df.head(limit)
    return results_df






