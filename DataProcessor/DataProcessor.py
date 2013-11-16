#!/usr/bin/env python

import csv
import simplejson as json
from dateutil import parser
import numpy as np

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
        self.data = None
        self._check_config()

    def send_event(self, event):
        pass

    def import_csv_file(self, csvfile):
        reader = csv.reader(open(csvfile, 'r'))
        rows = [row for row in reader]
        if len(row[0]) < len(self.config['Dimensions']):
            raise DataProcessingException('Fewer dimensions were specified in the config than exist in the data')
        formatted_rows = []
        for row in rows:
            formatted_rows.append(self.format_func(row))
        self.data = formatted_rows
        self.procrustes()

    def procrustes(self):
        """Rescales the continuous-values columns of data to the values specified by the sound bank file"""
        if not self.data or len(self.data) < 2:
            return
        for i in range(len(self.data[0])):
            if self.config['column_types'][i] != 'continuous':
                continue
            c_max, c_min = self.sound_bank[self.config['dimensions'][i]].values
            this_column = np.array([row[i] for row in self.data])
            this_column -= this_column.min()
            this_column *= (c_max - c_min) / this_column.max()
            this_column += c_min
            for j, row in enumerate(self.data):
                row[i] = this_column[j]

    def _check_config(self):
        if self.config['column_types'][0] not in ['datetime', 'continuous']:
            raise DataProcessingException('The first data column specified in the config has to be either a \
                    continuous value or a DateTime string')
        for i in range(1, len(self.config['column_types'])):
            config_dtype = self.config['column_types'][i]
            if config_dtype == 'binary':
                config_dtype = 'categorical'
            config_dimension = self.config['dimensions'][i-1]
            if config_dimension not in self.sound_bank:
                raise DataProcessingException('Sound Dimension specified in the config does not exist in the \
                        sound bank file')
            sound_bank_dtype = self.sound_bank[config_dimension]['type']
            if sound_bank_dtype != config_dtype:
                raise DataProcessingException('Data type for this dimension do not match between what is \
                        specified in the config and what the sound bank allows')

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
