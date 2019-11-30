from app import app
import mysql.connector as conn
from app.config import config
from app.dbClient import dbClient, twitterAccountData, Tweet
from flask import render_template, request

HANDLE = "@egg620"

@app.route('/')
@app.route('/home', methods = ['POST', 'GET'])
def home():

    if request.method == 'POST':
        if request.form['posOrNeg'] == 'Positive':
            is_descending = False
        else:
            is_descending = True
        
        client = dbClient(config)
        client.set_handle(HANDLE)

        twitter_account_data = twitterAccountData(client)
        top_five_tweets = client.get_top_five_tweets(descending=is_descending)
        top_five_bad_words = client.get_top_five_bad_words()

        client.close_connection()

        return render_template("home.html",
            Overview=twitter_account_data, tweets=top_five_tweets, phrasesToAvoid=top_five_bad_words)
    
    else:
        client = dbClient(config)
        client.set_handle(HANDLE)

        twitter_account_data = twitterAccountData(client)
        top_five_tweets = client.get_top_five_tweets(descending=True)
        top_five_bad_words = client.get_top_five_bad_words()

        client.close_connection()

        return render_template("home.html",
        Overview=twitter_account_data, tweets=top_five_tweets, phrasesToAvoid=top_five_bad_words)

@app.route('/history', methods = ['POST', 'GET'])
def history():

    if request.method == 'POST':
        if request.form.get('ascending'):
            is_descending = False
        else:
            is_descending = True
        
        client = dbClient(config)
        client.set_handle(HANDLE)

        
        all_tweets = client.get_tweets_by_x(request.form['sortBy'], is_descending)
        
        client.close_connection()

        return render_template("history.html", tweets=all_tweets)
    else:

        client = dbClient(config)
        client.set_handle(HANDLE)

        
        all_tweets = client.get_all_tweets(descending=True)
        
        client.close_connection()

        return render_template("history.html", tweets=all_tweets)

@app.route('/history-search', methods = ['POST'])
def history_search():

    if request.method == 'POST':
        
        keyword_text = request.form['keywords']
        keywords = [word.strip() for word in keyword_text.split(",")]

        client = dbClient(config)
        client.set_handle(HANDLE)

        
        all_tweets = client.get_tweets_with_keywords(keywords)
        
        client.close_connection()

        return render_template("history.html", tweets=all_tweets)

@app.route('/tweet/<string:tweetID>')
def tweet(tweetID:str):

    client = dbClient(config)
    client.set_handle(HANDLE)

    tweet = client.get_tweet(tweetID)

    return render_template("tweet.html", tweet=tweet)



