import googlemaps, geocoder
from datetime import datetime

class mapsClient:
    __instance = None
    client = None
    #creates or returns the single instance of the maps client
    @staticmethod
    def getClient():
        if mapsClient.__instance == None:
            mapsClient.__instance = mapsClient()
        return mapsClient.__instance

    #initializes (only called when there is no instance)
    def __init__(self):
        if mapsClient.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            mapsClient.__instance = self
            mapsClient.client = googlemaps.Client(self.getKey())

    #gets the key from the hidden file
    def getKey(self):
        keyFile = open(".key.txt")
        return keyFile.read()

    #gets the intended route directions
    def getRoute(self, departure, destination):
        #gets the latitude/longitude of the current location for default departure (doesn't affect the string)
        if departure == "here":
            departureLatLng = geocoder.ip('me').latlng
            departure = str(departureLatLng[0]) + "," + str(departureLatLng[1])
        gmaps = self.getClient()
        now = datetime.now()
        directions_result = gmaps.client.directions(departure, destination, mode="transit", departure_time=now)
        return directions_result

    def getMycroftResponse(self, departure, destination):
        #initializes a mycroft response string to be built while parsing through the data
        mycroftResponse = ""

        #gets the payload containing relevant information
        directions_result = self.getRoute(departure, destination)
        if len(directions_result) == 0:
            mycroftResponse = "Sorry. Something went wrong, and I wasn't able to get the route from " + departure + " to " + destination + ". Please try again or try asking me in a different way."
            return mycroftResponse
        extractedPayload = extractPayload(directions_result)

        #Builds the mycroft response with the data from google maps
        mycroftResponse += formatTimeandDistance(extractedPayload, departure, destination)
        #loops through data in extracted payload to update the html-instructions into a more human-like format
        for data in extractedPayload: 
            if(isinstance(data, str)):
                mycroftResponse += formatInstructions(data)

        mycroftResponse += "You will then have arrived at your destination."

        return mycroftResponse

#extracts information we need from full directions payload
def extractPayload(jsonPayload):
    newPayload = []
    #google maps' json payloads are stored as lists of json data
    for listElement in jsonPayload:
        #an overarching list "legs" contains the json payloads for directions
        legs = listElement.get("legs")

        #within each leg, there is a json payload of travelling directions
        for leg in legs:
            newPayload.append(leg.get("departure_time"))
            newPayload.append(leg.get("arrival_time"))
            newPayload.append(leg.get("duration"))

            #steps has large payloads of data which include html instructions, distance, start, destination, etc. for each step in the process
            steps = leg.get("steps")
            for step in steps:
                newPayload.append(step.get("html_instructions"))

    return newPayload

#reformats the instruction strings into more human instructions (2 cases specified in API request mode field: either walking or taking public transportation)
def formatInstructions(instruction):
    #splits the instruction into individual words
    instructionParts = instruction.split(" ")

    #normally will say "Bus/Train/Subway/etc to {destination}" for transit directions, but we want our VTA not to speak like a computer
    if instructionParts[0] != "Walk": 
        newInstructionStart = "Take the " + instructionParts[0].lower()
        instructionParts.pop(0) #removes the first element of the instruction parts
        instructionParts.insert(0, newInstructionStart)
        instruction = " ".join(instructionParts)
    instruction = instruction + ". "

    return instruction

#reformats the data payloads for time and distance to how they will be read to the user [takes in the full payload for data accuracy]
def formatTimeandDistance(tdData, departure, destination):
    #payload contains the departure time as the first element
    depTime = tdData[0].get("text") + " " + tdData[0].get("time_zone") + " time"

    #payload contains the ETA as the second element
    ETA = tdData[1].get("text") + " " + tdData[1].get("time_zone") + " time"

    #payload contains the duration as the third element and needs reformatting to be read correctly (the time measurement is abbreviated)
    duration = tdData[2].get("text").replace("mins", "minutes")
    duration = duration.replace("hrs", "hours")

    #puts info together in string to be read by TTS
    tdString = "Leaving " + departure + " at " + depTime + ", you will get to " + destination + " at " + ETA + ". The trip will take " + duration + ". "
    return tdString




#testing
def main():
    client = mapsClient.getClient()
    print(client.getMycroftResponse("here","New York City"))


if __name__ == "__main__":
    main()

