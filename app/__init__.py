from flask import Flask
from flask_hashing import Hashing

app = Flask(__name__)
hashing = Hashing(app)

from app import routes
