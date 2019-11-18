from app import app
import mysql.connector as conn
from app.config import config


@app.route('/')
@app.route('/index')
def index():

    og_conn = conn.connect(**config)

    cursor = og_conn.cursor()
    
    # cursor.execute("insert into test values('testval2');")
    # og_conn.commit()

    cursor.execute("SELECT * FROM test;")
    
    result = ""

    for element in cursor:
        result += element[0]

    og_conn.close()

    return result
