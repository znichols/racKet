import math
import numpy
# from pygame.locals import *

class generate_tone:
	def __init__(self, cfg = None):
		pass

	def generate_sine(self,bits,sample_rate,duration,frequency):
		n_samples = int(round(duration*sample_rate))

		#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
		buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
		max_sample = 2**(bits - 1) - 1

		for s in range(n_samples):
		    t = float(s)/sample_rate    # time in seconds

		    #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
		    buf[s][0] = int(round(max_sample*math.sin(2*math.pi*frequency*t)))        # left
		return buf
