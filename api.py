import image

import requests
import json
from datetime import datetime, timedelta
from copy import deepcopy

cookie = ""
cookieExpiration = datetime.now() - timedelta(seconds=1)

token = ""
tokenExpiration = datetime.now() - timedelta(seconds=1)

attractionsData = {}
oldApiData = {}

attractionsHours = {}

def updateAttractions():
		global attractionsData

		if not attractionsData:
			f = open("data/attractions.json")
			attractionsData = json.load(f)

		apiData = getDataFromApi()

		formattedAttractions = []
		for name in attractionsData:
			formattedAttraction = generateFormattedAttraction(name, attractionsData[name], apiData)
			formattedAttractions.append(formattedAttraction)

		writeDebug(formattedAttractions)
		image.generateBoards(formattedAttractions)

def generateFormattedAttraction(attractionName, attractionData, apiData):
	obj = {}

	if "name" in attractionData:
		obj["name"] = attractionData["name"]
	else:
		obj["name"] = attractionName

	if attractionName in apiData:
		attractionApiData = apiData[attractionName]
		obj["isAttraction"] = attractionApiData["asset"]["type"].lower() == "attraction"
		obj["isDown"] = not attractionApiData["standby"]["available"]
		if "waitTime" in attractionApiData["standby"]:
			obj["waitTime"] = attractionApiData["standby"]["waitTime"]
		else:
			obj["waitTime"] = 0
		obj["hasLL"] = "flex" in attractionApiData
		if obj["hasLL"]:
			obj["LLActive"] = attractionApiData["flex"]["available"]
			if "displayNextAvailableTime" in attractionApiData["flex"]:
				obj["LLTimeNext"] = attractionApiData["flex"]["displayNextAvailableTime"]
			if not obj["LLActive"] and "displayEnrollmentStartTime" in attractionApiData["flex"]:
				obj["LLTimeStart"] = attractionApiData["flex"]["displayEnrollmentStartTime"]
		obj["url"] = attractionApiData["asset"]["detailsUri"].split("/")[-2]

	else:
		obj["isAttraction"] = attractionData["isAttraction"]
		obj["waitTime"], obj["isDown"] = getDataFromOldApi(attractionData["qtimeName"])
		obj["hasLL"] = False
		obj["url"] = attractionData["url"]

	obj["open"], obj["close"] = getAttractionHours(obj["url"])
	obj["isOpen"] = obj["open"] < datetime.now() < obj["close"]

	return obj

def getCookie():
	global cookie, cookieExpiration

	if datetime.now() < cookieExpiration:
		return cookie

	s = requests.Session()
	s.headers.update({"user-agent" : "Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)"})
	r = s.post(url="https://disneyworld.disney.go.com/finder/api/v1/authz/public", data="{}")
	cookie = s.cookies.get_dict()["__d"]
	cookieExpiration = datetime.now() + timedelta(seconds=int(r.json()["result"]["expires_in"]) - 60)
	return cookie

def getToken():
	global token, tokenExpiration

	if datetime.now() < tokenExpiration:
		return token

	url = "https://disneyworld.disney.go.com/authentication/get-client-token/"
	r = requests.get(url, headers = {"user-agent" : "Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)", "cookie": f"__d={ getCookie() };"})
	token = r.json()["access_token"]
	tokenExpiration = datetime.now() + timedelta(seconds=int(r.json()["expires_in"]) - 60)
	return token

def getDataFromApi():
	url = "https://disneyworld.disney.go.com/tipboard-vas/api/v1/parks/80007838/experiences?userId=%7BCFBEEA52-3C8B-426A-BAB2-0A594CC6D256%7D&includeAssets=true"
	r = requests.get(url, headers = {"user-agent" : "Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)", "Authorization": f"BEARER { getToken() }"})

	data = {}
	for value in r.json()["availableExperiences"]:
		data[value["asset"]["name"]] = value
	return data

def getDataFromOldApi(name):
	global oldApiData

	try:
		r = requests.get("https://queue-times.com/parks/5/queue_times.json")
	except:
		if name in oldApiData:
			return oldApiData[name]["wait_time"], not oldApiData[name]["is_open"]
		else:
			return 0, False

	oldApiData = {}
	for element in r.json()["lands"][0]["rides"]:
		oldApiData[element["name"]] = element

	return oldApiData[name]["wait_time"], not oldApiData[name]["is_open"]

def getAttractionHours(attractionUrl):
	global attractionsHours

	if attractionUrl in attractionsHours and ( attractionsHours[attractionUrl]["close"] > datetime.now() or int(datetime.now().strftime("%H")) > 7 ):
		return attractionsHours[attractionUrl]["open"], attractionsHours[attractionUrl]["close"]

	dateUrl = datetime.now().strftime('%Y-%m-%d')
	url = f"https://disneyworld.disney.go.com/finder/api/v1/explorer-service/details-entity-simple/wdw/{ attractionUrl }/{ dateUrl }/"
	r = requests.get(url, headers = {"user-agent" : "Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)", "cookie": f"__d={ getCookie() };"})
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

	attractionsHours[attractionUrl] = {}
	attractionsHours[attractionUrl]["open"], attractionsHours[attractionUrl]["close"] = startTime, endTime

	return startTime, endTime

def writeDebug(formattedAttractions):

	with open("static/times.txt", "w") as f:
		f.write("Epcot Future World Wait Times:")
		for attraction in formattedAttractions:
			f.write(f'\n{ attraction["name"] } - { image.getOutput(attraction) }')

	with open("static/times.json", "w") as f:
		attractionsString = []
		for attraction in formattedAttractions:
			stringAttraction = deepcopy(attraction)
			stringAttraction["open"] = stringAttraction["open"].strftime("%Y-%m-%d, %H:%M:%S")
			stringAttraction["close"] = stringAttraction["close"].strftime("%Y-%m-%d, %H:%M:%S")
			attractionsString.append(stringAttraction)
		f.write(json.dumps(attractionsString, indent=2))
