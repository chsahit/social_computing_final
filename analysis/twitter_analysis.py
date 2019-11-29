import tweet
import stats
from typing import List, Tuple

def allTweetTexts(pathToTwitterData: str) -> List[str]:
    return [x.text for x in tweetsFromFile(pathToTwitterData)]

def tweetsFromFile(pathToTwitterData: str) -> List[tweet.Tweet]:
    tweets = []
    with open(pathToTwitterData, "r") as f:
        # Reading past header of .csv file
        f.readline()
        for line in f:
            line = line.strip()
            t = tweet.TweetFactory.getTweet(line)
            tweets.append(t)
    return tweets

def hashtagsInTweet(t: tweet.Tweet) -> List[str]:
    tags = []
    for tag in t.hashtags.strip().split():
        tags.append(tag.lower())
    return tags

def nMostCommonHashtags(pathToTwitterData: str, n: int) -> List[Tuple[str, int]]:
    tweets = tweetsFromFile(pathToTwitterData)
    return stats.nMostCommonTokens(tweets, n, hashtagsInTweet)

def nMostCommonBigrams(pathToTwitterData: str, n: int):
    tweetTexts = allTweetTexts(pathToTwitterData)
    return stats.nMostCommonTokens(tweetTexts, n, stats.bigramsInText)

def nMostCommonWords(pathToTwitterData: str, n: int):
    tweetTexts = allTweetTexts(pathToTwitterData)
    return stats.nMostCommonTokens(tweetTexts, n)
