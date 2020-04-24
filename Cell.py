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

from Sound import Sound


# need some parameters to set up the maximum duration of sound
# processed sound folder
class CellHistoryTracker:
    """
        Tracks the encoutner history of a cell

    """

    def __init__(self):
        self.encounter_log = {}
        self.position_log = []

    @property
    def total_number_of_encounter(self):
        return len(self.encounter_log)

    def add_encounter(self, frame_number, other_cell):
        # add the other cell's name to history
        if frame_number not in self.encounter_log:
            self.encounter_log[frame_number] = []
        # add to log
        self.encounter_log[frame_number].append(other_cell.name)

    def add_pos(self, loc):
        self.position_log.append(loc)

    def get_position_log(self):
        return self.position_log

    def print_log(self):
        pass


class Cell(object):
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
    def __init__(self, loc:Tuple[int,int], N: int, value: int, color:int=None, size=1, name:str=None, life_time=100):
        # what properties to have here ?
        # store the sound
        self.sound = Sound()
        # some nice propeties to have --> a cell shouldn't be alive forever
        self._life_time = life_time
        self.alive = True
        # this is the size of the board
        self._loc = loc 
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

    @loc.setter
    def loc(self, next_loc:Tuple[int,int]):
        # check if the next move is bounded
        if not 0<=next_loc[0]<=self.N and 0<=next_loc[1]<=self.N:
            raise ValueError(f"next move {next_loc} is out of bound in a {self.N} board")
        # record the moves this cell take
        self._loc = next_loc
        # add to the position log
        self.history_tracker.add_pos(next_loc)

    # def get_next_loc(self):
    #     # instead let the board compute next state
    #     # delegate the next move generation to the cell it self with the knowledge of the board?
    #     # randomly samole a direction with the knowledge of the board
    #     # just mvoe four dirs
    #     MOVES = [1, 0, -1]
    #     # get some drifts to the next step --> make it random noise
    #     # update last probabily with momentum
    #
    #     def move_valid(xm, ym):
    #         # check if the input move is valid
    #         x = self._loc[0] + xm
    #         y = self._loc[1] + ym
    #         return 0 <= x < self.N and 0 <= y < self.N
    #
    #     move = np.random.choice(MOVES, 2, replace=True)
    #     while not move_valid(move[0], move[1]):
    #         # sampel a new move from here
    #         move = np.random.choice(MOVES, 2, replace=True)
    #
    #     # update last probability
    #     new_loc = (self._loc[0] + move[0], self._loc[1] + move[1])
    #     # update the current location
    #     self._loc = new_loc
    #
    #     return self._loc

    def evolve(self):
        # the cell object should know how and when to evolve
        pass

    @property
    def history(self):
        return self.history_tracker

    def save_sound_to_path(self, path):
        self.sound.save_sound(path)


# def _test_sound_merge_between_two_cells():
#     # initialize two cells
#     A = Cell((0, 0), 10, 10)
#     B = Cell((0, 0), 10, 10)
#     print(A.sound.sound_file)
#     print(B.sound.sound_file)
#
#     A.sound.play()
#     B.sound.play()
#     print("play a ")
#
#     mm = Merge_Manager()
#     mm.merge([A, B])
#     print("play after ")
#     A.sound.play()
#
#
# if __name__ == "__main__":
#     # do some testing here to see things work as expected
#     # c = Cell((0,0),100)
#     # print(c.get_next_loc())
#     # rand_prob = np.random.rand(2)
#     # print(rand_prob)
#     _test_sound_merge_between_two_cells()
