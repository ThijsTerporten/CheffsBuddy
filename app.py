"""
This document will run the app and all of its functionality
"""

import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get(("SECRET_KEY"))

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_index")
def get_index():
    """
    Function to get the landing page
    """
    return render_template("index.html")


@app.route("/get_categories")
def get_categories():
    """
    Function that gets all categories from mongodb
    """
    categories = list(mongo.db.categories.find())
    return render_template("categories.html", categories=categories)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Function to register to website
    Checks wether the user exists in the database
    If so redirects towards the signup page
    Create object for new user that gets inserted into database
    Create session cookie for user
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Succesfull")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Function for loggin in using existing username
    Check whether username exists in database
    Ensure the hashed password matches user input
    Ensure Username matches user input
    """
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(
                    url_for("my_recipes", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect username and/or password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/my_recipes/<username>", methods=["GET", "POST"])
def my_recipes(username):
    """
    Grab the session username from the database to see users recipes
    """
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("my_recipes.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """
    Logs the user out by removing the cookie
    Redirects to login page
    """
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    """
    Function to add a new recipe
    """
    if not session.get("user"):
        flash("You must be logged in to create a new recipe")
        return redirect(url_for("login"))

    if request.method == "POST":
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "category_name": request.form.get("category_name"),
            "recipe_instructions": request.form.get("recipe_instructions"),
            "created_by": session["user"],
            "ingredients": request.form.get("ingredients"),
            "image_url": request.form.get("image_url")
        }

        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Succesfully created!")
        return redirect(url_for("get_categories"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
