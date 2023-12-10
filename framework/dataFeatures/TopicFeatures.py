import gensim



"""
Not used
"""
def trainTopicModel(list_entities):

    #create document of entities
    ent_news = []
    for doc in list_entities:
        ent_news.append(doc["Locations"] + doc["Organizations"] + doc["People"])

    dictionary = gensim.corpora.Dictionary(ent_news)
    dictionary.filter_extremes(no_below=15, no_above=0.75, keep_n=10000)
    bow_corpus = [dictionary.doc2bow(doc) for doc in ent_news]
    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=10, id2word=dictionary, passes=2, workers=4)
    return dictionary,lda_model


#    for idx, topic in lda_model.print_topics(-1):
#        print('Topic: {} \nWords: {}'.format(idx, topic))

def classifyNewsIntoTopic(news,dictionary,lda_model):
    ents=news["Locations"]+news["Organizations"]+news["People"]
    bow_vector = dictionary.doc2bow(ents)
    top_topic=sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1])[0][0]

    top_topic_terms=lda_model.show_topic(top_topic)
    top_topic_terms=[term for term,score in top_topic_terms]

    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1]):
        print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))




