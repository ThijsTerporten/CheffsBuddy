"""
This document will run the app and all of its functionality
"""

import os
from flask import (
    Flask, flash, render_template,
    redirect, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONOGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONOGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get(("SECRET_KEY"))

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_categories")
def get_categories():
    """
    Testing
    """
    categories = list(mongo.db.categories.find())
    return render_template("categories.html", categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
