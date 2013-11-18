#!/usr/bin/env python

import pygame
import socket, asyncore, sys, time, signal
import simplejson as json
import numpy as np
from threading import Timer, Thread
import SynthWaves

class SoundPlayer:
    """Sends sound events to pygame to play. Since pygame can only mix 8 sounds at once,
    this object also mixes together all the sounds that occur in a 200ms window, and
    send the results to pygame. If sounds last 1s max, this means pygame only has to handle
    mixing 5 (downmixed) sounds together, and we'll handle the rest"""
    #TODO make the windowing and pre-mixing more flexible to reduce latency or allow for longer
    #sound lengths
    #TODO add adjustable waveform lengths and volumes
    #TODO add other sound banks
    def __init__(self, jsonconfig):
        self.config = jsonconfig
        self.sound_banks = json.load(open(self.config['sound_bank_definitions_file'], 'r'))
        self.event_waveforms = {}
        self.buffer = np.zeros(44100, dtype='int16')
        self.buffer_start_t = time.time()
        self.n_events = 0

    def add_sound_to_buffer(self, sound_description):
        current_t = time.time()
        tdiff = current_t - self.buffer_start_t
        if tdiff > 0.75:
            print "Warning: this sound got here too late to go in the buffer. Is the Scheduler running?"
            return
        sound_index = int(44100 * tdiff)
        sound_waveform = self.make_sound_waveform(sound_description)
        self.buffer[sound_index:sound_index+len(sound_waveform)] += sound_waveform
        self.n_events += 1
        
    def send_buffer_to_pygame(self):
        if self.n_events > 0:
            sound_array = self.buffer
            sound_array[sound_array < -128] = -128
            sound_array[sound_array > 128] = 128
            sound = pygame.sndarray.make_sound(sound_array.astype('uint8'))
            sound.play()
            self.n_events = 0
            self.buffer = np.zeros(44100, dtype='int16')
        self.buffer_start_t = time.time()

    def make_sound_waveform(self, sound_description):
        sound_key = sound_description['sound_bank'] + \
            str(sorted([(k, sound_description['features'][k]) for k in sound_description['features']]))
        if sound_key in self.event_waveforms:
            return self.event_waveforms[sound_key]
        if sound_description['sound_bank'] not in ['synth_waves']:
            print "Sound bank not found... skipping"
            return np.zeros(1)
        this_sound = SynthWaves.create_sound(sound_description['features'])
        self.event_waveforms[sound_key] = this_sound
        return this_sound

class SoundBufferScheduler(Thread):
    """Runs in a separate thread and calls the SoundPlayer methods to send the current sound
    buffer to pygame, and to switch to the next buffer"""
    def __init__(self, sound_player, update_time=0.2):
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
    def __init__(self, sock, sound_player, scheduler):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.sound_player = sound_player
        self.scheduler = scheduler
    def handle_read(self):
        data = self.recv(1024)
        if data:
            events = data.split('#')
            for event in events:
                if event == '':
                    continue
                if event[:4] == 'Exit':
                    self.scheduler.stop()
                    sys.exit(0)
                sound_description = json.loads(event)
                self.sound_player.add_sound_to_buffer(sound_description)
                print event

class SoundServer(asyncore.dispatcher):
    def __init__(self, host, port, sound_player, scheduler):
        self.sound_player = sound_player
        self.scheduler = scheduler
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = SoundEventHandler(sock, self.sound_player, self.scheduler)

def main():
    if len(sys.argv) < 2:
        print "Usage: %s <configfile>" % sys.argv[0]
        sys.exit(-1)

    configfile = sys.argv[1]
    config = json.load(open(configfile, 'r'))
    pygame.mixer.init(config['sample_rate'], config['sound_bits'], config['channels'], 1024)
    sound_player = SoundPlayer(config)
    buffer_scheduler = SoundBufferScheduler(sound_player)
    buffer_scheduler.start()

    def exit_handler(signal, frame):
        buffer_scheduler.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, exit_handler)

    host = socket.gethostname()
    port = config['socket_port']
    server = SoundServer(host, port, sound_player, buffer_scheduler)
    asyncore.loop(1)

if __name__ == '__main__':
    main()
