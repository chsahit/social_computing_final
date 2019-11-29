from datetime import datetime

class TweetFactory:
    @classmethod
    def getTweet(cls, tweetText):
        startContent = tweetText.find('"')
        endContent = tweetText.rfind('",')
        begining = tweetText[:startContent - 1].split(",")
        content = tweetText[startContent + 1:endContent]
        end = tweetText[endContent + 2:].split(",")
        return Tweet(*begining, content, *end)
class Tweet:
    def __init__(self, date, username, to, replies
        ,retweets, favorites, text, geo, mentions
        ,hashtags, tweetId, permalink):
        self.date = date
        self.username = username
        self.to = to
        self.replies = replies
        self.retweets = retweets
        self.favorites = favorites
        self.text = text
        self.geo = geo
        self.mentions = mentions
        self.hashtags = hashtags
        self.id = tweetId
        self.permalink = permalink
    
    def getDate(self) -> datetime:
        return datetime.fromisoformat(self.date)
    
    def __lt__(self, other):
        return self.getDate() < other.getDate()
    
    def __eq__(self, other):
        if not isinstance(other, Tweet):
            return False
        return self.getDate() == other.getDate()
    
    def __ne__(self, other):
        return not self.__eq__(other)