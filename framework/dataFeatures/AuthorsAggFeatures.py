import os
import json
import numpy as np
import modules.mongo_interface_backend as mib
import math
def getAuthorsFromJson(json_files_list,output_folder):



    json_files_list.sort(reverse=True)
    authors=dict()
    for filename in json_files_list:
        jsonFile = open(filename, encoding="utf8")
        data = json.load(jsonFile)
        for news in data:
            entry=dict()
            try:
                entry=news
                if not(news["Author"] in authors.keys()):
                    authors[news["Author"]] = list()

                authors[news["Author"]].append(entry)
            except Exception as e:
                print(e)
    with open(f'{output_folder + "/" + "authors.json" }', 'w', encoding='utf-8') as fp:
        json.dump(authors, fp, indent=4, ensure_ascii=False)



from collections import Counter
def getAuthorsTopics(author_data,year="all",top=10):
    org=list()
    per=list()
    loc=list()
    for news in author_data:
        if year!="all":
            year_news=int(news["Date"][0:4])
            if year_news != year:
                continue
        org=org+news["Organizations"]
        per=per+news["People"]
        loc=loc+news["Locations"]
    result=dict()
    result["Organizations"]=dict(Counter(org).most_common(top))
    result["People"] = dict(Counter(per).most_common(top))
    result["Locations"] = dict(Counter(loc).most_common(top))
    return(result)


def getAuthorsKeywords(author_data,year="all",top=10):

    keywords=dict()
    for news in author_data:
        if year!="all":
            year_news=int(news["Date"][0:4])
            if year_news != year:
                continue
        for kw,score in news["Keywords"]:
            if(not (kw in keywords.keys())):
                keywords[kw]=score
            else:
                keywords[kw]=keywords[kw]+score

    keywords=sorted(keywords.items(), key=lambda x: x[1])
    result=dict()
    result["kw_1"]=[]
    result["kw_2"] =[]
    result["kw_3"] =[]
    for kw,score in keywords:
        result["kw_"+str(len(kw.split()))].append({kw:score})
    result["kw_1"]=result["kw_1"][0:top]
    result["kw_2"] = result["kw_2"][0:top]
    result["kw_3"] = result["kw_3"][0:top]
    return(result)


def getAuthorReadibility(author_data):
    results=list()
    for news in author_data:
        avg_readibility=news["flesch_kincaidPT_Body"]+\
                        news["coleman_liauPT_Body"]+\
                        news["ariPT_Body"]+\
                        news["gunningFogPT"]

        avg_readibility=avg_readibility/4
        results.append(avg_readibility)
    read_score=np.array(results).mean()
    return({"Readibility":read_score,"Readibility_log": math.log(read_score) })


def getEntityDiversity(author_data):
    results=list()
    for news in author_data:

        news_std=np.array(list(news["Entities_#"].values())).std()
        if(np.isnan(news_std)):
            news_std=0
        news_div=len(news["Entities_#"])
        score=(0.1+news_std)*(5-news_div)
        results.append(score)
    #Low => more diversity
    #high count => more diversity ( at least one entity per type)
    # std x (5-count). the lower the score, the less diversity.
    # (5 instead 4 so the result is not 0 when 4 entities are included.  0.1 constant to avoid 0)
    eds=round(sum(results)/len(results),3)
    return({"EntityDiversityScore":eds,"EntityDiversityScore_log":math.log(eds)})


def getAverageEntity(author_data):
    results = list()
    for news in author_data:
        avg_ent = np.array(list(news["Entities_#"].values())).sum()/news["word_count_Body"]
        results.append(avg_ent)
    score=round(sum(results)/len(results),3)
    return({"Average_Entities":score})



def getAverageQuotation(author_data):
    results = list()
    for news in author_data:
        results.append(len(news["n_quotes"]))
    avg_quotes = round(sum(results)/len(results),3)
    return({"Avg_quotes":avg_quotes})


def getRelevantPOS(author_data):
    results_noun = list()
    results_verb = list()
    results_adj = list()
    pos=["NOUN","PROPN","ADJ","VERB"]
    for news in author_data:
        for p in pos:
            if p not in news["POS_tag_count"].keys():
                news["POS_tag_count"][p]=0
        results_noun.append((news["POS_tag_count"]["NOUN"]+news["POS_tag_count"]["PROPN"])/news["word_count_Body"])
        results_adj.append(news["POS_tag_count"]["ADJ"]/news["word_count_Body"])
        results_verb.append(news["POS_tag_count"]["VERB"]/news["word_count_Body"])
    results_noun=sum(results_noun)/len(results_noun)
    results_adj=sum(results_adj)/len(results_adj)
    results_verb=sum(results_verb)/len(results_verb)
    return({"Avg_Noun":results_noun,"Avg_Adj":results_adj,"Avg_Verb":results_verb})



def getAverageCorpusLength(author_data):
    word_c=0
    sent_c=0
    syl_c=0
    for news in author_data:
        word_c=word_c+news["word_count_Body"]
        sent_c=sent_c+news["sentence_count_Body"]
        syl_c=syl_c+news["syllable_count_Body"]

    word_c=round(word_c/len(author_data),2)
    sent_c = round(sent_c / len(author_data),2)
    syl_c = round(syl_c / len(author_data),2)
    syl_word=round(syl_c / word_c,2)
    return{"Avg_word_count":word_c,"Avg_sent_count":sent_c,"Avg_syl_per_word":syl_word,"Avg_word_count_log":math.log(word_c)}
d
def getAuthorPopularity(author_data):
    popularity=list()
    for news in author_data:
        popularity.append(news["Popularity"])
    score=sum(popularity)/len(popularity)
    return({"Avg_popularity":score})


#def getAuthorMostPopularArticles(author_name,top=10):








def getAuthorsFeatures(author_name,l_original):

    print(author_name)
    author_data=mib.getNewsByAuthor(l_original)
    author_feat=dict()
    author_feat.update({"Name":author_name})
    author_feat.update(getAuthorsTopics(author_data))
    author_feat.update(getAuthorsKeywords(author_data))
    author_feat.update(getAuthorReadibility(author_data))
    author_feat.update(getAverageEntity(author_data))
    author_feat.update(getEntityDiversity(author_data))
    author_feat.update(getAverageQuotation(author_data))
    author_feat.update(getAverageCorpusLength(author_data))
    author_feat.update(getRelevantPOS(author_data))

    return author_feat





def normalizeAuthorFeatures(data_all_authors,output_folder):


    feat2norm=["Readibility_log",
               "Average_Entities",
               "EntityDiversityScore_log",
               "Avg_quotes",
               "Avg_word_count_log",
               "Avg_sent_count",
               "Avg_Noun",
               "Avg_Adj",
               "Avg_Verb"]

    for feat in feat2norm:
        feat_max=max([author[feat] for author in data_all_authors])
        feat_min=min([author[feat] for author in data_all_authors])
        for author in data_all_authors:
            norm_feat=round((author[feat]-feat_min)/(feat_max-feat_min),2)
            if("_id" in author.keys()):
                del author["_id"]
            author.update({"norm_"+feat:norm_feat})

    with open(f'{output_folder+"authors_features.json"}', 'w', encoding='utf-8') as fp:
        json.dump(data_all_authors, fp, indent=4, ensure_ascii=False)

