import api, image

from flask import Flask, redirect, render_template
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

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

def update_wait_times():
	image.generate_boards(api.get_wait_times())

def update_images():
	image.change_main_board()
	image.change_innoventions_boards()

if  __name__ == "__main__":
	print("STARTING TIPBOARD")
	update_wait_times()
	print("UPDATED WAIT TIMES")
	update_images()
	print("UPDATED IMAGES")
	scheduler.add_job(id = "update wait times", func=update_wait_times, trigger="interval", seconds=60)
	scheduler.add_job(id = "update images", func=update_images, trigger="interval", seconds=7)
	scheduler.start()
	app.run("0.0.0.0", 8081)
