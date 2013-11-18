#!/usr/bin/env python

import simplejson as json
import cv, time, sys
import numpy as np
from pylab import *

import EventSender

class VideoClient:
    def __init__(self, config, capture):
        self.config = json.load(open(config, 'r'))
        self.event_sender = EventSender.EventSender(self.config['socket_port'])
        #self.event_sender = None

        sound_banks = json.load(open(self.config['sound_bank_definitions_file'], 'r'))
        self.sound_bank = sound_banks[self.config['sound_bank']]
        self.update_interval = 0.1 #time in s to wait between sending bursts. Shouldn't make this too small
        self.capture = capture
        self.sound_cutoff = 50.
    def hear_some_video(self):
        frame_num = 0
        frame = None
        while frame == None:
            print "Still got no frame"
            frame = cv.QueryFrame(self.capture)
            cv.WaitKey(2)
        last_frame_array = np.asarray(frame[:, :])
        while True:
            time.sleep(self.update_interval)
            frame_num += 1
            print 'Current frame: ', frame_num
            frame = None
            while frame == None:
                frame = cv.QueryFrame(self.capture)
                cv.WaitKey(1)
            this_frame_array = np.asarray(frame[:, :])
            d = (this_frame_array.astype('i') - last_frame_array.astype('i')).sum(2)
            self.play_sound_from_frame_diff(d)
            last_frame_array = this_frame_array.copy()
    def play_sound_from_frame_diff(self, frame_diff):
        num_pitches = 6
        lines_per_pitch = frame_diff.shape[1] / num_pitches
        print abs(frame_diff).mean()
        for i in range(num_pitches):
            if abs(frame_diff[:, i*lines_per_pitch:(i+1)*lines_per_pitch]).mean() > self.sound_cutoff:
                event = self._make_event_dict(i)
                #print event
                self.event_sender.send_event(event)

    def _make_event_dict(self, i):
        event_d = {'sound_bank': self.config['sound_bank'], 'features': 
                {'wave_type': 'sine', 'pitch': self.sound_bank['pitch']['values'][i]}}
        event_d['volume'] = 1
        return event_d

def main():
    cv.NamedWindow("Video", cv.CV_WINDOW_AUTOSIZE)
    capture = cv.CaptureFromCAM(0)
    cv.WaitKey(5)
    vc = VideoClient(sys.argv[1], capture)
    vc.hear_some_video()

if __name__=='__main__':
    main()
