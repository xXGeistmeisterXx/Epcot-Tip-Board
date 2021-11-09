import requests
import json
from datetime import datetime, timedelta
import requests
from tzlocal import get_localzone
import pytz
import copy

formattedAttractions = []
attractionTimes = {}
attractions = {}

def getOutput(attraction):
	result = f'{ attraction["time"] } min'
	if not attraction["isRide"]:
		result = "Open"
	elif attraction["time"] == 0:
		result = "No wait"
	if attraction["isDown"]:
		result = "Down"
	if not attraction["isOpen"]:
		result = "Closed"
	return result

def getAttractions():
	if not formattedAttractions:
		updateAttractions()
	return copy.deepcopy(formattedAttractions)

def updateAttractions():
		global formattedAttractions, attractions, attractionTimes

		try:
			r = requests.get("https://queue-times.com/parks/5/queue_times.json")
		except:
			return

		apiData = {}
		for element in r.json()["lands"][0]["rides"]:
			apiData[element["name"]] = element

		if not attractions:
			f = open("data/attractions.json")
			attractions = json.load(f)

		formattedAttractions = []
		for name in attractions:
			if name in apiData:
				obj = {"name":attractions[name]["name"], "isRide":attractions[name]["is_ride"], "time":apiData[name]["wait_time"], "isDown":not apiData[name]["is_open"]}

				if not obj["name"]:
					obj["name"] = name

				if name not in attractionTimes:
					attractionTimes[name] = getAttractionHours(attractions[name]["url"], datetime.now().strftime("%Y-%m-%d"))

				if attractionTimes[name]["close"] < datetime.now() and int(datetime.now().strftime("%H")) <= 7:
					attractionTimes[name] = getAttractionHours(attractions[name]["url"], datetime.now().strftime("%Y-%m-%d"))

				obj["isOpen"] = attractionTimes[name]["open"] < datetime.now() and attractionTimes[name]["close"] > datetime.now()

				formattedAttractions.append(obj)

		timeGet = datetime.fromisoformat(list(apiData.values())[0]["last_updated"][:-1]).replace(tzinfo=pytz.utc).astimezone(get_localzone()).strftime("%m/%d/%Y, %I:%M:%S %p")

		with open("static/times.txt", "w") as f:
			f.write("Epcot Future World Wait Times:")
			for attraction in formattedAttractions:
				f.write(f'\n{ attraction["name"] } - { getOutput(attraction) }')
			f.write(f'\n\nlast updated at { timeGet }')

		with open("static/times.json", "w") as f:
			f.write(json.dumps(formattedAttractions, indent=2))

		with open("static/hours.json", "w") as f:
			attractionTimesString = {}
			for attraction in attractionTimes:
				attractionTimesString[attraction] = {}
				attractionTimesString[attraction]["open"] = attractionTimes[attraction]["open"].strftime("%Y-%m-%d, %H:%M:%S")
				attractionTimesString[attraction]["close"] = attractionTimes[attraction]["close"].strftime("%Y-%m-%d, %H:%M:%S")
			f.write(json.dumps(attractionTimesString, indent=2))

def getCookie():
	s = requests.Session()
	s.headers.update({"user-agent" : "Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)"})
	r = s.post(url="https://disneyworld.disney.go.com/finder/api/v1/authz/public", data="{}")
	cookie = s.cookies.get_dict()["__d"]
	return cookie


def getAttractionHours(attractionUrl, dateUrl):

	url = f"https://disneyworld.disney.go.com/finder/api/v1/explorer-service/details-entity-simple/wdw/{ attractionUrl }/{ dateUrl }/"
	cookie = getCookie()
	r = requests.get(url, headers = {"user-agent" : "Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)", "cookie": f"__d={ cookie };"})
	timeDict = r.json()["aagData"]["schedule"]["schedules"]

	startTimeString = timeDict["Operating"]["Morning"][0]["startTime"]
	endTimeString = timeDict["Operating"]["Morning"][0]["endTime"]
	if "Early Entry" in timeDict:
		startTimeString = timeDict["Early Entry"][0]["startTime"]
	if "Extended Evening" in timeDict:
		endTimeString = timeDict["Extended Evening"][0]["endTime"]

	startTime = datetime.strptime(f"{ dateUrl }, { startTimeString }", "%Y-%m-%d, %H:%M:%S")
	endTime = datetime.strptime(f"{ dateUrl }, { endTimeString }", "%Y-%m-%d, %H:%M:%S")

	if startTime > endTime:
		endTime = endTime + timedelta(days=1)

	return {"open": startTime, "close": endTime}
