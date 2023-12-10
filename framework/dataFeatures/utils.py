import string

from resources.syllable.silva2011 import syllable_separator
import pandas as pd
import spacy
import re


"""
Use to build the most common word dictionaries

"""
def buildCommonWordsVoc(top=5000):
    #Function to build the common word dictionary
    punct=list(string.punctuation)
    punct=[p for p in punct if p!="-"]+["«","»"]
    # Using readlines()
    file1 = open("resources/formas.totalpt.txt", 'r',encoding='ISO-8859-15', errors='ignore')
    Lines = file1.readlines()

    common_words=list()
    count = 0
    # Strips the newline character
    for line in Lines:
            if(len(common_words)>=top):
                break
            word=line.split("\t")[1].split("\n")[0]
            word = [w for w in word if w not in punct]

            word = "".join(word).lower()

            if (len(word) != 0):
                syll_count=1
                try:
                    syll_count=len(syllable_separator.separate(word))
                except Exception as e:
                    print(e)
                if(count<top and (not word.isnumeric()) and (len(re.findall('[a-zA-Z]', word))>0)):
                    common_words.append(word)
                    count=count+1
                    print(word)
    return common_words



#Build list

#common_words=buildCommonWordsVoc(top=5000)
#import pickle
#pickle.dump(common_words,open("resources/common_words.p","wb"))