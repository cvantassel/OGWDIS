import unittest 
from dbClient import *
import mysql.connector as conn
from config import config
  
class TestDbClient(unittest.TestCase):

    def setUp(self):
        set_up_queries = [
            "INSERT INTO ogAccount VALUES ('tester@gmail.com', 'password1!', '@test_handle', 'hour');",
            "INSERT INTO twitterAccount VALUES('@test_handle', 'tester@gmail.com', 'password1!', '2019-08-29 12:00:0', 'tester@gmail.com', 100);",

            "INSERT INTO tweet VALUES (99990, '@test_handle', '2019-09-01 09:00:0', 'positive tweet yay', 1, 1, 1, 'https://twitter.com/i/web/status/1128357932238823424');",
            "INSERT INTO followEvent VALUES (88880, '@user0', '2019-09-01 09:15:00', 1, 99990, '@test_handle');",

            "INSERT INTO tweet VALUES (99991, '@test_handle', '2019-09-01 10:00:0', 'negative tweet boo', 2, 2, 2, 'https://twitter.com/i/web/status/1128357932238823425');",
            "INSERT INTO followEvent VALUES (88881, '@user1', '2019-09-01 10:15:00', -1, 99991, '@test_handle');",

            "INSERT INTO tweet VALUES (99992, '@test_handle', '2019-09-02 11:00:0', 'very positive tweet yay', 3, 3, 3, 'https://twitter.com/i/web/status/1128357932238823425');",
            "INSERT INTO followEvent VALUES (88882, '@user2', '2019-09-02 11:15:00', 1, 99992, '@test_handle');",
            "INSERT INTO followEvent VALUES (88883, '@user3', '2019-09-02 11:16:00', 1, 99992, '@test_handle');",

            
            "INSERT INTO tweet VALUES (99993, '@test_handle', '2019-09-02 13:30:0', 'very negative tweet boo', 4, 4, 4, 'https://twitter.com/i/web/status/1128357932238823425');",
            "INSERT INTO followEvent VALUES (88884, '@user4', '2019-09-02 13:45:00', -1, 99993, '@test_handle');",
            "INSERT INTO followEvent VALUES (88885, '@user5', '2019-09-02 13:46:00', -1, 99993, '@test_handle');",

            "INSERT INTO tweet VALUES (99994, '@test_handle', '2019-09-02 14:0:0', 'super duper negative tweet boo', 5, 5, 5, 'https://twitter.com/i/web/status/1128357932238823425');",
            "INSERT INTO followEvent VALUES (88886, '@user6', '2019-09-02 14:15:00', -1, 99994, '@test_handle');",
            "INSERT INTO followEvent VALUES (88887, '@user7', '2019-09-02 14:16:00', -1, 99994, '@test_handle');",
            "INSERT INTO followEvent VALUES (88888, '@user8', '2019-09-02 14:17:00', -1, 99994, '@test_handle');",

            "INSERT INTO tweet VALUES (99995, '@test_handle', '2019-09-02 15:30:0', 'super duper positive tweet yay', 6, 6, 6, 'https://twitter.com/i/web/status/1128357932238823425');",
            "INSERT INTO followEvent VALUES (88889, '@user9', '2019-09-02 15:45:00', 1, 99995, '@test_handle');",
            "INSERT INTO followEvent VALUES (88890, '@user10','2019-09-02 15:46:00', 1, 99995, '@test_handle');",
            "INSERT INTO followEvent VALUES (88891, '@user11','2019-09-02 15:47:00', 1, 99995, '@test_handle');",
        ]

        self.client = dbClient(config)
        self.client.set_handle("@test_handle")
        self.client.set_email("tester@gmail.com")

        for query in set_up_queries:
            self.client.run_query(query)
    
    def tearDown(self):
        tear_down_queries = [
            "delete from ogAccount where email='tester@gmail.com';",
            "delete from twitterAccount where handle='@test_handle';",
            "delete from tweet where handle='@test_handle';",
            "delete from followEvent where associatedAccount='@test_handle';",
        ]

        for query in tear_down_queries:
            self.client.run_query(query)
        
        self.client.close_connection()

    def test_get_top_five_tweets_desc(self):

        top_five_tweets = self.client.get_top_five_tweets(descending=True)

        self.assertEqual(len(top_five_tweets), 5)

        descending_by_impact = sorted(top_five_tweets, reverse=True, key=lambda tweet: tweet.impact)
        self.assertEqual(top_five_tweets, descending_by_impact)

        best_tweet = 99995
        self.assertEqual(top_five_tweets[0].id, best_tweet)
    
    def test_get_top_five_tweets_asc(self):

        top_five_tweets = self.client.get_top_five_tweets(descending=False)

        self.assertEqual(len(top_five_tweets), 5)

        ascending_by_impact = sorted(top_five_tweets, key=lambda tweet: tweet.impact)
        self.assertEqual(top_five_tweets, ascending_by_impact)

        worst_tweet = 99994
        self.assertEqual(top_five_tweets[0].id, worst_tweet)
    
    def test_get_all_tweets(self):

        all_tweets = self.client.get_all_tweets(descending=True)
        
        self.assertEqual(len(all_tweets), 6)

        most_recent_tweet = 99995
        self.assertEqual(all_tweets[0].id, most_recent_tweet)
    
    def test_get_follow_count(self):

        follow_count = self.client.get_follow_count()

        self.assertEqual(follow_count, 100)
    
    def test_get_unfollow_count(self):

        unfollow_count = self.client.get_unfollow_count()

        self.assertEqual(unfollow_count, -6)
    
    def test_keyword_search(self):

        keywords = ['positive']
        search_results = self.client.get_tweets_with_keywords(keywords)

        self.assertEqual(len(search_results), 3)

        for tweet in search_results:
            self.assertIn('positive', tweet.content)
    
    def test_multi_keyword_search(self):

        keywords = ['positive', 'super']
        search_results = self.client.get_tweets_with_keywords(keywords)

        self.assertEqual(len(search_results), 4)

        for tweet in search_results:
            self.assertTrue(('positive' in tweet.content) or ('super' in tweet.content))
    
    def test_get_tweets_by_favorites(self):

        results = self.client.get_tweets_by_x("favorites", descending=True)

        self.assertEqual(len(results), 6)

        descending_by_fav = sorted(results, reverse=True, key=lambda tweet: tweet.favorites)
        self.assertEqual(results, descending_by_fav)

        highest_value = 6
        self.assertEqual(results[0].favorites, highest_value)

    def test_get_tweets_by_retweets(self):

        results = self.client.get_tweets_by_x("retweets", descending=True)

        self.assertEqual(len(results), 6)

        descending_by_rt = sorted(results, reverse=True, key=lambda tweet: tweet.retweets)
        self.assertEqual(results, descending_by_rt)

        highest_value = 6
        self.assertEqual(results[0].retweets, highest_value)
    
    def test_get_tweets_by_replies(self):

        results = self.client.get_tweets_by_x("replies", descending=True)

        self.assertEqual(len(results), 6)

        descending_by_replies = sorted(results, reverse=True, key=lambda tweet: tweet.replies)
        self.assertEqual(results, descending_by_replies)

        highest_value = 6
        self.assertEqual(results[0].replies, highest_value)
    
    def test_follower_data_with_temp_window_hour(self):

        tweet = self.client.get_tweet('99990')
        self.client.add_follow_data_to_tweet_with_new_window(tweet, 'hour')

        new_followers = ['@user0']
        new_unfollowers = []

        self.assertEqual(tweet.follows, new_followers)
        self.assertEqual(tweet.unfollows, new_unfollowers)

    def test_follower_data_with_temp_window_day(self):

        tweet = self.client.get_tweet('99990')
        self.client.add_follow_data_to_tweet_with_new_window(tweet, 'day')

        new_followers = ['@user0']
        new_unfollowers = ['@user1']

        self.assertEqual(tweet.follows, new_followers)
        self.assertEqual(tweet.unfollows, new_unfollowers)
    
    def test_handle_follow_event_hour(self):

        query = "INSERT INTO tweet VALUES (99996, '@test_handle', '%s', 'brand spanking new tweet', 7, 7, 7, 'https://twitter.com/i/web/status/1128357932238823425');" % (datetime.now() - timedelta(minutes=1))
        self.client.run_query(query)

        self.client.handle_follow_event("@user12", 1)
        self.client.handle_follow_event("@user13", -1)

        get_follow_events_query = "select associatedFollower, associatedTweet, associatedAccount from followEvent where associatedTweet=99996"
        rows = self.client.run_query(get_follow_events_query)

        self.assertEqual(len(rows), 2)
    
    def test_get_avg_follow_rate(self):

        query = "INSERT INTO followEvent VALUES (88892, '@user12','2019-09-02 15:47:00', 1, 99995, '@test_handle');"
        self.client.run_query(query)

        rate = self.client.lifetime_change()
        self.assertEqual(rate, 1/13)
    


        







        
  
if __name__ == '__main__': 
    unittest.main() 