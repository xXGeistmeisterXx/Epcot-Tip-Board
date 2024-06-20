from bs4 import BeautifulSoup
from urllib.request import urlopen
import yaml
import json

class Attraction:

	def __init__(self, name):
		self.name = name
		self.display_name = name
		self.location = 0
		self.wait_time = ""
		self.LL = ""
		self.VQ = False

	def __str__(self):
		return f"""{ self.name }:
 - display name: { self.display_name }
 - wait time: { self.wait_time }
 - LL: { self.LL }
 - VQ: { self.VQ }"""

	def to_dict(self):
		return {
		"name" : self.name,
		"wait_time": self.wait_time,
		"LL": self.LL
		}

	def isOpen(self):
		return not (self.wait_time == "Closed") and not (self.wait_time == "Refurb")

	def LLOpen(self):
		return not (self.LL == "Lightning Lane all distributed")

attraction_info = {}

def get_attraction_info():

	global attraction_info

	if not attraction_info:

		with open('attractions.yml', 'r') as file:

			attractions_info = {
			"attractions" : [],
			"names" : {},
			"VQ" : {}
			}

			attractions = yaml.safe_load(file)
			for attraction in attractions:
				if isinstance(attraction, str):
					attractions_info["attractions"].append(attraction)
				else:
					attraction_name = list(attraction.keys())[0]
					attractions_info["attractions"].append(attraction_name)

					if "display name" in attraction[attraction_name]:
						attractions_info["names"][attraction_name] = attraction[attraction_name]["display name"]

					if "virtual queue" in attraction[attraction_name]:
						attractions_info["VQ"][attraction_name] = attraction[attraction_name]["virtual queue"]

		return attractions_info

def get_attractions():

	attractions_info = get_attraction_info()

	statuses = ["Open", "Closed", "Down", "Refurb"]

	url = "https://www.laughingplace.com/w/p/epcot-current-wait-times/"
	page = urlopen(url)
	html = page.read().decode("utf-8")
	soup = BeautifulSoup(html, "html.parser")
	table = soup.find("table", {"class":"lp_attraction"})
	rows = table.find_all("tr")

	last_check_time = soup.find("span", {"id":"f_lastcheck"}).text.split(" ")[0]
	park_hours = soup.find("div", {"class":"hours"}).text.split(": ")[1]

	attractions = []

	for row in rows:
		cols = row.find_all("td")

		name = cols[0].text
		if name in attractions_info["attractions"]:

			attraction = Attraction(name)
			attraction.location = attractions_info["attractions"].index(name)

			if name in attractions_info["names"]:
				attraction.display_name = attractions_info["names"][name]

			if name in attractions_info["VQ"]:
				attraction.VQ = attractions_info["VQ"][name]

			if cols[1].text in statuses:
				attraction.wait_time = cols[1].text
			else:
				attraction.wait_time = cols[1].text[:-4]

			if "Attraction Sold Out Today" in cols[2].text or "Attraction\xa0Sold\xa0Out\xa0Today" in cols[2].text:
				attraction.LL = "Lightning Lane all distributed"
			elif "Genie+" in cols[2].text or "LL" in cols[2].text:
				split_text = cols[2].text.split(" ")
				last_slot = split_text[-1]
				attraction.LL = last_slot if last_slot else split_text[-2]
				attraction.LL += "m"

			attractions.append(attraction)

	attractions = list(sorted(attractions, key=lambda attraction: attraction.location))
	for attraction in attractions:
		del attraction.location

	write_debug(attractions, last_check_time, park_hours)
	write_api(attractions, last_check_time)

	return attractions

def write_debug(attractions, last_check_time, park_hours):
	with open("static/times.txt", "w") as f:
		f.write(f"Epcot Future World Wait Times [{ park_hours }] (last updated { last_check_time }):")
		for attraction in attractions:
			f.write(f'\n{ attraction.display_name } - { attraction.wait_time }')

def write_api(attractions, last_check_time):
	api = { "update_time":last_check_time, "data":[attraction.to_dict() for attraction in attractions] }
	with open("static/api.json", "w") as f:
		json.dump(api, f)

if __name__ == "__main__":
	for attraction in get_attractions(): print(str(attraction) + "\n")
