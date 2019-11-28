from app import app
import mysql.connector as conn
from app.config import config
from app.dbClient import dbClient, twitterAccountData, Tweet
from flask import render_template

HANDLE = "@applejuice"

@app.route('/')
@app.route('/home')
def home():

    client = dbClient(config)
    client.set_handle(HANDLE)

    twitter_account_data = twitterAccountData(client)
    top_five_tweets = client.get_top_five_tweets(descending=True)
    top_five_bad_words = client.get_top_five_bad_words()

    client.close_connection()

    return render_template("home.html",
     Overview=twitter_account_data, tweets=top_five_tweets, phrasesToAvoid=top_five_bad_words)

@app.route('/history')
def history():
    client = dbClient(config)
    client.set_handle(HANDLE)

    
    all_tweets = client.get_all_tweets(descending=True)
    
    client.close_connection()

    return render_template("history.html", tweets=all_tweets)

@app.route('/tweet/<string:tweetID>')
def tweet(tweetID:str):

    client = dbClient(config)
    client.set_handle(HANDLE)

    tweet = client.get_tweet(tweetID)

    return render_template("tweet.html", tweet=tweet)



