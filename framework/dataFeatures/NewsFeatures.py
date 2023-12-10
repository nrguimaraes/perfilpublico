

import re
import spacy
import numpy as np
import pickle
from collections import Counter

model = 'pt_core_news_lg'
nlp = spacy.load(model)

emotions_dict=pickle.load(open("resources/emotions_dictPT.p","rb"))
#type: "Title","Snippet","Body"

#sentiment lexicon without emoticons and hashtags
sentiment_lexicon=pickle.load(open("resources/oplexicon_filtered.p","rb"))
def getQuotations(newsarticle):
    corpus=newsarticle["Body"]
    corpus=corpus.replace("“", '"')
    corpus = corpus.replace("”", '"')
    regexPattern = '"' + '(.+?)' + '"'
    quotes=(re.findall(regexPattern, corpus))
    return {"n_quotes":quotes}





def get_pos(newsarticle):
    doc=nlp(newsarticle["Body"])
    result_pos=dict()
    for token in doc:
        if token.pos_ in result_pos.keys():
            result_pos[token.pos_]=result_pos[token.pos_]+1
        else:
            result_pos[token.pos_] =1

    return {"POS_tag_count":result_pos}




def get_entities(newsarticle):
    doc=nlp(newsarticle["Body"])
    result_ent=dict()
    for ent in doc.ents:
        if not (ent.label_ in result_ent.keys()):
            result_ent[ent.label_]=0
        result_ent[ent.label_] =result_ent[ent.label_]+1
    return {"Entities_#":result_ent}



def getEmotionandSentiment(newsarticle,type):
    text=newsarticle[type]
    text=text.lower()
    doc=nlp(text)
    emotions_list_1 = list()
    emotions_list_2 = list()
    emotions_list_3 = list()
    sentiment_pos=0
    sentiment_neg = 0
    sentiment_neu=0
    for word in doc:
        token=word.text
        if token in emotions_dict.keys():
            emotions_list_1.append(emotions_dict[token][0])
            emotions_list_2.append(emotions_dict[token][1])
            emotions_list_3.append(emotions_dict[token][2])
        if token in sentiment_lexicon.keys():
            token_pol=sentiment_lexicon[token]
            if(token_pol>0):
                sentiment_pos=sentiment_pos+1
            elif(token_pol==0):
                sentiment_neu = sentiment_neu+1
            else:
                sentiment_neg = sentiment_neg + 1
    #remove duplicados nos casos em que as supra categorias nao tem  sub categorias (super/basicas)
    emotions_list_3=[x for x in emotions_list_3 if x not in ["SURPRESA","EMOÇÕES NÃO ESPECÍFICAS","INDIFERENÇA"]]
    emotions_list_2=[x for x in emotions_list_2 if x not in ["SURPRESA","EMOÇÕES NÃO ESPECÍFICAS","INDIFERENÇA"]]

    result = dict()


    result["Emo_Supra_"+str(type)]=dict(Counter(emotions_list_1))
    result["Emo_Super_"+str(type)]=dict(Counter(emotions_list_2))
    result["Emo_Basic_"+str(type)]=dict(Counter(emotions_list_3))
    result["Sentiment_"+str(type)]={"pos":sentiment_pos,"neu":sentiment_neu,"neg":sentiment_neg}
    return result






def wordCount (newsarticle,type):
	doc = nlp(newsarticle[type])
	count=0
	for token in doc:
		word = token.text
		word_clas = token.tag_
		#punctuations are not words
		if word_clas != "PUNCT" :
			count=count+1
			#print word

	return {"word_count_"+str(type):count}



def sentence_count (newsarticle,type):
	doc = nlp(newsarticle[type])
	count=0
	for d in doc.sents:
		count=count+1
	return {"sentence_count_"+str(type):count}



def avg_word_per_sentence (newsarticle,type):
	x=0
	try:
		x=newsarticle["word_count_"+str(type)] / newsarticle["sentence_count_"+str(type)]
	except:
		x=0

	return {"avg_word_per_sentence_"+str(type): float(x)}






def avg_sentence_length (newsarticle,type):
    doc = nlp(newsarticle[type])
    sent_count=list()
    for d in doc.sents:
        count = 0
        for token in d:
            if token.tag_ != "PUNCT":
                count=count+1

        #Sometimes some sentences are returned with empty tokens
        if(count>2):
            sent_count.append(count)
        return({"avg_sent_count":round(np.mean(sent_count))})


