from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
from os import path
import os
import sqlite3
from functools import wraps
from textblob import TextBlob
from datetime import timedelta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///feedbacks.db"
app.config["SECRET_KEY"] = "some_secret_key"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
db = SQLAlchemy(app)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    sentiment = db.Column(db.String(50), nullable=True)
    initiative_id = db.Column(db.Integer, db.ForeignKey("initiative.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    initiative = db.relationship("Initiative", back_populates="feedbacks")


class Initiative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


class User(db.Model):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    feedbacks = db.relationship("Feedback", backref="user", lazy=True)


def wordcloud(initiative_id):
    sql_query = "SELECT content FROM feedback WHERE initiative_id=" + str(initiative_id)
    cnx = sqlite3.connect('instance/feedbacks.db')
    df = pd.read_sql_query(sql_query, cnx)
 
    comment_words = ''
    stopwords = set(STOPWORDS)
    
    # iterate through the csv file
    for val in df.content:
        
        # typecaste each val to string
        val = str(val)
    
        # split the value
        tokens = val.split()
        
        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
        
        comment_words += " ".join(tokens)+" "
    
    wordcloud = WordCloud(width = 800, height = 800,
                    background_color ='white',
                    stopwords = stopwords,
                    min_font_size = 10).generate(comment_words)
    
    wordcloud.to_file('static/images/' + str(initiative_id) + '.jpg')


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["logged_in"] = True
            session["username"] = user.username
            session["role"] = user.role
            session["user_id"] = user.id  # Storing the user's ID in the session
            return redirect(url_for("index"))
        else:
            error = "Invalid credentials. Please try again."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    initiatives = Initiative.query.all()
    return render_template("index.html", initiatives=initiatives)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/add_initiative", methods=["GET", "POST"])
def add_initiative():
    if request.method == "POST":
        name = request.form.get("name")
        new_initiative = Initiative(name=name)
        db.session.add(new_initiative)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add_initiative.html")


@app.route("/submit_feedback/<int:initiative_id>", methods=["POST"])
@login_required
def submit_feedback(initiative_id):
    content = request.form.get("content")

    # Analyze the sentiment using TextBlob
    analysis = TextBlob(content)
    if analysis.sentiment.polarity > 0:
        sentiment = "positive"
    elif analysis.sentiment.polarity == 0:
        sentiment = "neutral"
    else:
        sentiment = "negative"

    new_feedback = Feedback(
        sentiment=sentiment,
        content=content,
        initiative_id=initiative_id,
        user_id=session["user_id"],
    )    
    
    db.session.add(new_feedback)
    db.session.commit()

    wordcloud(initiative_id)
    flash("Feedback submitted successfully!", "success")
    return redirect(url_for("feedback_page", initiative_id=initiative_id))


@app.route("/initiative/<int:initiative_id>")
@login_required
def feedback_page(initiative_id):
    initiative = Initiative.query.get_or_404(initiative_id)
    feedbacks = Feedback.query.filter_by(initiative_id=initiative.id).all()
    return render_template(
        "feedback_page.html",
        feedbacks=feedbacks,
        initiative=initiative,
        user_role=session["role"],
    )


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()  # remember to remove when prod
        db.create_all()
        if not User.query.filter_by(
            username="hr"
        ).first():  # if username="hr" not present means fresh db
            hr = User(username="hr", password="123456", role="HR")
            employee = User(username="employee", password="123456", role="Employee")
            db.session.add(hr)
            db.session.add(employee)
            db.session.commit()
    app.run(debug=True)
