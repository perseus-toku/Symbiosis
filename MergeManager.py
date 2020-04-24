import numpy as np
import os
import wave
import pydub
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import random
from pydub.playback import play

class Merge_Manager:
    """
        mm controls how two cells merge together
    """
    def __init__(self):
        # define some hyper parameters here
        pass

    def merge(self, frame_num, cell_list):
        # merge two cells according to the propeties of both cells
        # read in all the sound files and each would get a portion from the others?
        # do not make it on squared, make it a constant cost --> it is okay for now to be slow but can optimize later
        print("merge cell")
        n = len(cell_list)
        for i in range(n):
            cur_cell = cell_list[i]
            l1 = len(cur_cell.sound)
            # access to the loaded sounds
            cur_sound = cur_cell.sound.try_load_sound()
            for j in range(n):
                if j == i:
                    continue
                other_cell = cell_list[j]
                # select a part from here
                l2 = len(other_cell.sound)
                # select a part to add to the previous sound
                other_sound = other_cell.sound.try_load_sound()
                # generate a position
                pos = random.randint(0, min(l1, l2) // 2)
                cur_sound = cur_sound.overlay(other_sound, pos, loop=False)

                ## add to the encounter list
                cur_cell.history_tracker.add(frame_num, other_cell)
            # update the current sound
            cur_cell.sound.set_modified_sound(cur_sound)

    def merge_sound(self, sound_a, sound_b):
        pass
