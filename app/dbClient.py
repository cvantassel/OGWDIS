import mysql.connector as conn
from datetime import datetime, timedelta

'''
# Query to get impact from individual tweets
#SELECT
    (SELECT COUNT(gainOrLoss) FROM followEvent WHERE associatedTweet = '%s' AND gainOrLoss = '1')
  - (SELECT COUNT(gainOrLoss) FROM followEvent WHERE associatedTweet = '%s' AND gainOrLoss = '-1') AS Impact; % (self.tweetID)
'''

class Tweet():

    def __init__(self, id, content = "", time = "", impact = "", favorites="", retweets="", replies="", link=""):
        self.id = id
        self.dateTime = time
        self.content = content
        self.impact = impact
        self.favorites = favorites
        self.retweets = retweets
        self.replies = replies
        self.link = link
        self.follows = []
        self.unfollows = []
    
    def __repr__(self):
        return "ID: " + str(self.id) + "\nTime: " + str(self.dateTime) + "\nBody: " + str(self.content) + "\nImpact: " + str(self.impact) + "\nFavorites: " + str(self.favorites) + "\nRetweets: " + str(self.retweets) + "\nReplies: " + str(self.replies) + "\nLink: " + str(self.link)
    def __str__(self):
        return "ID: " + str(self.id) + "\nTime: " + str(self.dateTime) + "\nBody: " + str(self.content) + "\nImpact: " + str(self.impact) + "\nFavorites: " + str(self.favorites) + "\nRetweets: " + str(self.retweets) + "\nReplies: " + str(self.replies) + "\nLink: " + str(self.link)

