import mysql.connector as conn

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
        return self.run_query(query)[0][0]
    
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


class twitterAccountData():

    def __init__(self, dbClient:dbClient):
        self.FollowCount = dbClient.get_follow_count()
        self.UnfollowCount = 0 #TODO
        self.NetFollowCount = abs(self.FollowCount - self.UnfollowCount)
        self.TweetCount = 0 #TODO
        self.AvgFollowRate = 0 #TODO
        self.ChangeFromLifetime = 0 #TODO

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