def avg_word_length (newsarticle,type):
    doc = nlp(newsarticle[type])
    word_sum = list()
    for token in doc:
        word = token.text
        word_clas = token.tag_
        # punctuations are not words

        if word_clas != "PUNCT":
            word_sum.append(len(word))

        # print word
    return({"avg_word_length":round(np.mean(word_sum),2)})


import resources.tools as tools
def syllable_count(newsarticle,type):

    from resources.syllable.silva2011 import syllable_separator
    count=0
    count_error=0
    doc = nlp(newsarticle[type])

    for w in doc:
        w_clean = tools.clear_string(w.text)
        w = tools.clear_string(w_clean)
        if len(w)>1:
            #result =
            #print ('separando palavra:%s' %w_clean)
            try:
                syllables = syllable_separator.separate(w)
                #print(syllables)
                leng = len(syllables)
                count+=leng
                #print ('word:%s syllables:%s %i ' %(w, syllables,leng))
            except:
                count_error+=1
                #print ('ERROR ON WORD: %s' %w)


    return {"syllable_count_"+str(type):count}



def avg_syllables_per_word (newsarticle,type):
	x=0
	try:
		x=  float(newsarticle["syllable_count_"+str(type)] / newsarticle["word_count_"+str(type)])
	except:
		x=0
	return{"avg_syllables_per_word_"+str(type): x}


import string

def number_of_letters(newsarticle,type):
    w = tools.clear_string(newsarticle[type])
    w=[t for t in w if t not in string.punctuation+" "+"\n"]
    return({"letter_count_"+str(type):len(w)})
def contentDensity(newsarticle,type):

    nVerb = 0
    nNoun = 0
    nAdjective = 0
    nAdverb = 0
    doc=nlp(newsarticle[type])
    for tag in doc:
        word = tag.text
        word_clas = tag.tag_
        # if word_clas == "VB" or word_clas == "VBD" or word_clas == "VBG" or word_clas == "VBN" or word_clas == "VBP" or word_clas == "VBZ" :
        if word_clas == "VERB":
            nVerb += 1
        # elif word_clas == "NN" or word_clas == "NNS" or word_clas == "NNP" or word_clas == "NNPS" :
        elif word_clas == "NOUN":
            nNoun += 1
        # elif word_clas == "JJ" or word_clas == "JJR" or word_clas == "JJS" :
        elif word_clas == "ADJ":
            nAdjective += 1
        # elif word_clas == "RB" or word_clas == "RBR" or word_clas == "RBS":
        elif word_clas == "ADV":
            nAdverb += 1

    contentDensity = 10
    # print ('somatorio %i'%(nVerb+nNoun+nAdjective+nAdverb))
    # print ('dividido por %i'%len(postag))

    content_words = nVerb + nNoun + nAdjective + nAdverb
    function_words = float(len(doc) - content_words)

    content_density = content_words / function_words if function_words else 0

    return {"content_density_"+str(type): content_density}



import resources.dictionaries  as dic
def getConnectives(newsarticle,type,connectiveType):

    ConnectiveCount = 0
    doc=nlp(newsarticle[type])
    if connectiveType=="aditive":
        dic_cat=dic.DIC_ADITIVE
    elif connectiveType=="temporal":
        dic_cat = dic.DIC_TEMP
    elif connectiveType == "casual":
        dic_cat = dic.DIC_CASUAL
    elif connectiveType == "logic":
        dic_cat = dic.DIC_LOGIC
    elif connectiveType == "positive":
        dic_cat = dic.DIC_POSITIVE
    elif connectiveType == "negative":
        dic_cat = dic.DIC_NEGATIVE
    else:
        print("connective type is not a valid option")
        return None
    for w in doc:
        cw=w.text.lower()
        #print(w.tag_)
        if (w.tag_ in ["CONJ","SCONJ","CCONJ"] and cw in dic_cat):
            #print ('aditive: %s' %w)
            ConnectiveCount+=1

    #print(ConnectiveCount)
    return ConnectiveCount


