#!/usr/bin/env python

import csv
import simplejson as json
from dateutil import parser

import EventSender
from DataProcessingException import DataProcessingException

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
        self.format_func = make_formatter(self.config)
    def send_event(self, event):
        pass

    def import_csv_file(self, csvfile):
        reader = csv.reader(open(csvfile, 'r'))
        rows = [row for row in reader]
        if len(row[0]) < len(self.config['Dimensions']):
            raise DataProcessingException('More Dimensions were specified in the config than exist in the data')
        formatted_rows = []
        for row in rows:
            formatted_rows.append(self.format_func(row))

def format_datetime(element, **kwargs):
    return parser.parse(element)

def format_categorical(element, seen_dict={}, **kwargs):
    if element in seen_dict:
        return seen_dict[element]
    else:
        this_category = len(seen_dict) + 1
        seen_dict[element] = this_category
        return this_category

def format_continuous(element, **kwargs):
    return float(element)

def format_boolean(element, **kwargs):
    if element == '0' or element[0] == 'F' or element[0] == 'f':
        return False
    return True

def make_formatter(config):
    dtypes = config['column_types']
    formatter_map = {'datetime': format_datetime, 'categorical': format_categorical, 
            'continuous': format_continuous, 'binary': format_boolean}
    seen_dict = {}
    def format_func(row):
        formatted_row = [formatter_map[dtype](element, seen_dict=seen_dict) for (element, dtype) \
                in zip(row, dtypes)]
        return formatted_row
    return format_func
