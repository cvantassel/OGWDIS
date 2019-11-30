import mysql.connector as conn

'''
# Query to get impact from individual tweets
#SELECT
    (SELECT COUNT(gainOrLoss) FROM followEvent WHERE associatedTweet = '%s' AND gainOrLoss = '1')
  - (SELECT COUNT(gainOrLoss) FROM followEvent WHERE associatedTweet = '%s' AND gainOrLoss = '-1') AS Impact; % (self.tweetID)
'''

class Tweet():

    def __init__(self, id, content = "", date = "", time = "", impact = "", favorites="", retweets="", replies="", link=""):
        self.id = id
        self.date = date
        self.dateTime = time
        self.content = content
        self.impact = impact
        self.favorites = favorites
        self.retweets = retweets
        self.replies = replies
        self.link = link

class dbClient():
    """https://dev.mysql.com/doc/connector-python/en/connector-python-reference.html"""

    def __init__(self, config:dict):

        self.og_conn = og_conn = conn.connect(**config)
        self.cursor = og_conn.cursor()
    
    def set_handle(self, handle):
        self.handle = handle

    def run_query(self, query):
        response = self.cursor.execute(query)
        result = []
        for row in self.cursor:
            result.append(row)
        return result


    def run_multi_query(self, queries: list):
    
        result = []
        try:
            responses = self.cursor.execute(query, multi=True)
            self.og_conn.commit()

            for response in responses:
                for record in response:
                    result.append(record)
            
            return str(result)
        except Exception as ex:
            return str(ex)

    def run_get_data_procedure(self, proc_name:str, arguments:list):
        
        result = []
        
        try:
            self.cursor.callproc(proc_name, [username])
            self.og_conn.commit()

            for response in self.cursor.stored_results():
                for record in response.fetchall():
                    result.append(str(record))
            
            return result
        
        except Exception as ex:
            print(ex)
    
    def get_follow_count(self)->int:
        query = "select followers from twitterAccount where handle = '%s';" % (self.handle)
        count = self.run_query(query)[0][0]
        if count is not None:
            return count
        else:
            return 0
    
    def get_unfollow_count(self)->int:
        query = """select SUM(gainOrLoss), associatedAccount from followEvent 
        where gainOrLoss < 0 and associatedAccount = '%s';""" % (self.handle)
        count = self.run_query(query)[0][0]
        if count is not None:
            return count
        else:
            return 0

    def get_tweet(self, tweetID:str)->Tweet:
        query = """select tweetID, date, time, content, retweet, favorites, replies, link from tweet
	                    where handle = '%s';""" % (self.handle)

        tweet_data = self.run_query(query)[0]
        
        return Tweet(*tweet_data)
    
    def get_top_five_bad_words(self)->list:
        query = "select phrase from word order by badness DESC limit 5;"
        bad_words = []
        response = self.run_query(query)
        for row in response:
            bad_words.append(row[0])
        return bad_words

    def get_all_tweets(self, descending = True)->list:
        if(descending):
            order_by = 'DESC'
        else:
            order_by = 'ASC'
        
        query = """select tweet.tweetID, tweet.content, tweet.date, tweet.time, 
                        followEvent.gainOrLoss, tweet.favorites, tweet.retweet, tweet.replies, tweet.link
                        from tweet
                        inner join followEvent on tweet.tweetID
                        where tweet.handle = '%s'
                        order by followEvent.gainOrLoss %s
                        """ % (self.handle, order_by)
        tweet_rows = self.run_query(query)

        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets

    def get_tweets_with_keywords(self, keywords:list)->list:

        query = """select tweet.tweetID, tweet.content, tweet.date, tweet.time, followEvent.gainOrLoss, tweet.retweet, tweet.favorites, tweet.replies, tweet.link from tweet
                inner join followEvent on tweet.tweetID
                where tweet.handle = '%s'""" % (self.handle,)
        
        first_keyword = True

        for keyword in keywords:

            if first_keyword:
                query += "\nAND tweet.content LIKE '%{}%'\n".format(keyword)
                first_keyword = False
            else:
                query += "OR tweet.content LIKE '%{}%'\n".format(keyword)
        
        query += ";"

        tweet_rows = self.run_query(query)

        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets
        
    
    def get_tweet_count(self)->int:
        query = "select COUNT(tweetID) from tweet where handle = '%s'" % (self.handle)
        count = self.run_query(query)[0][0]
        if count is not None:
            return count
        else:
            return 0
    
    def get_tweets_between_dates(self, start, end)->list:
        query = """select tweetID, date, time, content, retweet, favorites, replies, link from tweet
	                    where handle = '%s' and date between '%s' and '%s';""" % (self.handle, start, end)
        
        tweet_rows = self.run_query(query)
        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets
    
    def get_tweets_between_date_times(self, start, end)->list:
        query = """select tweetID, date, time, content, retweet, favorites, replies, link from tweet
	                    where handle = '%s' and time between '%s' and '%s';""" % (self.handle, start, end)
        
        tweet_rows = self.run_query(query)
        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets

    def get_tweets_by_x(self, x:str, descending = True,):

        if(descending):
            order_by = 'DESC'
        else:
            order_by = 'ASC'

        x = x.lower()
        valid_tweet_sorts = ["favorites", "replies"]

        if x == "impact":
            x = "followEvent.gainOrLoss"
        elif x in valid_tweet_sorts:
            x = "tweet." + x
        elif x == "retweets":
            x = "tweet.retweet" #TODO: prolly should just rename this column
        else:
            return -1
        
        query = """select tweet.tweetID, tweet.content, tweet.date, tweet.time, followEvent.gainOrLoss, tweet.retweet, tweet.favorites, tweet.replies, tweet.link from tweet
                        inner join followEvent on tweet.tweetID
                        where tweet.handle = '%s'
                        order by %s %s
                        limit 5;""" % (self.handle, x, order_by)
        
        tweet_rows = self.run_query(query)

        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets
        

    def get_top_five_tweets(self, descending = True)->list:
        if(descending):
            order_by = 'DESC'
        else:
            order_by = 'ASC'

        query = """select tweet.tweetID, tweet.content, tweet.date, tweet.time, followEvent.gainOrLoss from tweet
                        inner join followEvent on tweet.tweetID
                        where tweet.handle = '%s'
                        order by followEvent.gainOrLoss %s
                        limit 5;""" % (self.handle, order_by)
        
        tweet_rows = self.run_query(query)

        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets

    def close_connection(self):
        self.og_conn.close()
'''	
    def lifetime_change(self, start, end) -> int: 
        
        should return lifetime change, just not sure where to get start/end to pass in call below
    	query = """select
                        (select (count(*) from followEvent where associatedAccount = '%s' and gainOrLoss = '1' and (time between '%s' and '%s')
                        - (select (count(*) from followEvent where associatedAccount = '%s' and gainOrLoss = '1' and (time between '%s' and '%s'))
                        / (select followers from twitterAccount where handle = '%s') * 100;""" (self.handle, start, end, self.handle, start, end, self.handle)

        rate = self.run_query(query)

        return rate
        '''

class twitterAccountData():

    def __init__(self, dbClient:dbClient):
        self.FollowCount = dbClient.get_follow_count()
        self.UnfollowCount = dbClient.get_unfollow_count()
        self.NetFollowCount = abs(self.FollowCount - self.UnfollowCount)
        self.TweetCount = dbClient.get_tweet_count()
        self.AvgFollowRate = 0 #TODO
        self.ChangeFromLifetime = 0 #TODO query/function is written, just need to call (pass start/end times)
