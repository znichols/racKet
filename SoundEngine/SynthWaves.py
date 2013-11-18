#!/usr/bin/env python

import numpy as np
from scipy import signal


def generate_sine(sound_description):
    n_samples = int(round(0.2 * 44100))
    f_multiplier = sound_description['pitch'] * 2. * np.pi
    waveform = np.sin(np.arange(0, f_multiplier, f_multiplier / n_samples)) * 80
    return waveform.astype('int16')

def generate_square(sound_description):
    n_samples = int(round(0.2 * 44100))
    f_multiplier = sound_description['pitch'] * 2. * np.pi
    waveform = signal.square(np.arange(0, f_multiplier, f_multiplier / n_samples)) * 80
    return waveform.astype('int16')

def generate_sawtooth(sound_description):
    n_samples = int(round(0.2 * 44100))
    f_multiplier = sound_description['pitch'] * 2. * np.pi
    waveform = signal.sawtooth(np.arange(0, f_multiplier, f_multiplier / n_samples)) * 80
    return waveform.astype('int16')

wave_type_map = {'sine': generate_sine, 'sawtooth': generate_sawtooth, 'square': generate_square}

def create_sound(sound_description):
    return wave_type_map[sound_description['wave_type']](sound_description)
