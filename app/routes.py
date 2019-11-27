from app import app
import mysql.connector as conn
from app.config import config
from app.dbClient import dbClient
from flask import render_template
from app.dataStructs import twitterAccountData


@app.route('/')
@app.route('/home')
def home():

    client = dbClient(config)
    client.set_handle("@applejuice")

    twitter_account_data = twitterAccountData(client)

    return render_template("home.html", Overview=twitter_account_data)
