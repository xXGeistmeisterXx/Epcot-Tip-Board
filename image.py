import api
from api import getOutput

from PIL import Image, ImageDraw, ImageFont
import time

mainBoardData = []
innoventionsBoardData = {}

def generateMainBoard(inputImage, outputImage):
	global mainBoardData

	spacing = 100
	intialHeight = 80
	pageLength = 7
	green = (19, 191, 45)

	if not mainBoardData:
		mainBoardData = api.getAttractions()

	img = Image.open(inputImage)
	fnt = ImageFont.truetype('fonts/font.otf', 90)
	d = ImageDraw.Draw(img)

	for attraction in mainBoardData[:pageLength]:
		height = intialHeight + mainBoardData.index(attraction) * spacing

		d.text((80, height), attraction["name"], font=fnt, fill=(255, 255, 255))
		d.text((1750, height), getOutput(attraction), font=fnt, fill=green)

	del mainBoardData[:pageLength]

	img.save(outputImage)

def generateInnoventionsBoard(inputImage, outputImage, loc):
	global innoventionsBoardData

	intialHeight = 180
	spacing = 100
	yellow = (214, 187, 54)
	green = (19, 191, 45)

	if loc not in innoventionsBoardData:
		innoventionsBoardData[loc] = api.getAttractions()
		generateWelcomeBoard(inputImage, outputImage)
		return

	img = Image.open(inputImage)
	fnt = ImageFont.truetype('fonts/font.otf', 115)
	d = ImageDraw.Draw(img)

	for attraction in innoventionsBoardData[loc][:2]:
		height = intialHeight + innoventionsBoardData[loc].index(attraction) * 510

		d.text((80, height), attraction["name"], font=fnt, fill=(255, 255, 255))

		if(attraction["isOpen"]):
			d.text((80 + 60, height + 110), "Stand-by", font=fnt, fill=yellow)
			d.text((1500, height + 110), getOutput(attraction), font=fnt, fill=green)
		else:
			d.text((80 + 60, height + 110), "Closed", font=fnt, fill=yellow)

	del innoventionsBoardData[loc][:2]

	if not innoventionsBoardData[loc]:
		del innoventionsBoardData[loc]

	img.save(outputImage)

def getHorizontal(image, font, text):
	imageWidth = image.size[0]
	fontWidth = font.getsize(text)[0]
	return (imageWidth - fontWidth) / 2

def getVertical(image, font, offset, text):
	imageHeight = image.size[1]
	fontHeight = font.getsize(text)[1]
	return (imageHeight - fontHeight) / 2 + offset

def generateWelcomeBoard(inputImage, outputImage):

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
	d.text((getHorizontal(img, fnt, text), getVertical(img, fnt, offset * -1, text)), text, font=fnt, fill=yellow)

	text = "The current time is:"
	d.text((getHorizontal(img, fnt, text), getVertical(img, fnt, 0, text)), text, font=fnt, fill=green)

	text = currentTime
	d.text((getHorizontal(img, fnt, text), getVertical(img, fnt, offset, text)), text, font=fnt, fill=yellow)

	img.save(outputImage)
