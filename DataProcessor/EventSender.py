#!/usr/bin/env python

import logging, socket, sys
import simplejson as json

class EventSender:
    """Object for setting up an event sending client to talk to the sound engine server"""
    def __init__(self, port, logging_handler=logging.StreamHandler(stream=sys.stdout)):
        self.logger = logging.getLogger(__name__)
        if logging_handler:
            self.logger.addHandler(logging_handler)
        self.logger.setLevel(logging.INFO)
        self.socket_port = port
        host = socket.gethostname()
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, self.socket_port))
        except:
            self.logger.debug("Couldn't open the socket to send messages. Is the sound engine up?")
            raise

    def send_event(self, json_event):
        str_event = json.dumps(json_event)
        print str_event
        self.socket.send(str_event + '#')
    def send_string_event(self, string_event):
        self.socket.send(string_event + '#') 
    def send_exit_event(self):
        self.socket.send('Exit#')
