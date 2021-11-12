from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import math
import os

mainBoardData = {}
innoventionsBoardsData = {}

def getOutput(attraction):
	result = f'{ attraction["waitTime"] } min'
	if not attraction["isAttraction"]:
		result = "Open"
	elif attraction["waitTime"] == 0:
		result = "No wait"
	if attraction["isDown"]:
		result = "Down"
	if not attraction["isOpen"]:
		result = "Closed"
	return result

def generateBoards(formattedAttractions):
	generateMainBoard(formattedAttractions)
	generateInnoventionsBoards(formattedAttractions)

def generateMainBoard(formattedAttractions):
	global mainBoardData
	mainBoardData = {}

	pageLength = 7

	mainBoardData["pages"] = math.ceil(len(formattedAttractions) / pageLength)
	mainBoardData["position"] = 0

	intialHeight = 90
	spacing = 100
	green = (19, 191, 45)

	for page in range(mainBoardData["pages"]):

		img = Image.open("images/templates/main-board.png")
		fnt = ImageFont.truetype('fonts/font.otf', 90)
		d = ImageDraw.Draw(img)

		startingIndex = page * pageLength
		pageAttractions = formattedAttractions[startingIndex:startingIndex + pageLength]
		for attraction in pageAttractions:
			height = intialHeight + pageAttractions.index(attraction) * spacing

			d.text((90, height), attraction["name"], font=fnt, fill=(255, 255, 255))
			d.text((1750, height), getOutput(attraction), font=fnt, fill=green)

			img.save(f"images/main-board/{ page }.png")

def generateInnoventionsBoards(formattedAttractions):
	global innoventionsBoardsData
	innoventionsBoardsData = {}

	pageLength = 2
	innoventionsBoardsData["pages"] = math.ceil(len(formattedAttractions) / pageLength)
	innoventionsBoardsData["position"] = -1


	for page in range(innoventionsBoardsData["pages"]):
		startingIndex = page * pageLength
		generateInnoventionsPage("images/templates/east-board.png", f"images/east-board/{ page }.png", formattedAttractions[startingIndex:startingIndex + pageLength])
		generateInnoventionsPage("images/templates/west-board.png", f"images/west-board/{ page }.png", formattedAttractions[startingIndex:startingIndex + pageLength])

	time = datetime.now()
	generateWelcomeBoard("images/templates/east-board.png", "images/east-board/-1.png", time)
	generateWelcomeBoard("images/templates/west-board.png", "images/west-board/-1.png", time)

def generateInnoventionsPage(inputImage, outputImage, attractions):

	intialHeight = 175
	spacing = 100
	intialWidth = 90
	yellow = (214, 187, 54)
	green = (19, 191, 45)
	red = (184, 31, 31)

	img = Image.open(inputImage)
	fnt = ImageFont.truetype('fonts/font.otf', 115)
	d = ImageDraw.Draw(img)

	for attraction in attractions:
		height = intialHeight + attractions.index(attraction) * 492

		d.text((intialWidth, height), attraction["name"], font=fnt, fill=(255, 255, 255))

		if(attraction["isOpen"]):
			d.text((intialWidth + 60, height + 110), "Stand-by", font=fnt, fill=yellow)
			d.text((1500, height + 110), getOutput(attraction), font=fnt, fill=green)
		else:
			d.text((intialWidth + 60, height + 110), "Closed", font=fnt, fill=yellow)

		if attraction["hasLL"]:

			if not attraction["LLActive"]:

				if attraction["isOpen"]:
					d.text((intialWidth + 60, height + 110 + 110), "Lightning Lane all distributed", font=fnt, fill=red)

				elif "LLTimeStart" in attraction:
					d.text((intialWidth + 60, height + 110 + 110), f"Lightning Lane opens at { attraction['LLTimeStart'] }", font=fnt, fill=red)

			else:

				d.text((intialWidth + 60, height + 110 + 110), "Lightning Lane:", font=fnt, fill=red)
				d.text((1500, height + 110 + 110), attraction["LLTimeNext"], font=fnt, fill=red)

		img.save(outputImage)

def generateWelcomeBoard(inputImage, outputImage, time):

	currentTime = time.strftime("%I:%M %p")
	if(currentTime[0] == "0"):
		currentTime = currentTime[1:]

	offset = 270
	yellow = (214, 187, 54)
	green = (19, 191, 45)

	img = Image.open(inputImage)
	fnt = ImageFont.truetype('fonts/font.otf', 180)
	d = ImageDraw.Draw(img)

	text = "Welcome to EPCOT"
	d.text((getHorizontalCenter(img, fnt, text), getVerticalCenter(img, fnt, offset * -1, text)), text, font=fnt, fill=yellow)

	text = "The current time is:"
	d.text((getHorizontalCenter(img, fnt, text), getVerticalCenter(img, fnt, 0, text)), text, font=fnt, fill=green)

	text = currentTime
	d.text((getHorizontalCenter(img, fnt, text), getVerticalCenter(img, fnt, offset, text)), text, font=fnt, fill=yellow)

	img.save(outputImage)

def getHorizontalCenter(image, font, text):
	imageWidth = image.size[0]
	fontWidth = font.getsize(text)[0]
	return (imageWidth - fontWidth) / 2

def getVerticalCenter(image, font, offset, text):
	imageHeight = image.size[1]
	fontHeight = font.getsize(text)[1]
	return (imageHeight - fontHeight) / 2 + offset

def changeMainBoard():
	global mainBoardData

	if os.path.exists("static/main-board.png"):
		os.remove("static/main-board.png")
	os.link(f'images/main-board/{ mainBoardData["position"] }.png', "static/main-board.png")

	mainBoardData["position"] += 1

	if mainBoardData["position"] == mainBoardData["pages"]:
		mainBoardData["position"] = 0

def changeInnoventionsBoards():
	global innoventionsBoardsData

	if os.path.exists("static/east-board.png"):
		os.remove("static/east-board.png")
	os.link(f'images/east-board/{ innoventionsBoardsData["position"] }.png', "static/east-board.png")
	if os.path.exists("static/west-board.png"):
		os.remove("static/west-board.png")
	os.link(f'images/west-board/{ innoventionsBoardsData["position"] }.png', "static/west-board.png")

	innoventionsBoardsData["position"] += 1
	if innoventionsBoardsData["position"] == innoventionsBoardsData["pages"]:
		innoventionsBoardsData["position"] = -1
		time = datetime.now() + timedelta(seconds=7)
		generateWelcomeBoard("images/templates/east-board.png", "images/east-board/-1.png", time)
		generateWelcomeBoard("images/templates/west-board.png", "images/west-board/-1.png", time)
