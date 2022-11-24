from bs4 import BeautifulSoup
from urllib.request import urlopen
import yaml

def get_attraction_info():
	with open('attractions.yml', 'r') as file:

		attractions_info = {
		"attractions" : [],
		"names" : {}
		}

		attractions = yaml.safe_load(file)
		for attraction in attractions:
			if isinstance(attraction, str):
				attractions_info["attractions"].append(attraction)
			else:
				attraction_name = list(attraction.keys())[0]
				attractions_info["attractions"].append(attraction_name)
				attractions_info["names"][attraction_name] = attraction[attraction_name]["display name"]

		return attractions_info

def get_wait_times():

	attractions_info = get_attraction_info()

	statuses = ["Open", "Closed", "Down"]

	url = "https://www.laughingplace.com/w/p/epcot-current-wait-times/"
	page = urlopen(url)
	html = page.read().decode("utf-8")
	soup = BeautifulSoup(html, "html.parser")
	table = soup.find("table", {"class":"lp_attraction"})
	rows = table.find_all("tr")

	last_check_time = soup.find("span", {"id":"f_lastcheck"}).text.split(" ")[0]

	attraction_times = []

	for row in rows:
		cols = row.find_all("td")

		name = cols[0].text
		if name in attractions_info["attractions"]:

			attraction = {}
			attraction["location"] = attractions_info["attractions"].index(name)

			if(name in attractions_info["names"]):
				attraction["name"] = attractions_info["names"][name]
			else:
				attraction["name"] = name

			if cols[1].text in statuses:
				attraction["wait time"] = cols[1].text
			else:
				attraction["wait time"] = cols[1].text[:-4]

			if "Attraction Sold Out Today" in cols[2].text or "Attraction\xa0Sold\xa0Out\xa0Today" in cols[2].text:
				attraction["LL"] = "Lightning Lane all distributed"
			elif "Genie+" in cols[2].text or "LL" in cols[2].text:
				attraction["LL"] = cols[2].text.split(" ")[-1:][0] + "m"

			attraction_times.append(attraction)

	attraction_times = list(sorted(attraction_times, key=lambda attraction: attraction["location"]))
	for attraction in attraction_times:
		del attraction["location"]

	write_debug(attraction_times, last_check_time)

	return attraction_times

def write_debug(attractions, last_check_time):
	with open("static/times.txt", "w") as f:
		f.write(f"Epcot Future World Wait Times (last updated { last_check_time }):")
		for attraction in attractions:
			f.write(f'\n{ attraction["name"] } - { attraction["wait time"] }')
