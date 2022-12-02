from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import math
import os

main_board_data = {}
main_board_data["position"] = 0

innoventions_boards_data = {}
innoventions_boards_data["position"] = -1

def generate_boards(attractions):

	if not os.path.exists("images/main-board"):
		os.makedirs("images/main-board")

	if not os.path.exists("images/west-board"):
		os.makedirs("images/west-board")

	if not os.path.exists("images/east-board"):
		os.makedirs("images/east-board")

	generate_main_board(attractions)
	generate_innoventions_boards(attractions)

def generate_main_board(attractions):
	global main_board_data

	page_length = 7

	main_board_data["pages"] = math.ceil(len(attractions) / page_length)

	intial_height = 90
	spacing = 100
	green = (19, 191, 45)

	for page in range(main_board_data["pages"]):

		img = Image.open("images/templates/main-board.png")
		fnt = ImageFont.truetype('fonts/font.otf', 90)
		d = ImageDraw.Draw(img)

		starting_index = page * page_length
		page_attractions = attractions[starting_index:starting_index + page_length]
		for attraction in page_attractions:
			height = intial_height + page_attractions.index(attraction) * spacing

			d.text((90, height), attraction.display_name, font=fnt, fill=(255, 255, 255))
			d.text((1750, height), attraction.wait_time, font=fnt, fill=green)

			img.save(f"images/main-board/{ page }.png")

def generate_innoventions_boards(attractions):
	global innoventions_boards_data

	pageLength = 2
	innoventions_boards_data["pages"] = math.ceil(len(attractions) / pageLength)


	for page in range(innoventions_boards_data["pages"]):
		starting_index = page * pageLength
		generate_innoventions_page("images/templates/east-board.png", f"images/east-board/{ page }.png", attractions[starting_index:starting_index + pageLength])
		generate_innoventions_page("images/templates/west-board.png", f"images/west-board/{ page }.png", attractions[starting_index:starting_index + pageLength])

	time = datetime.now()
	generate_welcome_board("images/templates/east-board.png", "images/east-board/-1.png", time)
	generate_welcome_board("images/templates/west-board.png", "images/west-board/-1.png", time)

def generate_innoventions_page(input_image, output_image, attractions):

	intial_height = 175
	spacing = 100
	intial_width = 90
	yellow = (214, 187, 54)
	green = (19, 191, 45)
	red = (184, 31, 31)

	img = Image.open(input_image)
	fnt = ImageFont.truetype('fonts/font.otf', 115)
	d = ImageDraw.Draw(img)

	for attraction in attractions:
		height = intial_height + attractions.index(attraction) * 492

		d.text((intial_width, height), attraction.display_name, font=fnt, fill=(255, 255, 255))

		if(attraction.isOpen()):
			open_text = "Virtual-Queue" if attraction.VQ else "Stand-By"
			d.text((intial_width + 60, height + 110), open_text, font=fnt, fill=yellow)
			d.text((1500, height + 110), attraction.wait_time, font=fnt, fill=green)
		else:
			d.text((intial_width + 60, height + 110), "Closed", font=fnt, fill=yellow)

		if attraction.LL:

			if attraction.LLOpen():

				d.text((intial_width + 60, height + 110 + 110), "Lightning Lane:", font=fnt, fill=red)
				d.text((1500, height + 110 + 110), attraction.LL, font=fnt, fill=red)

			elif attraction.isOpen():

				d.text((intial_width + 60, height + 110 + 110), "Lightning Lane all distributed", font=fnt, fill=red)


		img.save(output_image)

def generate_welcome_board(input_image, output_image, time):

	current_time = time.strftime("%I:%M %p")
	if(current_time[0] == "0"):
		current_time = current_time[1:]

	offset = 270
	yellow = (214, 187, 54)
	green = (19, 191, 45)

	img = Image.open(input_image)
	fnt = ImageFont.truetype('fonts/font.otf', 180)
	d = ImageDraw.Draw(img)

	text = "Welcome to EPCOT"
	d.text((get_horizontal_center(img, fnt, text), get_vertical_center(img, fnt, offset * -1, text)), text, font=fnt, fill=yellow)

	text = "The current time is:"
	d.text((get_horizontal_center(img, fnt, text), get_vertical_center(img, fnt, 0, text)), text, font=fnt, fill=green)

	text = current_time
	d.text((get_horizontal_center(img, fnt, text), get_vertical_center(img, fnt, offset, text)), text, font=fnt, fill=yellow)

	img.save(output_image)

def get_horizontal_center(image, font, text):
	image_width = image.size[0]
	font_width = font.getsize(text)[0]
	return (image_width - font_width) / 2

def get_vertical_center(image, font, offset, text):
	image_height = image.size[1]
	font_height = font.getsize(text)[1]
	return (image_height - font_height) / 2 + offset

def change_main_board():
	global main_board_data

	if os.path.exists("static/main-board.png"):
		os.remove("static/main-board.png")
	os.link(f'images/main-board/{ main_board_data["position"] }.png', "static/main-board.png")

	main_board_data["position"] += 1

	if main_board_data["position"] == main_board_data["pages"]:
		main_board_data["position"] = 0

def change_innoventions_boards():
	global innoventions_boards_data

	if os.path.exists("static/east-board.png"):
		os.remove("static/east-board.png")
	os.link(f'images/east-board/{ innoventions_boards_data["position"] }.png', "static/east-board.png")
	if os.path.exists("static/west-board.png"):
		os.remove("static/west-board.png")
	os.link(f'images/west-board/{ innoventions_boards_data["position"] }.png', "static/west-board.png")

	innoventions_boards_data["position"] += 1
	if innoventions_boards_data["position"] == innoventions_boards_data["pages"]:
		innoventions_boards_data["position"] = -1
		time = datetime.now() + timedelta(seconds=7)
		generate_welcome_board("images/templates/east-board.png", "images/east-board/-1.png", time)
		generate_welcome_board("images/templates/west-board.png", "images/west-board/-1.png", time)
