import numpy as np
import os

import wave
import pydub
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import random
from pydub.playback import play
import matplotlib.pyplot as plt


from Sound import Sound


def visulize_sound(path):
    # load sound and visulize the waves ???
    spf = wave.open(path, "r")

    # Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    # print(signal[:100])
    signal = np.fromstring(signal, "Int16")

    print(signal[:100])
    # If Stereo
    if spf.getnchannels() == 2:
        print("Just mono files")

    plt.figure(1)
    plt.title("Signal Wave...")
    plt.plot(signal)
    plt.show()


#### value function --> 




if __name__ == "__main__":
    visulize_sound("processed_sound_inputs/animal-market.wav")
