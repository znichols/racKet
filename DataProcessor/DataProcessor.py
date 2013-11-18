#!/usr/bin/env python

import csv, time
import simplejson as json
from dateutil import parser
import numpy as np

import EventSender
from DataProcessingException import DataProcessingException

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
        self.chunk_interval = 0.033 #time in s to wait between sending bursts. Shouldn't make this too small

    def import_csv_file(self, csvfile):
        """Load a csv file with the column datatypes specified in the config"""
        reader = csv.reader(open(csvfile, 'r'))
        rows = [row for row in reader]
        if len(row[0]) < len(self.config['dimensions']):
            raise DataProcessingException('Fewer dimensions were specified in the config than exist in the data')
        formatted_rows = []
        for row in rows:
            formatted_rows.append(self.format_func(row))
        self.data = sorted(formatted_rows, key=lambda x: x[0])
        self.procrustes()

    def procrustes(self):
        """Rescales the continuous-values columns of data to the values specified by the sound bank file"""
        if not self.data or len(self.data) < 2:
            return
        for i in range(len(self.data[0])):
            if self.config['column_types'][i] != 'continuous':
                continue
            c_max, c_min = self.sound_bank[self.config['dimensions'][i]]['values']
            this_column = np.array([row[i] for row in self.data])
            this_column -= this_column.min()
            if this_column.max() > 0:
                this_column *= (c_max - c_min) / this_column.max()
            this_column += c_min
            for j, row in enumerate(self.data):
                row[i] = this_column[j]

    def send_data(self, time_stretch_interval, play_window=[0, 1]):
        """Send a portion of the loaded data to the sound engine via the EventSender
            the time_stretch_interval specifies how long (in seconds) that the portion should take to play
            the play_window specifies the portion of data to play, the default is to play all the data"""
        N = len(self.data)
        if N == 0:
            return
        this_data = [self.data[i] for i in range(int(play_window[0]*N), int(play_window[1]*N))]
        time_column = [row[0] for row in this_data]
        if self.config['column_types'][0] == 'datetime':
            #Currently discriminating at 1s resolution TODO: add ms or microseconds
            time_column = [(this_time - time_column[0]).total_seconds() for this_time in time_column]
        tcol_array = np.array(time_column)
        tcol_array -= tcol_array[0]
        if tcol_array[-1] > 0:
            tcol_array *= (time_stretch_interval / tcol_array[-1])
        i = 0
        start_t = time.time()
        time.sleep(self.chunk_interval)
        this_t = time.time()
        tdiff = this_t - start_t
        while True:
            this_event_bundle = {}
            while i < len(this_data):
                if tcol_array[i] > tdiff:
                    break
                row_tuple = tuple(this_data[i][1:])
                if row_tuple in this_event_bundle:
                    this_event_bundle[row_tuple]['volume'] += 1
                else:
                    this_event_bundle[row_tuple] = self._make_event_dict(this_data[i])
                i += 1
            for event in this_event_bundle.values():
                self.event_sender.send_event(event)
            if tdiff > time_stretch_interval:
                break
            after_event_t = time.time()
            if (after_event_t - this_t) < self.chunk_interval:
                time.sleep(self.chunk_interval - (after_event_t - this_t))
            this_t = time.time()
            tdiff = this_t - start_t

    def _make_event_dict(self, event):
        event_d = {'sound_bank': self.config['sound_bank'], 'features': {}}
        for i in range(1, len(event)):
            this_key = self.config['dimensions'][i]
            this_key_dtype = self.config['column_types'][i]
            this_value = None
            if this_key_dtype == 'continuous':
                this_value = str(event[i])
            else:
                this_value = self.sound_bank[this_key]['values'][event[i]]
            event_d['features'][this_key] = this_value
        event_d['volume'] = 1
        return event_d

    def _check_config(self):
        if self.config['column_types'][0] not in ['datetime', 'continuous']:
            raise DataProcessingException('The first data column specified in the config has to be either a \
                    continuous value or a DateTime string')
        for i in range(1, len(self.config['column_types'])):
            config_dtype = self.config['column_types'][i]
            if config_dtype == 'binary':
                config_dtype = 'categorical'
            config_dimension = self.config['dimensions'][i]
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
