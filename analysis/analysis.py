import argparse
import numpy as np
import pandas as pd
import sys
import stats
import reddit_analysis
import twitter_analysis
from enum import Enum
from gender_coding import Word, getWuWordsFromFile
from langdetect import detect_langs
from typing import List, Tuple, Set, Dict
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegressionCV
from heapq import nlargest, nsmallest

class Gender(Enum):
    NEITHER = 2
    FEMALE = 1
    MALE = 0

# identify all words that either identify "male" or "female"
def getGenderedWords(genderedWordsPath: str) -> Tuple[List[Word], List[Word]]:
    genderedWords = getWuWordsFromFile(genderedWordsPath)

    male, female = ([], [])
    for word in genderedWords:
        if word.female == "1":
            female.append(word)
        elif word.female == "0":
            male.append(word)
    
    return (male, female)

def getPostGender(post: str, maleWords: Set[str], femaleWords: Set[str]) -> Gender:
    maleCount = 0
    femaleCount = 0
    for word in stats.wordsInText(post):
        if word in maleWords:
            maleCount += 1
        elif word in femaleWords:
            femaleCount += 1
    
    if maleCount > 0 and femaleCount == 0:
        return Gender.MALE
        
    if femaleCount > 0 and maleCount == 0:
        return Gender.FEMALE

    return Gender.NEITHER

def isLang(post: str, targetLang:str) -> bool:
    lang = None
    try:
        lang = str(detect_langs(post)[0])
    except:
        return False
    return targetLang in lang

def getGenderedPosts(posts: str, maleWords: List[Word], femaleWords: List[Word]) -> Tuple[List[str], List[int]]:
    maleWords = set([x.word for x in maleWords])
    femaleWords = set([x.word for x in femaleWords])
    
    genderedPosts = []
    genders = []
    for post in posts:
        gender = getPostGender(post, maleWords, femaleWords)
        if gender == Gender.NEITHER or not isLang(post, "en"):
            continue
        genderedPosts.append(post)
        genders.append(gender.value)
    
    return (genderedPosts, genders)

def bowFromTokens(tokens: List, bowTokens: List) -> List[int]:
    '''
        bowFromTokens assumes every token in bowTokens is hashable and unique.
    '''
    tokenToIndex = {}
    for i in range(len(bowTokens)):
        token = bowTokens[i]
        tokenToIndex[token] = i

    assert len(tokenToIndex) == len(bowTokens), '''every token in bowTokens should be hashable and unique
    got {} unique tokens
    expected {}'''.format(len(tokenToIndex), len(bowTokens))

    x = [0] * len(bowTokens)
    for token in tokens:
        if token in tokenToIndex:
            index = tokenToIndex[token]
            x[index] = 1
    return x

def makeBOW(posts: List[str], bowTokens: List, tokenFn=stats.wordsInText) -> List[List[int]]:
    '''
        makeBOW assumes every token in bowTokens is hashable and unique.
    '''
    x = []
    for post in posts:
        tokens = tokenFn(post)
        featureVec = bowFromTokens(tokens, bowTokens)
        x.append(featureVec)
    return x

def filterTokens(tokens, tokenFilterFn=lambda x: True):
    return list(filter(tokenFilterFn, tokens))

def isExcludedWord(word: Word) -> bool:
    return word.exclude == "1"

def makeIsNotExcludedBigram(genderedWords: List[Word]):
    excludedWords = filter(isExcludedWord, genderedWords)
    excludedWords = set([x.word for x in excludedWords])

    def notExcludedBigram(bigram: Tuple[str, str]):
        assert type(bigram) == tuple and len(bigram) == 2, '''expected bigram would be a tuple of length 2, but got a {} 
        of length {}'''.format(type(bigram), len(bigram))
        
        return not (bigram[0] in excludedWords or bigram[1] in excludedWords)
    
    return notExcludedBigram

def makeIsNotExcludedUnigram(genderedWords: List[Word]):
    excludedWords = filter(isExcludedWord, genderedWords)
    excludedWords = set([x.word for x in excludedWords])

    def notExcludedUnigram(unigram: str):
        return not unigram in excludedWords 
    
    return notExcludedUnigram
        

def makeWordGenderer(words: List[Word]):
    maleWords = filter(lambda x: x.female == "0", words)
    maleWords = set([x.word for x in maleWords])

    femaleWords = filter(lambda x: x.female == "1", words)
    femaleWords = set([x.word for x in femaleWords])

    def wordGenderer(word: str) -> Gender:
        if word in maleWords:
            return Gender.MALE
        if word in femaleWords:
            return Gender.FEMALE
        return Gender.NEITHER

    return wordGenderer