class dbClient():
    """https://dev.mysql.com/doc/connector-python/en/connector-python-reference.html"""

    def __init__(self, config:dict):

        self.og_conn = og_conn = conn.connect(**config)
        self.cursor = og_conn.cursor()
    
    def set_handle(self, handle):
        self.handle = handle
    def set_email(self, email):
        self.email = email

    def run_query(self, query):
        try:
            response = self.cursor.execute(query)
        except Exception as ex:
            print("THE FOLLOWING QUERY FAILED:", query)
            print("WITH ERROR", str(ex))
            return ex
        result = []
        for row in self.cursor:
            result.append(row)
        return result

    def run_insert_query(self, query):
        try:
            response = self.cursor.execute(query)
            self.og_conn.commit()
        except Exception as ex:
            print("THE FOLLOWING QUERY FAILED:", query)
            print("WITH ERROR", str(ex))
            return ex
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
            return int(count)
        else:
            return 0

    def add_follow_data_to_tweet(self, tweet:Tweet):
        get_follows_query = """ select associatedFollower from followEvent
	                                inner join tweet on followEvent.associatedTweet = tweet.tweetID
                                    where tweet.handle = '%s' and tweet.tweetID = %d and gainOrLoss > 0;""" % (self.handle, tweet.id)
        
        get_unfollows_query = """ select associatedFollower from followEvent
	                                inner join tweet on followEvent.associatedTweet = tweet.tweetID
                                    where tweet.handle = '%s' and tweet.tweetID = %d and gainOrLoss < 0;""" % (self.handle, tweet.id)

        follows = []
        follow_results = self.run_query(get_follows_query)
        for row in follow_results:
            follows.append(row[0])
        tweet.follows = follows

        unfollows = []
        unfollow_results = self.run_query(get_unfollows_query)
        for row in unfollow_results:
            unfollows.append(row[0])
        tweet.unfollows = unfollows
    
    def get_tweet_window(self)->str:
        query = "select defaultWindow from ogAccount where email = '%s'" % (self.email)
        resp = self.run_query(query)
        return resp[0][0]

    def handle_follow_event(self, follower_handle:str, gain_or_loss:int):
        
        tweet_window = self.get_tweet_window()

        now = datetime.now()

        if tweet_window == 'hour':
            window_begin = now - timedelta(hours=1)
        elif tweet_window == 'day':
            window_begin = now - timedelta(days=1)
        elif tweet_window == 'week':
            window_begin = now - timedelta(weeks=1)
        else:
            raise Exception(tweet_window, "Is not a valid window")

        find_last_associated_tweet_query = """select tweetID, content from tweet
                                                    where handle = '%s'
                                                    and datetime between '%s' and '%s'
                                                    order by datetime desc;""" % (self.handle, window_begin, now)
        
        resp = self.run_query(find_last_associated_tweet_query)

        # Create Follow Event
        if(len(resp) == 0):
            associated_tweet_id = None
            associated_tweet_content = None
        else:
            associated_tweet_id = resp[0][0]
            associated_tweet_content = resp[0][1]


        insert_call = """insert into followEvent (associatedFollower, time, gainOrLoss, associatedTweet, associatedAccount)
                            values (%s, %s, %s, %s, %s)"""
        
        self.cursor.execute(insert_call, (follower_handle, now, gain_or_loss, associated_tweet_id, self.handle))

        # Update Word Bank
        sign = ""
        if (gain_or_loss == "-1"):
            sign = "-"
        else:
            sign = "+"
        
        for word in associated_tweet_content.split(" "):
            # For each word, upsert it and its goodness into the word table 
            query = """INSERT INTO word VALUES (%s, %s) ON DUPLICATE KEY UPDATE goodness = goodness """ + sign + """ 1 ;""" 
            self.cursor.execute(query, (word, gain_or_loss))
            # For each word, add it and its tweetID to the composedOf table
            query = "INSERT INTO composedOf VALUES ('%s', %s)" % (word, associated_tweet_id)
            self.cursor.execute(query)
        
        self.og_conn.commit()



    
    def add_follow_data_to_tweet_with_new_window(self, tweet:Tweet, temp_window:str):

        if temp_window == 'hour':
            window_end = tweet.dateTime + timedelta(hours=1)
        elif temp_window == 'day':
            window_end = tweet.dateTime + timedelta(days=1)
        elif temp_window == 'week':
            window_end = tweet.dateTime + timedelta(weeks=1)
        else:
            return -1

        get_follows_query = """ select associatedFollower from followEvent
                                    where associatedAccount = '%s' and gainOrLoss > 0
                                    and time between '%s' and '%s';""" % (self.handle, tweet.dateTime, window_end)
        
        get_unfollows_query =  """ select associatedFollower from followEvent
                                    where associatedAccount = '%s' and gainOrLoss < 0
                                    and time between '%s' and '%s';""" % (self.handle, tweet.dateTime, window_end)
        
        follows = []
        follow_results = self.run_query(get_follows_query)
        for row in follow_results:
            follows.append(row[0])
        tweet.follows = follows

        unfollows = []
        unfollow_results = self.run_query(get_unfollows_query)
        for row in unfollow_results:
            unfollows.append(row[0])
        tweet.unfollows = unfollows

        tweet.impact = len(follows) - len(unfollows)


        

    def get_tweet(self, tweetID:str)->Tweet:
        query = """select tweet.tweetID, tweet.content,  tweet.datetime, 
                        sum(followEvent.gainOrLoss), tweet.favorites, tweet.retweet, tweet.replies, tweet.link
                        from tweet
                        inner join followEvent on tweet.tweetID = followEvent.associatedTweet
                        where tweet.handle = '%s' and tweet.tweetID = %s
                        group by tweet.tweetID
                        """ % (self.handle, tweetID)

        tweet_data = self.run_query(query)[0]
        
        return Tweet(*tweet_data)
    
    def get_top_five_bad_words(self)->list:
        query = "select phrase from word order by goodness DESC limit 5;"
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
        
        query = """select tweet. tweetID, tweet.content,  tweet.datetime, 
                        sum(followEvent.gainOrLoss), tweet.favorites, tweet.retweet, tweet.replies, tweet.link
                        from tweet
                        inner join followEvent on tweet.tweetID = followEvent.associatedTweet
                        where tweet.handle = '%s'
                        group by tweet.tweetID
                        order by tweet.datetime %s
                        """ % (self.handle, order_by)
        tweet_rows = self.run_query(query)

        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets

    def get_tweets_with_keywords(self, keywords:list)->list:

        query = """select tweet.tweetID, tweet.content,  tweet.datetime, sum(followEvent.gainOrLoss), tweet.favorites, tweet.retweet, tweet.replies, tweet.link from tweet
                inner join followEvent on tweet.tweetID = followEvent.associatedTweet
                where tweet.handle = '%s'""" % (self.handle,)
        
        first_keyword = True

        for keyword in keywords:

            if first_keyword:
                query += "\nAND tweet.content LIKE '%{}%'\n".format(keyword)
                first_keyword = False
            else:
                query += "OR tweet.content LIKE '%{}%'\n".format(keyword)
        
        query += "group by tweet.tweetID;"

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
        query = """select tweetID, date, time, content, favorites, retweet, replies, link from tweet
	                    where handle = '%s' and date between '%s' and '%s';""" % (self.handle, start, end)
        
        tweet_rows = self.run_query(query)
        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets
    
    def get_tweets_between_date_times(self, start, end)->list:
        query = """select tweetID, date, time, content, favorites, retweet, replies, link from tweet
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
        
        query = """select tweet.tweetID, tweet.content,  tweet.datetime, sum(followEvent.gainOrLoss), tweet.favorites, tweet.retweet, tweet.replies, tweet.link from tweet
                        inner join followEvent on tweet.tweetID = followEvent.associatedTweet
                        where tweet.handle = '%s'
                        group by tweet.tweetID
                        order by %s %s""" % (self.handle, x, order_by)
        
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

        query = """select tweet.tweetID, tweet.content,  tweet.datetime, sum(followEvent.gainOrLoss) as impact from tweet
                        inner join followEvent on tweet.tweetID = followEvent.associatedTweet
                        where tweet.handle = '%s'
                        group by tweet.tweetID
                        order by impact %s
                        limit 5;""" % (self.handle, order_by)
        
        tweet_rows = self.run_query(query)

        tweets = []

        for row in tweet_rows:
            tweets.append(Tweet(*row))
        
        return tweets

    def get_accounts(self)->list:
        query = """select handle from twitterAccount where associatedAccount = "%s";""" % (self.email)
        account_rows = self.run_query(query)

        accounts = []

        for row in account_rows:
            accounts.append(row[0])
        
        return accounts


    def close_connection(self):
        self.og_conn.close()
	
    def get_password(self):
        return self.password

    def set_password(self, input_password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(input_password, salt)
        return hashed;

    def check_password(self, input_password):
        return bcrypt.checkpw(self.password, input_password)

	
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
