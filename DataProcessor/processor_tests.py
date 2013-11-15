#!/usr/bin/env python

import unittest
import socket, asyncore
import simplejson as json

import DataProcessor, EventSender

class BufferHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, message_list):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.message_list = message_list
    def handle_read(self):
        data = self.recv(1024)
        if data:
            message_list.append(data)

class MockServer(asyncore.dispatcher):
    def __init__(self, host, port, message_list = []):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.message_list = message_list
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = BufferHandler(sock, self.message_list)

class TestConvertingData(unittest.TestCase):
    pass

class TestSendingEvent(unittest.TestCase):
    def setUp(self):
        self.config = json.load(open('resources/config.json', 'r'))
        host = socket.gethostname()
        port = self.config['socket_port']
        self.server = MockServer(host, port)
        self.client = EventSender.EventSender(port)
        #asyncore.loop()
    def test_send_event(self):
        event = """{"sound_bank": "synth_waves", "features": {"pitch": 587.3, "wave_type": "square"}}"""
        event_json = json.loads(event)
        self.client.send_event(event_json)
        self.assertTrue(len(self.server.message_list) == 1)
        self.assertEqual(self.server.message_list[0], event)

class TestReadingConfig(unittest.TestCase):
    pass

class TestRescalingData(unittest.TestCase):
    pass

if __name__=='__main__':
    unittest.main()
