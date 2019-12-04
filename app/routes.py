import binascii
import os
import re
import time
import random

from flask import render_template, request, redirect
import hashlib


from app import app
from app.config import config
from app.dbClient import dbClient, twitterAccountData

HANDLE = "@egg620"
EMAIL = "jesse@comcast.com"

tweetWindows = ["hour", "day", "week"]


@app.route('/home', methods = ['POST', 'GET'])
def home():
    if (EMAIL == ""):
        return redirect("/login")
        

    if request.method == 'POST':
        if request.form['posOrNeg'] == 'Positive':
            is_descending = True
        else:
            is_descending = False
        
        client = dbClient(config)
        client.set_handle(HANDLE)

        twitter_account_data = twitterAccountData(client)
        top_five_tweets = client.get_top_five_tweets(descending=is_descending)
        top_five_bad_words = client.get_top_five_bad_words()

        client.close_connection()

        return render_template("home.html",
            Overview=twitter_account_data, tweets=top_five_tweets, phrasesToAvoid=top_five_bad_words, tweetWindows=tweetWindows)
    
    else:
        client = dbClient(config)
        client.set_handle(HANDLE)

        twitter_account_data = twitterAccountData(client)
        top_five_tweets = client.get_top_five_tweets(descending=True)
        top_five_bad_words = client.get_top_five_bad_words()

        client.close_connection()

        return render_template("home.html",
        Overview=twitter_account_data, tweets=top_five_tweets, phrasesToAvoid=top_five_bad_words, tweetWindows=tweetWindows)

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

@app.route('/tweet/<string:tweetID>', methods = ['GET', 'POST'])
def tweet(tweetID:str):

    if request.method == 'POST':

        temp_window = request.form['temp_window']
        client = dbClient(config)
        client.set_handle(HANDLE)

        tweet = client.get_tweet(tweetID)
        client.add_follow_data_to_tweet_with_new_window(tweet, temp_window)

        return render_template("tweet.html", tweet=tweet, timeWindows=tweetWindows)


    else:

        client = dbClient(config)
        client.set_handle(HANDLE)

        tweet = client.get_tweet(tweetID)
        client.add_follow_data_to_tweet(tweet)

        return render_template("tweet.html", tweet=tweet, timeWindows=tweetWindows)

@app.route('/preferences')
def preferences():
    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)

    account = client.get_accounts()
    res = request.args.get('res', " ")


    # request.form['name']
    return render_template("preferences.html", accounts=account, tweetWindows=tweetWindows, res=res)

@app.route('/preferences', methods=['POST'])
def updatepreferences():

    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)

    query = "update ogAccount set defaultAccount = '%s', defaultWindow = '%s' where email = '%s'" % (request.form['account'], request.form['window'], EMAIL)
    client.run_query(query)


    return redirect('/preferences?res=' + 'Done!')


@app.route('/settings')
def settings():

    res = request.args.get('res', " ")
    error = request.args.get('error', " ")
    return render_template("settings.html", error=error, res=res)

@app.route('/settings', methods=['POST'])
def updateSettings():

    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)
    

    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    hashed = (salt + pwdhash).decode('ascii')
    hashed = str(hashed)

    # Check Errors
    if (password != confirmPassword):
        return redirect("/settings?error=" + "Passwords%20Don%27t%20Match")
    if (not re.search("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email)):
        return redirect("/settings?error=" + "Invalid%20Email")
    
    # Run Queries
    if (email != ""):
        query = "update ogAccount set email = '%s' where email = '%s'" % (email, EMAIL)
    if (password != "" & confirmPassword != ""):
        query = "update ogAccount set password = '%s' where email = '%s'" % (hashed, EMAIL)
    if (email != "" & password != "" & confirmPassword != ""):
        query = "update ogAccount set email = '%s', password = '%s' where email = '%s'" % (EMAIL, hashed, EMAIL)

    client.run_query(query)
    return redirect('/settings?res=' + 'Done!')


@app.route('/deleteAcct')
def deleteAcct():
    return render_template("deleteAcct.html")

@app.route('/deleteAcct', methods=['POST'])
def deleteAcctAndRedirectToLogin():
    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)
    
    client.run_query("delete from ogAccount where email = '" + EMAIL +"'")
    return redirect("/login")

@app.route('/')
@app.route('/login')
def login():
    error = request.args.get('error', " ")
    return render_template("login.html", error=error)

@app.route('/', methods=['POST'])
@app.route('/login', methods=['POST'])
def signIntoAccount():
    if request.form['submitType'] == "Create Account":
        return redirect("/signup")
    elif request.form['submitType'] == "Log In":
        # hashing based on code from https://dev.to/brunooliveira/flask-series-part-10-allowing-users-to-register-and-login-1enb
        client = dbClient(config)
        email = request.form['email']
        password = request.form['password']
        checkPassword = client.run_query("select password from ogAccount where email = '" + email + "'")

        stored = checkPassword[0][0]
        salt = stored[:64]
        stored = stored[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512',
                                    password.encode('utf-8'),
                                    salt.encode('ascii'),
                                    100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        pwdhash = str(pwdhash)
        print(stored)
        print(pwdhash)
        if (pwdhash == stored):
            global EMAIL
            global HANDLE
            EMAIL = email
            HANDLE = client.run_query("select defaultAccount from ogAccount where email = '" + EMAIL +"'")
            HANDLE = HANDLE[0][0]
            print(HANDLE)
            return redirect("/home")
        else:
            return redirect("/login?error=" + "Invalid%20Account")


@app.route('/signup')
def signin():
    error = request.args.get('error', " ")
    return render_template("signup.html", error=error)

@app.route('/signup', methods=['POST', 'GET'])
# hashing based on code from https://dev.to/brunooliveira/flask-series-part-10-allowing-users-to-register-and-login-1enb
def signUp():
    client = dbClient(config)
    email = request.form['email']
    password = request.form['password']
    check_pass = request.form['confirmPassword']
    handle = request.form['handle']

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    hashed= (salt + pwdhash).decode('ascii')
    hashed = str(hashed)

    if password == check_pass:
        client.create_twitter_account(handle, email, hashed, email) #TODO: Change with api integration
        query = '''insert into ogAccount values ("{0}", "{1}", "{2}", 'hour');'''.format(email, hashed, handle)
        client.run_insert_query(query)
        return redirect("/login")
    else:
        return redirect("/signup?error=" + "Passwords%20Don%27t%20Match")

@app.route('/fakeFunction')
def fakeFunction():
    return render_template("fakeFunction.html")


@app.route('/fakeFunction', methods=['POST'])
def fakeFunctionHandler():

    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)

    if 'tweet' in request.form:

        def ran_num():
            return random.randint(1,99)
        
        tweet = request.form['tweet']
        currentTime = time.strftime('%Y-%m-%d %H:%M:%S')
        client.run_insert_query("insert into tweet (handle, content, datetime, retweet, favorites, replies) values ('%s', '%s', '%s', %d, %d, %d);" % (HANDLE, tweet, currentTime, ran_num(), ran_num(), ran_num()))

    if 'handle' in request.form:        
        follower_handle = request.form['handle']
        gain_or_loss = request.form['gainOrLoss']
        client.handle_follow_event(follower_handle, gain_or_loss)

    return render_template("fakeFunction.html") 
