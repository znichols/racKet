import pygame
from pygame.locals import *
import socket, asyncore, sys
import simplejson as json
import numpy, math
import time
from SoundEngine import generate_tone

class BufferHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock):
        asyncore.dispatcher_with_send.__init__(self, sock)
    def handle_read(self):
        data = self.recv(1024)
        if data:
            events = data.split('#')
            for event in events:
                print event
                if event == '':
                    continue
                # post the sound
                my_event = pygame.event.Event(USEREVENT, {"duration":.100, "frequency" : event["features"]["pitch"], "pan": .5, "volume": 1 })
                pygame.event.post(my_event)

                if event[:4] == 'Exit':
                    # post the quit message
                    my_exit_event = pygame.event.Event(QUIT)
                    pygame.event.post(my_exit_event)

# class PyGameQueue:
#     def __init__(self):
#     # initialize event queue

# class ProcessQueue:
#     def __init__(self,)
def generate_sine(bits,sample_rate,duration,frequency,pan,volume = None):
        n_samples = int(round(duration*sample_rate))

        #setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
        buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
        max_sample = 2**(bits - 1) - 1

        
        pi_over_2 = math.pi/2
        if volume >= 100:
            volume = 99
        # at least some volume
        amplitude = .3 + (.01 * volume)
        if amplitude > 1.0:
            amplitude = 1.0
        for s in range(n_samples):
            t = float(s)/sample_rate    # time in seconds


            #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
            signal =  amplitude * int(round(max_sample*math.sin(2*math.pi*frequency*t)))
            aSigL  =     signal * math.sin(pan*pi_over_2)
            aSigR  =     signal * math.cos(pan*pi_over_2)
            buf[s][0] = aSigL       # left
            buf[s][1] = aSigR        # right
        
        # layer click from resources
        # buf[s][2] = 
        # buf[s][3] = 
        
        return buf

class Server(asyncore.dispatcher):
    def __init__(self, host, port,l_size,l_bits,l_sample_rate,l_channels):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        pygame.mixer.pre_init(l_sample_rate, -l_bits, l_channels)
        pygame.init()

        _display_surf = pygame.display.set_mode(l_size, pygame.HWSURFACE | pygame.DOUBLEBUF)
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = BufferHandler(sock)

# class StartEngine(self,l_size,l_bits,l_sample_rate,l_channels):
#       try:
#           pygame.mixer.pre_init(l_sample_rate, -l_bits, l_channels)
#           pygame.init()
#           _display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)

#       except:
#           self.logger.debug("Couldn't couldn't start audio mixer server?")
#           raise


def main():
    if len(sys.argv) < 2:
        print "Usage: %s <configfile> [num_events]" % sys.argv[0]
        sys.exit(-1)
    configfile = sys.argv[1]
    config = json.load(open(configfile, 'r'))
    host = socket.gethostname()
    port = config['socket_port']
    BITS = config['bits']
    SAMPLE_RATE = config['sample_rate']
    
    window_size = (config['window_size']['width'],config['window_size']['height'])
    print window_size
    # window_size[1] = config['window_size']['height']
    bits = config['bits']
    sample_rate = config['sample_rate']
    channels = config['channels']
    server = Server(host, port,window_size,bits,sample_rate,channels)
    pygame.event.set_allowed([ USEREVENT, QUIT ])
    # my_event = pygame.event.Event(USEREVENT, {"duration":.030, "frequency":440, "pan": 1, "volume": 1 })
    # pygame.event.post(my_event)
    # my_event = pygame.event.Event(USEREVENT, {"duration":.100, "frequency":550, "pan": 1, "volume": 1 })
    # pygame.event.post(my_event)
    # my_exit_event = pygame.event.Event(QUIT)
    # pygame.event.post(my_exit_event)

    if pygame.event.peek([USEREVENT, QUIT]) is not True:
        sys.exit("No Events in Stream!")
    for e in pygame.event.get():
        print "event"
        print e
        if e.type == QUIT:
            time.sleep(1)
            pygame.quit()
            sys.exit()
        elif e.type == USEREVENT:
            buf = generate_sine(BITS,SAMPLE_RATE,e.duration,e.frequency,e.pan,e.volume)
            sound = pygame.sndarray.make_sound(buf)
            #play once, then loop forever
            sound.play()
        time.sleep(2 * e.duration)
        asyncore.loop(e.duration)

    
if __name__ == '__main__':
    main()


