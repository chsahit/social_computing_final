from heapq import nlargest
from nltk.tokenize import TweetTokenizer
from nltk import ngrams
from typing import Dict, List, Tuple
 
def wordsInText(t: str) -> List[str]:
    tokenizer = TweetTokenizer(preserve_case=False)
    return tokenizer.tokenize(t) 

def bigramsInText(t: str) -> List[Tuple[str, str]]:
    words = wordsInText(t)
    return ngrams(words, 2)

def wordCountInTexts(texts, tokenFn=wordsInText) -> Dict[str, int]:
    wordCount = {}
    for text in texts:
        for word in tokenFn(text):
            if not word in wordCount:
                wordCount[word] = 0
            wordCount[word] += 1
    return wordCount

def nMostCommonTokens(posts, n: int, tokenFn=wordsInText) -> List[Tuple[str, int]]: 
    '''
        tokenFn is a function of the form fun(arg1: T) which returns a list of
            tokens from arg1

        posts is a list of objects of type T coresponding with the expected
            type of tokenFn's arg1

        nMostCommonTokens returns a list of the n most common tokens in posts
    '''
    wordCount = wordCountInTexts(posts, tokenFn)
    return nlargest(n, wordCount.items(), lambda x: x[1])

def writeCounter(outputFile: str, counter: List[Tuple[str, int]]) -> None:
    with open(outputFile, "w") as f:
        f.write("token,count\n")
        for token, count in counter:
            f.write("{},{}\n".format(token, count))