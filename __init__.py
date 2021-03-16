from mycroft import MycroftSkill, intent_file_handler


class TransitRouting(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('routing.transit.intent')
    def handle_routing_transit(self, message):
        self.speak_dialog('routing.transit')


def create_skill():
    return TransitRouting()