def makeBigramGenderer(words: List[Word]):
    '''
        A bigram is coded as MALE or FEMALE if one or both of the words in
        the bigram are coded as MALE or FEMALE. If one of the words is male
        and the other is female, the bigram is coded as NEITHER.
    '''
    wordGenderer = makeWordGenderer(words)

    def bigramGender(bigram) -> Gender:
        g1 = wordGenderer(bigram[0])
        g2 = wordGenderer(bigram[1])
        
        # If one of the words in the bigram isn't gendered choose other gender
        if g1 == Gender.NEITHER:
            return g2
        if g2 == Gender.NEITHER:
            return g1
        
        # If genders aren't the same and both are gendered the gender is
        # inconclusive, so return neither.
        if g1 != g2:
            return Gender.NEITHER

        return g1
        
    return bigramGender

def trainLassoModel(X, Y):
    randomSeed = 104729
    X_train, X_test, y_train, y_test = train_test_split(X, Y,
                                                    train_size=0.9,
                                                    random_state=randomSeed)
    model=LogisticRegressionCV(Cs=20,cv=5,penalty='l1',solver='liblinear',refit=True, n_jobs = -1).fit(X_train,y_train)
    
    coef=model.coef_
    print(coef[0].sum())

    y_predicted = model.predict(X_test)
    auc = roc_auc_score(y_test, y_predicted)
    print(classification_report(y_test, y_predicted))
    # print("AUC: {}".format(auc))
    # print(confusion_matrix(y_test, y_predicted))

    return model

def nMostPredictiveFeaturesFromModel(model, features: List, featureGenderer, n):
    featuresToCoef = {}
    coefs = model.coef_[0]
    for index in range(len(coefs)):
        feature = features[index]
        featuresToCoef[feature] = coefs[index]

    nLargestMaleFeatures = nsmallest(n, featuresToCoef.items(), lambda x: x[1])
    nLargestFemaleFeatures = nlargest(n, featuresToCoef.items(), lambda x: x[1])

    return (nLargestMaleFeatures, nLargestFemaleFeatures)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-gp","--genderedWordsPath", help="Path to file of gendered words in the csv format of Wu's 'vocab10k.csv'.", default="../vocab10K.csv", type=str)
    parser.add_argument("-dp", "--dataPath", help="Path to data file scrapped from a platform.", default="../custom_data/all_tweets.csv", type=str)
    parser.add_argument("-pl","--platform", help='''Platform data is from.
        Must be one of \{'twitter', 'reddit'\}.''', default="twitter", choices=["twitter", "reddit"])
    parser.add_argument("-ng","--ngram", help='''Ngram size.
        Right now, must be one of \{1, 2}.''', default=1, choices=[1, 2], type=int)
    parser.add_argument("-nt","--numTokens", help="Number of most common tokens to use as features.", default=10000, choices=range(10, 200000), type=int)    
    parser.add_argument("-nw","--numWords", help="Number of most coorelated words per gender to examine.", default=10, choices=range(5, 1000), type=int)    
    
    args = parser.parse_args()

    maleWords, femaleWords = getGenderedWords(args.genderedWordsPath)
    allGenderedWords = maleWords + femaleWords

    posts = None
    if args.platform == "twitter": 
        posts = twitter_analysis.allTweetTexts(args.dataPath)
    elif args.platform == "reddit":
        posts = reddit_analysis.getRedditTexts(args.dataPath)
    else:
        raise
    
    features = None
    genderer = None
    exclusionFilter = None
    if args.ngram == 1:
        features = [token for token, count in stats.nMostCommonTokens(posts, args.numTokens, stats.wordsInText)]
        genderer = makeWordGenderer(allGenderedWords)
        exclusionFilter = makeIsNotExcludedUnigram(allGenderedWords)
    elif args.ngram == 2:
        features = [token for token, count in stats.nMostCommonTokens(posts, args.numTokens, stats.bigramsInText)]
        genderer = makeBigramGenderer(allGenderedWords)
        exclusionFilter = makeIsNotExcludedBigram(allGenderedWords)
    else:
        raise
    
    genderedPosts, postGenders = getGenderedPosts(posts, maleWords, femaleWords)
    
    # filtering excluded words from features
    features = filterTokens(features, tokenFilterFn=exclusionFilter)

    x = makeBOW(genderedPosts, features, stats.wordsInText)
    model = trainLassoModel(x, postGenders)
    male, female = nMostPredictiveFeaturesFromModel(model, features, genderer, args.numWords)
    
    print("\nWomen:")
    for word, coef in female:
        print("\tWord: \"{}\" Coef: {}".format(word, coef))
    
    print("\nMen:")
    for word, coef in male:
        print("\tWord: \"{}\" Coef: {}".format(word, coef))

