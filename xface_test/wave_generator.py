from math import *

#A class to generate some signals
class WaveGenerator(object):

    def generate_sine(samples, amplitude):
        dx = 2*pi/samples;

        x = 0
        result = []
        for i in range(samples):
            x = x+dx
            result.append(int(round(sin(x)*amplitude))+127)
        return result
