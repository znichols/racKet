#!/usr/bin/env python

import pygame
import socket, asyncore, sys, time
import simplejson as json
from threading import Timer, Thread

class SoundPlayer:
    """Sends sound events to pygame to play. Since pygame can only mix 8 sounds at once,
    this object also mixes together all the sounds that occur in a 200ms window, and
    send the results to pygame. If sounds last 1s max, this means pygame only has to handle
    mixing 5 (downmixed) sounds together, and we'll handle the rest"""
    #TODO make the windowing and pre-mixing more flexible to reduce latency or allow for longer
    #sound lengths
    def __init__(self, jsonconfig):
        self.config = jsonconfig
        sound_banks = json.load(open(self.config['sound_bank_definitions_file'], 'r'))
    def play_sound(self, sound_description):
        pass
    def send_buffer_to_pygame(self):
        print "Sending current buffer to pygame"
        print "Current time: ", time.time()

class SoundBufferScheduler(Thread):
    """Runs in a separate thread and calls the SoundPlayer methods to send the current sound
    buffer to pygame, and to switch do the next buffer"""
    def __init__(self, sound_player, update_time):
        Thread.__init__(self)
        self.sound_player = sound_player
        self.update_time = update_time
        self.on = True
    def run(self):
        while self.on:
            buffer_switch_thread = Timer(self.update_time, self.sound_player.send_buffer_to_pygame)
            buffer_switch_thread.start()
            buffer_switch_thread.join()
    def stop(self):
        self.on = False

class SoundEventHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock):
        asyncore.dispatcher_with_send.__init__(self, sock)
    def handle_read(self):
        data = self.recv(1024)
        if data:
            events = data.split('#')
            for event in events:
                if event == '':
                    continue
                if event[:4] == 'Exit':
                    sys.exit(0)
                print event

class SoundServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = BufferHandler(sock)


def main():
    if len(sys.argv) < 2:
        print "Usage: %s <configfile> [num_events]" % sys.argv[0]
        sys.exit(-1)

    configfile = sys.argv[1]
    config = json.load(open(configfile, 'r'))
    sound_player = SoundPlayer(config)
    buffer_scheduler = SoundBufferScheduler(sound_player, 0.5)
    buffer_scheduler.start()
    time.sleep(5)
    buffer_scheduler.stop()

    #host = socket.gethostname()
    #port = config['socket_port']
    #server = SoundServer(host, port)
    #asyncore.loop(1)

if __name__ == '__main__':
    main()
