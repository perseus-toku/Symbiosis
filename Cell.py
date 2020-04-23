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
                s = random.randint(0, len(self.loaded_sound)-self.max_duration * 1000)
                self.loaded_sound = self.loaded_sound[s: s+self.max_duration * 1000]
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





class Cell:
    """
        A voice cell is a basic unit of life in the sb game
        the voice cell stores propety related to this single cell and provide functionalities to
        itneract with other cells

        The first step would be to create a single canvas(a grid) where the cells can be shown and can potentially interact


    """

    # loc: a tuple describing the x,y location of the cell
    def __init__(self, loc, N, color=None, size=1, name=None):
        # what properties to have here ?
        # store the sound
        self.sound = Sound()
        # some nice propeties to have --> a cell shouldn't be alive forever
        self.life_time = 10000
        self.alive = True
        self.loc = loc
        # this is the size of the board
        self.N = N

        if not color:
            # random generate a color from [0..255]
            self.color = random.randint(125, 255)
        else:
            self.color = color

        # self.last_move_prob = np.array([1/3.0,1/3.0,1/3.0])
        # should add some momentum to the game
        # need to store the history of encounter for this cell
        self.encounter_history = []
        self.name = name

    def get_next_move(self):
        # delegate the next move generation to the cell it self with the knowledge of the board?
        # randomly samole a direction with the knowledge of the board
        # just mvoe four dirs
        MOVES = [1, 0, -1]
        # get some drifts to the next step --> make it random noise
        # update last probabily with momentum

        def move_valid(xm, ym):
            # check if the input move is valid
            x = self.loc[0] + xm
            y = self.loc[1] + ym
            return 0 <= x < self.N and 0 <= y < self.N

        move = np.random.choice(MOVES, 2, replace=True)
        while not move_valid(move[0], move[1]):
            # sampel a new move from here
            move = np.random.choice(MOVES, 2, replace=True)

        # update last probability
        new_loc = (self.loc[0] + move[0], self.loc[1] + move[1])
        # update the current location
        self.loc = new_loc

        return self.loc

    def evolve(self):
        # the cell object should know how and when to evolve
        pass

    @property
    def history(self):
        return self.encounter_history

"""
    mm controls how two cells merge together
"""


class Merge_Manager:
    def __init__(self):
        # define some hyper parameters here
        pass

    def merge(self, cell_list):
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
                cur_cell.encounter_history.append(other_cell.name)
            # update the current sound
            cur_cell.sound.set_modified_sound(cur_sound)

    def merge_sound(self, sound_a, sound_b):
        pass


def _test_sound_merge_between_two_cells():
    # initialize two cells
    A = Cell((0, 0), 10)
    B = Cell((0, 0), 10)
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
    # print(c.get_next_move())
    # rand_prob = np.random.rand(2)
    # print(rand_prob)
    _test_sound_merge_between_two_cells()
