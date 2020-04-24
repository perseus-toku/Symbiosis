from typing import Dict, Tuple, Sequence
import numpy as np
import os

import wave
import pydub
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import random
from pydub.playback import play


# need some parameters to set up the maximum duration of sound
# processed sound folder

"""
    A class to store the sound object
"""


class Sound:
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

        # try not to load in the sound in the beginning, load the information dynamically
        self.loaded_sound = None

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
        if not self.loaded_sound:
            self.loaded_sound = AudioSegment.from_wav(self.sound_file)
            # truncate the sound file if necessary
            if len(self.loaded_sound) > self.max_duration * 1000:
                # truncate -- > randomly select a part
                s = random.randint(0, len(self.loaded_sound) - self.max_duration * 1000)
                self.loaded_sound = self.loaded_sound[s : s + self.max_duration * 1000]
        return self.loaded_sound

    def play_sound(self):
        # use pyaudio funcitons to play the sound --> use functions from util.py
        pass

    def __len__(self):
        # read in the sound object and get the length from it
        self.try_load_sound()
        # get the length of the audiosegment object
        return len(self.loaded_sound)

    def set_modified_sound(self, in_sound):
        self.loaded_sound = in_sound

    def play(self):
        ### should be able to play the sound without any io operations
        # loaded sound is an audio segment
        self.try_load_sound()
        play(self.loaded_sound)

    def export_sound(self, path=None):
        # save the sound to an output directory for play back --> then let a different function handle play back
        output_file_name = "check_sound.wav"
        self.loaded_sound.export(output_file_name, format="wav")


class CellHistoryTracker:
    """
        Tracks the encoutner history of a cell

    """

    def __init__(self):
        self.log = {}

    @property
    def total_number_of_encounter(self):
        return len(self.log)

    def add(self, frame_number, other_cell):
        # add the other cell's name to history
        if frame_number not in self.log:
            self.log[frame_number] = []
        # add to log
        self.log[frame_number].append(other_cell.name)

    def print_log(self):
        pass


class Cell:
    """
        A voice cell is a basic unit of life in the sb game
        the voice cell stores propety related to this single cell and provide functionalities to
        itneract with other cells

        The first step would be to create a single canvas(a grid) where the cells can be shown and can potentially interact

        Properties
        -----------
            sound: every cell has a sound object
            life_time: number of frames the cell can stay alive
            alive: indicator to show if the cell is alive --> dead cells are recollected
            N: canvas size
            color: color to display for the cell
            value: the value of existence of the cell

    """

    # loc: a tuple describing the x,y location of the cell
    def __init__(self, loc:Tuple[int,int], N: int, value: int, color:int=None, size=1, name:str=None):
        # what properties to have here ?
        # store the sound
        self.sound = Sound()
        # some nice propeties to have --> a cell shouldn't be alive forever
        self._life_time = 10000
        self.alive = True
        self._loc = loc
        # this is the size of the board
        self.N = N
        # self.last_move_prob = np.array([1/3.0,1/3.0,1/3.0])
        # should add some momentum to the game
        # need to store the history of encounter for this cell
        self._name = name
        self._value = value
        self.history_tracker = CellHistoryTracker()
        self._next_loc = None
        if not color:
            # random generate a color from [0..255]
            self.color = random.randint(125, 255)
        else:
            self.color = color

    @property
    def life_time(self):
        return self._life_time

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def loc(self):
        return self._loc

    @property
    def next_loc(self):
        return self._next_loc

    @next_loc.setter
    def next_loc(self, next_loc:Tuple[int,int]):
        # check if the next move is bounded
        if not 0<=next_loc[0]<=self.N and 0<=next_loc[1]<=self.N:
            raise ValueError(f"next move {next_loc} is out of bound in a {self.N} board")
        self._next_loc = next_loc

    def get_next_loc(self):
        # instead let the board compute next state
        # delegate the next move generation to the cell it self with the knowledge of the board?
        # randomly samole a direction with the knowledge of the board
        # just mvoe four dirs
        MOVES = [1, 0, -1]
        # get some drifts to the next step --> make it random noise
        # update last probabily with momentum

        def move_valid(xm, ym):
            # check if the input move is valid
            x = self._loc[0] + xm
            y = self._loc[1] + ym
            return 0 <= x < self.N and 0 <= y < self.N

        move = np.random.choice(MOVES, 2, replace=True)
        while not move_valid(move[0], move[1]):
            # sampel a new move from here
            move = np.random.choice(MOVES, 2, replace=True)

        # update last probability
        new_loc = (self._loc[0] + move[0], self._loc[1] + move[1])
        # update the current location
        self._loc = new_loc

        return self._loc

    def evolve(self):
        # the cell object should know how and when to evolve
        pass

    @property
    def history(self):
        return self.history_tracker


"""
    mm controls how two cells merge together
"""


class Merge_Manager:
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


def _test_sound_merge_between_two_cells():
    # initialize two cells
    A = Cell((0, 0), 10, 10)
    B = Cell((0, 0), 10, 10)
    print(A.sound.sound_file)
    print(B.sound.sound_file)

    A.sound.play()
    B.sound.play()
    print("play a ")

    mm = Merge_Manager()
    mm.merge([A, B])
    print("play after ")
    A.sound.play()


if __name__ == "__main__":
    # do some testing here to see things work as expected
    # c = Cell((0,0),100)
    # print(c.get_next_loc())
    # rand_prob = np.random.rand(2)
    # print(rand_prob)
    _test_sound_merge_between_two_cells()
