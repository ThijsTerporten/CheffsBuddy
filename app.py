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
    recipes = list(mongo.db.recipes.find())
    return render_template(
                            "categories.html",
                            categories=categories,
                            recipes=recipes)


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
        return redirect(url_for("get_categories"))

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
    username = session["user"]
    if username == session["user"]:
        recipes = list(mongo.db.recipes.find(
            {"created_by": session["user"]}))
    else:
        flash("You weren't supposed to be here!")
        return redirect(url_for("get_categories"))
    return render_template(
        "my_recipes.html",
        username=username,
        recipes=recipes)


@app.route("/full_recipe/<recipe_id>")
def full_recipe(recipe_id):
    """
    Shows the full recipe from the database
    """
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    try:
        category_name = mongo.db.categories.find_one(
            {"_id": ObjectId(recipe["category_id"])})["category_name"]
        recipe["category_id"] = category_name
    except BaseException:
        recipe["category_id"] = "undefined"
    return render_template("full_recipe.html", recipe=recipe)


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
            "recipe_instructions": request.form.getlist("recipe_instructions"),
            "created_by": session["user"],
            "ingredients": request.form.getlist("ingredients"),
            "image_url": request.form.get("image_url"),
            "description": request.form.get("description")
        }

        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Succesfully created!")
        return redirect(url_for("get_categories"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route("/edit_recipes/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    """
    Allows user to edit their created recipe
    """
    if "user" in session:
        user = session["user"]
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if recipe["created_by"]:
            if recipe["created_by"] == user:
                if request.method == "POST":
                    update = {
                        "recipe_name": request.form.get("recipe_name"),
                        "category_name": request.form.get("category_name"),
                        "recipe_instructions": request.form.getlist(
                            "recipe_instructions"),
                        "created_by": session["user"],
                        "ingredients": request.form.getlist("ingredients"),
                        "image_url": request.form.get("image_url"),
                        "description": request.form.get("description")
                    }
                    mongo.db.recipes.update(
                        {"_id": ObjectId(recipe_id)}, update)
                    flash("Recipe Succesfully Updated")
                    return redirect(url_for("get_categories"))
            else:
                flash("Whoops you are not this recipes creator")
                return redirect(url_for("get_categories"))

        categories = mongo.db.categories.find().sort("category_name", 1)
        return render_template(
            "edit_recipe.html", recipe=recipe, categories=categories)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    """
    Remove a recipe from the database
    """
    if "user" in session:
        user = session["user"]
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if recipe["created_by"]:
            if recipe["created_by"] == user:
                mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
                flash("Recipe Succesfully Removed")
                return redirect(url_for("get_categories"))
        else:
            flash("You didnt create this recipe!")
            return redirect(url_for("categories.html"))


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Function to search for recipes in the database
    """
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("categories.html", recipes=recipes)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
