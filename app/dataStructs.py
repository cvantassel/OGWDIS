from app.dbClient import dbClient

class twitterAccountData():

    def __init__(self, dbClient:dbClient):
        self.FollowCount = dbClient.get_follow_count()
        self.UnfollowCount = 0 #TODO
        self.NetFollowCount = abs(self.FollowCount - self.UnfollowCount)
        self.TweetCount = 0 #TODO
        self.AvgFollowRate = 0 #TODO
        self.ChangeFromLifetime = 0 #TODO