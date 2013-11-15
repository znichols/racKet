#!/usr/bin/env python

import sys, time
import simplejson as json
import DataProcessor, EventSender

def main():
    config = json.load(open(sys.argv[1], 'r'))
    port = config['socket_port']
    event_sender = EventSender.EventSender(port)
    event_sender.send_string_event(sys.argv[2])
    event_sender.send_exit_event()

if __name__=='__main__':
    main()

