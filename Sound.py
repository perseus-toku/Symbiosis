import numpy as np
import os

import wave
import pydub
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import random
from pydub.playback import play


class Sound:
    """
        A class to store the sound object
    """

    # max_duration --> seconds of sound input to get
    def __init__(
        self, selection="random", max_duration=10, sound_dir="processed_sound_inputs"
    ):
        # randomly select a sound
        self.max_duration = max_duration
        self.sound_dir = sound_dir
        if selection == "random":
            # select from the folder
            self.sound_file = self.rand_get_a_sound()
        else:
            raise ValueError("unknown selection method")

        # should load the sound
        # try not to load in the sound in the beginning, load the information dynamically
        self.loaded_sound = self.try_load_sound()

    def __len__(self):
        # read in the sound object and get the length from it
        self.try_load_sound()
        # get the length of the audiosegment object
        return len(self.loaded_sound)

    def rand_get_a_sound(self):
        # randomly select a sound input object to store in the current file
        files = []
        for file in os.listdir(self.sound_dir):
            if "wav" in file:
                files.append(os.path.join(self.sound_dir, file))
                selected = np.random.choice(files, 1, replace=False)
        # do not load here, only load dynamically
        return selected[0]

    def try_load_sound(self):
        # load the sound if it is not already done
        loaded_sound = AudioSegment.from_wav(self.sound_file)
        # truncate the sound file if necessary
        if len(loaded_sound) > self.max_duration * 1000:
            # truncate -- > randomly select a part
            s = random.randint(0, len(loaded_sound) - self.max_duration * 1000)
            loaded_sound = loaded_sound[s : s + self.max_duration * 1000]
        return loaded_sound

    def play_sound(self):
        # use pyaudio funcitons to play the sound --> use functions from util.py
        pass

    def set_modified_sound(self, in_sound):
        self.loaded_sound = in_sound

    def play(self):
        ### should be able to play the sound without any io operations
        # loaded sound is an audio segment
        play(self.loaded_sound)

    def save_sound(self, path):
        # save the sound to an output directory for play back --> then let a different function handle play back
        if "wav" not in path:
            raise NameError(f"sound path doesn't have wav in it : {path}")
        self.loaded_sound.export(path, format="wav")


if __name__ == "__main__":
    s = Sound()

    # run some quick test on sound
