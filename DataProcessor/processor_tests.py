#!/usr/bin/env python

import unittest
import socket, time
import simplejson as json
from subprocess import Popen, PIPE

import DataProcessor, EventSender

class TestConvertingData(unittest.TestCase):
    pass

class TestSendingEvent(unittest.TestCase):
    def setUp(self):
        self.config = json.load(open('resources/config.json', 'r'))
        host = socket.gethostname()
        port = self.config['socket_port']
        self.server_process = Popen(['python', 'MockServer.py', 'resources/config.json'], stdout=PIPE)
        time.sleep(1)
        self.client = EventSender.EventSender(port)
    def test_send_event(self):
        event = '{"sound_bank": "synth_waves", "features": {"pitch": 587.3, "wave_type": "square"}}'
        event_json = json.loads(event)
        self.client.send_event(event_json)
        print "Reading STDOUT"
        out = self.server_process.stdout.read()
        self.assertEqual(json.loads(event), json.loads(out))

class TestReadingConfig(unittest.TestCase):
    pass

class TestRescalingData(unittest.TestCase):
    pass

if __name__=='__main__':
    unittest.main()
