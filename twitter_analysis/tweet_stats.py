from tweet import TweetFactory, Tweet
from heapq import nlargest

def wordsInTweet(t: Tweet):
    words = []
    for word in t.text.strip().split():
        words.append(word.lower())
    return words

def wordCountInTweets(tweets):
    wordCount = {}
    for tweet in tweets:
        for word in wordsInTweet(tweet):
            if not word in wordCount:
                wordCount[word] = 0
            wordCount[word] += 1
    return wordCount

def tweetsFromFile(fileName):
    tweets = []
    with open(fileName, "r") as f:
        # Reading past header of .csv file
        f.readline()
        for line in f:
            line = line.strip()
            tweet = TweetFactory.getTweet(line)
            tweets.append(tweet)
    return tweets

def nMostCommonWords(fileName: str, n: int):
    tweets = tweetsFromFile(fileName)
    wordCount = wordCountInTweets(tweets)
    return nlargest(n, wordCount.items(), lambda x: x[1])

if __name__ == "__main__":
    # TODO(jtaylor351): Get tweet file name from stdin.
    tweetFileName = "../custom_data/all_tweets.csv"
    outputFileName = "most_common_words.csv"
    n = 10000
    topWords = nMostCommonWords(tweetFileName, n)
    with open(outputFileName, "w") as f:
        f.write("word,count\n")
        for word, count in topWords:
            f.write("{},{}\n".format(word, count))

