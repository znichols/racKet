#!/usr/bin/env python

import csv 
import simplejson as json

import EventSender

class SoundEvent:
    """Object to hold events for serializing and sending to the sound engine"""
    def __init__(self):
        pass

class DataProcessor:
    """Class for setting up the event sending client, for reading in data to send
        to the sound engine, and for translating data into sound events"""
    def __init__(self, configfile):
        self.config = json.load(open(configfile, 'r'))
        self.event_sender = EventSender.EventSender(self.config['socket_port'])
        sound_banks = json.load(open(self.config['sound_bank_definitions_file'], 'r'))
        self.sound_bank = sound_banks[self.config['sound_bank']]
    def send_event(self, event):
        pass

