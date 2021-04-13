from mycroft import MycroftSkill, intent_file_handler
from mapsClient import mapsClient

class TransitRouting(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    #gets the route to a destination from the current location or a given departure location [destination keyword REQUIRED]
    @intent_file_handler('routing.transit.intent')
    def handle_routing_transit(self, message):
        #initializes/retrieves client (singleton)
        gmaps = mapsClient.getClient()

        #gets the keyword values from the utterance
        departure = message.data.get('departure')
        destination = message.data.get('destination')

        #sets departure as here when there is no departure keyword as specified in mapsClient.py
        if departure is None:
            departure = "here"

        #receives directions in the format of a response string from Google Maps API through the client
        response = gmaps.getMycroftResponse(departure, destination)

        #responds to the user with directions to where they want to go
        self.speak(response)


def create_skill():
    return TransitRouting()

