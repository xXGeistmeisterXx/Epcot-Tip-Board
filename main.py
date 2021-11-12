import api, image

from flask import Flask, request, redirect, url_for, render_template
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_statistics import Statistics

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/stats.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
scheduler = APScheduler()

class Request(db.Model):
    __tablename__ = "request"

    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    response_time = db.Column(db.Float)
    date = db.Column(db.DateTime)
    method = db.Column(db.String)
    size = db.Column(db.Integer)
    status_code = db.Column(db.Integer)
    path = db.Column(db.String)
    user_agent = db.Column(db.String)
    remote_address = db.Column(db.String)
    exception = db.Column(db.String)
    referrer = db.Column(db.String)
    browser = db.Column(db.String)
    platform = db.Column(db.String)
    mimetype = db.Column(db.String)

db.create_all()

def check():
	if request.remote_addr != "127.0.0.1":
		return redirect(url_for("index"))

statistics = Statistics(app, db, Request, check)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/main-board")
def main():
    return render_template("tipboard.html", name="Main", board_image="main-board.png")

@app.route("/west-board")
def west():
    return render_template("tipboard.html", name="Innoventions West", board_image="west-board.png")

@app.route("/east-board")
def east():
    return render_template("tipboard.html", name="Innoventions East", board_image="east-board.png")

@app.route("/times")
def times():
	return redirect("static/times.txt")

def updateData():
	api.updateAttractions()

def updateImages():
	image.changeMainBoard()
	image.changeInnoventionsBoards()

if  __name__ == "__main__":
	updateData()
	updateImages()
	scheduler.add_job(id = 'Update Data', func=updateData, trigger="interval", seconds=60)
	scheduler.add_job(id = 'Update Images', func=updateImages, trigger="interval", seconds=7)
	scheduler.start()
	app.run("0.0.0.0", 8082)
