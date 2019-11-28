from app import app
import mysql.connector as conn
from app.config import config
from app.dbClient import dbClient, twitterAccountData, Tweet
from flask import render_template


@app.route('/')
@app.route('/home')
def home():

    client = dbClient(config)
    client.set_handle("@applejuice")

    twitter_account_data = twitterAccountData(client)
    top_five_tweets = client.get_top_five_tweets(descending=True)
    top_five_bad_words = client.get_top_five_bad_words()

    client.close_connection()

    return render_template("home.html",
     Overview=twitter_account_data, tweets=top_five_tweets, phrasesToAvoid=top_five_bad_words)
