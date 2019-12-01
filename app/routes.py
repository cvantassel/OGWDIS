from app import app
import mysql.connector as conn
from app.config import config
from app.dbClient import dbClient, twitterAccountData, Tweet
from flask import render_template, request, redirect
import re

HANDLE = ""
EMAIL = ""

tweetWindows = ["hour", "day", "week"]


@app.route('/home', methods = ['POST', 'GET'])
def home():
    if (EMAIL == ""):
        return redirect("/login")
        

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

@app.route('/tweet/<string:tweetID>')
def tweet(tweetID:str):

    client = dbClient(config)
    client.set_handle(HANDLE)

    tweet = client.get_tweet(tweetID)

    return render_template("tweet.html", tweet=tweet)

@app.route('/settings')
def settings():
    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)

    account = client.get_accounts()
    res = request.args.get('res', " ")


    # request.form['name']
    return render_template("settings.html", accounts=account, tweetWindows=tweetWindows, res=res)

@app.route('/settings', methods=['POST'])
def updateSettings():

    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)

    query = "update ogAccount set defaultAccount = '%s', defaultWindow = '%s' where email = '%s'" % (request.form['account'], request.form['window'], EMAIL)
    client.run_query(query)


    return redirect('/settings?res=' + 'Done!')


@app.route('/preferences')
def preferences():

    res = request.args.get('res', " ")
    error = request.args.get('error', " ")
    return render_template("preferences.html", error=error, res=res)

@app.route('/preferences', methods=['POST'])
def updatePreferences():

    client = dbClient(config)
    client.set_handle(HANDLE)
    client.set_email(EMAIL)
    

    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']


    # Check Errors
    if (password != confirmPassword):
        return redirect("/preferences?error=" + "Passwords%20Don%27t%20Match")
    if (not re.search("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email)):
        return redirect("/preferences?error=" + "Invalid%20Email")
    
    # Run Queries
    if (email != ""):
        query = "update ogAccount set email = '%s' where email = '%s'" % (email, EMAIL)
    if (password != "" & confirmPassword != ""):
        query = "update ogAccount set password = '%s' where email = '%s'" % (PASSWORD, EMAIL)
    if (email != "" & password != "" & confirmPassword != ""):
        query = "update ogAccount set email = '%s', password = '%s' where email = '%s'" % (EMAIL, PASSWORD, EMAIL)

    client.run_query(query)
    return redirect('/preferences?res=' + 'Done!')


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

@app.route('/login', methods=['POST'])
def signIntoAccount():
    client = dbClient(config)
    email = request.form['email']
    password = request.form['password']

    checkPassword = client.run_query("select password from ogAccount where email = '" + email +"'")
    print(checkPassword)
    if (checkPassword != []):
        if (password == checkPassword[0][0]):
            global EMAIL
            global HANDLE
            EMAIL = email
            HANDLE = client.run_query("select defaultAccount from ogAccount where email = '" + EMAIL +"'")
            HANDLE = HANDLE[0][0]
            return redirect("/home")
    else:
        return redirect("/login?error=" + "Invalid%20Account")