def ConnectiveIncidence(newsarticle,type,connectiveType):
    connective = getConnectives(newsarticle,type,connectiveType)
    try:
        score = connective / (newsarticle["word_count_" + str(type)] )
    except:
        score=0
    #print(score)
    return {"ConnectiveIncidence_" + str(type) + "_" + str(connectiveType): score}



#asd

common_words=pickle.load(open("resources/common_words.p","rb"))
import string
def complex_word_count(newsarticle,type):
    text=newsarticle[type].translate(str.maketrans('', '', string.punctuation))
    words=text.lower().split()
    complex_words=[w for w in words if (w not in common_words)]
    return({"complex_word_count_"+ str(type):len(complex_words)})


def gunningFog(newsarticle,type):
    wc = newsarticle["word_count_" + str(type)]
    sc = newsarticle["sentence_count_" + str(type)]
    complex_words=newsarticle["complex_word_count_"+ str(type)]
    gunfog=0.49*(wc/sc)+19*(complex_words/wc)
    return({"gunningFogPT":gunfog})

def fleschPT(newsarticle,type):
    wc=newsarticle["word_count_" + str(type)]
    sc=newsarticle["sentence_count_"+str(type)]
    sylc=newsarticle["syllable_count_"+str(type)]
    flesch=226-1.04*(wc/sc)-72*(sylc/wc)
    return ({"fleschPT_"+str(type):flesch})

def flesch_kincaidPT(newsarticle,type):
    wc=newsarticle["word_count_" + str(type)]
    sc=newsarticle["sentence_count_"+str(type)]
    sylc=newsarticle["syllable_count_"+str(type)]
    flesch_kincaid=0.36*(wc/sc)+10.4*(sylc/wc)-18
    return ({"flesch_kincaidPT_"+str(type):flesch_kincaid})

def gulpease_index(newsarticle,type):
    wc = newsarticle["word_count_" + str(type)]
    sc = newsarticle["sentence_count_" + str(type)]
    lc = newsarticle["letter_count_" + str(type)]
    gulpease=89+((300*sc-10*lc)/wc)
    return({"gulpease_index_"+str(type):gulpease})


def ariPT(newsarticle,type):
    wc=newsarticle["word_count_" + str(type)]
    sc=newsarticle["sentence_count_"+str(type)]
    lc = newsarticle["letter_count_" + str(type)]
    ari=4.6*(lc/wc)+0.44*(wc/sc)-20
    return ({"ariPT_"+str(type):ari})


def coleman_liaupt(newsarticle,type):
    wc=newsarticle["word_count_" + str(type)]
    sc=newsarticle["sentence_count_"+str(type)]
    lc = newsarticle["letter_count_" + str(type)]
    coleman=5.4*(lc/wc)-21*(sc/wc)-14
    return ({"coleman_liauPT_"+str(type):coleman})


"""
#Not working properly
def yearofNews(newsarticle):
    return({"Year":newsarticle["Date"][0:4]})

"""
def getFeatures(newsarticle):
    result_features=newsarticle

    #result_features.update(yearofNews(newsarticle))
    result_features.update(getQuotations(newsarticle))
    result_features.update(get_pos(newsarticle))
    result_features.update(get_entities(newsarticle))
    result_features.update(getEmotionandSentiment(newsarticle,"Body"))

    result_features.update(wordCount(newsarticle,"Body"))
    result_features.update(sentence_count(newsarticle,"Body"))
    result_features.update(syllable_count(newsarticle,"Body"))
    result_features.update(complex_word_count(newsarticle,"Body"))

    result_features.update(avg_syllables_per_word(newsarticle, "Body"))
    result_features.update(number_of_letters(newsarticle,"Body"))
    result_features.update(contentDensity(newsarticle, "Body"))
    for connective in ["aditive","temporal","casual","positive","negative"]:
        result_features.update(ConnectiveIncidence(newsarticle, "Body", connective))
    #readibility metrics

    result_features.update(fleschPT(newsarticle,"Body"))
    result_features.update(flesch_kincaidPT(newsarticle,"Body"))
    result_features.update(coleman_liaupt(newsarticle,"Body"))
    result_features.update(ariPT(newsarticle,"Body"))
    result_features.update(gulpease_index(newsarticle,"Body"))
    result_features.update(gunningFog(newsarticle,"Body"))




    return(result_features)








