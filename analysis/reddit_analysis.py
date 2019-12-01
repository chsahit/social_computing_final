import pandas as pd
import stats

def getRedditTexts(pathToRedditData: str):
    data = pd.read_csv(pathToRedditData)
    posts = []
    for i in range(len(data)):
        posts.append(' '.join(
          [
            str(data["text"][i]),
            str(data["comment1"][i]),
            str(data["comment2"][i]),
            str(data["comment3"][i])
          ]
        ).lower())
    return posts 

def nMostCommonBigrams(pathToRedditData: str, n: int):
    redditTexts = getRedditTexts(pathToRedditData)
    return stats.nMostCommonTokens(redditTexts, n, stats.bigramsInText)

def nMostCommonWords(pathToRedditData: str, n: int):
    redditTexts = getRedditTexts(pathToRedditData)
    return stats.nMostCommonTokens(redditTexts, n)