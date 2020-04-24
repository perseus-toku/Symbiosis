import os
import shutil

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import random

# custom import
from Cell import Cell
from Sound import Sound
from MergeManager import Merge_Manager

import logging
# just print to the terminal for now
logging.basicConfig(level=logging.DEBUG)


# some very useful sources
# http://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/

## create a visulizaiton image for the game

# some plt configurations
plt.style.use("dark_background")

# create a wrapper for logging utilities
def args_to_string(*argv):
    s = []
    for arg in argv:
        s.append(str(arg))
    return " ".join(s)


class Engine:
    """
        The engine is the driver to run the game it initializes the state and keeps track of the progress
        # should also have access to the current state of the game


        # actually save the file so that the main loop is non blocking and the music playing will be handled by a different folder
        # for example, do not play in memory, save the audio files and play back in disk

    """

    def __init__(self, num_of_cells=1, N=5, run_without_display=False, universe_life_time=100):
        self.num_of_cells = num_of_cells
        # maintaining a list of cells ???
        # and run update one by one ?

        ## keep a location map to save the locations of the cells
        # this also enables checking for overlap
        self.location_map = {}
        # keeps track of locations where contact happens for special highlight
        self.merge_locations = []

        self.N = N
        self.mm = Merge_Manager()

        # we want to play the sound of cells in the trace list
        self.trace_list = ["0"]

        # a dead cell cannot be reinvented
        self.dead_cells = []
        self.output_dir = "engine_outputs"
        self.run_without_display = run_without_display
        self.universe_life_time = universe_life_time

    def get_cell_by_name(self, name):
        # return the cell associated with the given name
        # return None if no match
        if type(name) != str:
            raise ValueError("Cell name should be a string")
        for clist in self.location_map.values():
            for c in clist:
                if c.name == name:
                    return c
        return None

    def _make_loc_key(self, x, y):
        return f"{x}:{y}"

    def _decode_loc_key(self, s):
        x, y = int(s.split(":")[0]), int(s.split(":")[1])
        return x, y

    def initilize_cells(self):
        for i in range(self.num_of_cells):
            # initialize cells
            # randomly generate initial location
            x, y = random.randint(0, self.N - 1), random.randint(0, self.N - 1)
            # logging.debug(x,y)
            # initiaze a value
            value = random.randint(0, 10)
            if i == 0:
                value = 100
            # find a way to initialize life time reasonably
            life_time = random.randint(0, 1000)
            c = Cell((x, y), self.N, value=value, name=str(i), life_time = life_time)

            k = self._make_loc_key(x, y)
            if k not in self.location_map:
                self.location_map[k] = []
            # append the cell to the location map
            self.location_map[k].append(c)

    def get_grid_from_loc_map(self):
        # grid is arranged by row and then column
        # generate the grid from location map, simply creating a 2d grid
        # we jsut need the keys
        locs = self.location_map.keys()
        # build a new grid
        grid = np.zeros(self.N * self.N).reshape(self.N, self.N)
        for l in locs:
            loc_color = min(255, sum([c.color for c in self.location_map[l]]))
            # decode the key object
            x, y = self._decode_loc_key(l)
            # allow customized color values for each cell
            grid[x][y] = loc_color
        return grid

    # def _encode_location_str(self, s):
    #     x, y = int(l.split(":")[0]), int(l.split(":")[1])
    #     return x,y

    def _global_get_next_move(self, frameNum):
        # can also try 2d normal map to add to the probability
        # with global information, sample the next move for each cell, store next move to each cell
        # go through the cell list
        new_location_map = {}
        prob = {"UP": 0.0, "DOWN": 0.0, "LEFT": 0.0, "RIGHT": 0.0}
        MOVES = ["UP", "DOWN", "LEFT", "RIGHT"]

        def clear_prob(prob):
            for k in prob:
                prob[k] = 0
            return prob

        def normalize_prob(prob):
            total = sum(prob.values())
            if total == 0:
                # the case that nothing is set
                for k in prob:
                    prob[k] = 0.25
            else:
                for k in prob:
                    prob[k] = prob[k] / total

            # also inject in some randomness
            random_ratio = 0.8
            for k in prob:
                prob[k] = (1-random_ratio)*prob[k] + random_ratio*0.25

            return prob

        def get_next_move(prob, x, y):
            next_pos = np.random.choice(MOVES, 1, p=list(prob.values()))
            # copy the original posiiton
            x_new, y_new = x, y
            if next_pos == "UP":
                x_new -= 1
            elif next_pos == "DOWN":
                x_new += 1
            elif next_pos == "LEFT":
                y_new -= 1
            elif next_pos == "RIGHT":
                y_new += 1
            return x_new, y_new

        ############## clean dead cells --> dead cells can still add to the location weight
        for cell in [c for l in self.location_map.values() for c in l]:
            if cell.life_time <= frameNum:
                logging.debug(f"cell {cell.name} dies on round {frameNum}")
                # the cell should be dead
                cell.alive = False
                self.dead_cells.append(cell)
                continue
            else:
                # the cell is still alive
                x, y = cell.loc
                # update sampling probability, cells in same loc won't add to the probability
                for k in self.location_map:
                    xp, yp = self._decode_loc_key(k)

                    # get total value in this position
                    total_value = sum([c.value for c in self.location_map[k]])

                    # compute probability
                    if xp > x:
                        prob["DOWN"] += total_value
                    elif xp < x:
                        prob["UP"] += total_value
                    # check left and right
                    if yp > y:
                        prob["RIGHT"] += total_value
                    elif yp < y:
                        prob["LEFT"] += total_value
                prob = normalize_prob(prob)
                # sample the next move

                x_new, y_new = get_next_move(prob, x, y)
                while not (0 <= x_new < self.N and 0 <= y_new < self.N):
                    x_new, y_new = get_next_move(prob, x, y)

                logging.debug(args_to_string(prob, x_new, y_new))
                # update the location of the map
                cell.loc = (x_new, y_new)
                # can create a new self.locaiton map
                new_k = self._make_loc_key(x_new, y_new)
                if new_k not in new_location_map:
                    new_location_map[new_k] = []
                new_location_map[new_k].append(cell)
            logging.debug("---"*10)


        # update location map
        self.location_map = new_location_map
        logging.debug(f"loc map  {self.location_map}")

    def _global_check_overlapping(self, frameNum):
        # we have the new merge manager here, dead cells are no longer shown
        # clear the merge locations
        self.merge_locations = []
        for k in self.location_map:
            if len(self.location_map[k]) >= 2:
                # call the merge manage to update the cells
                # python oeprations will be in place
                self.mm.merge(frameNum, self.location_map[k])
                x, y = self._decode_loc_key(k)
                self.merge_locations.append([x, y])
        # there are two cells in this
        # randomly select two and make a merge?
        # should give birth to a new cell here? -->let the merge manager control

    def _global_finalize(self, frameNum):
        # do what ever clean up that we have to do here
        # logging.debug the position log
        for k in self.location_map:
            for c in self.location_map[k]:
                pos_log = c.history_tracker.get_position_log()
                logging.debug(f"name is {c.name}-- pos log is {pos_log}")


    def _global_save_current_frame(self, frameNum):
        # it is import to have a method to save all the running sounds in this frame
        # recreate output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.mkdir(self.output_dir)
        log_path = os.path.join(self.output_dir, "log.txt")
        with open(log_path, "w") as f:
            f.write("log")
        for k in self.location_map:
            for c in self.location_map[k]:
                # get the sound
                fname = os.path.join(self.output_dir, c.name + ".wav")
                c.save_sound_to_path(fname)

    def _engine_update_frame(self, frameNum):
        # move all cells
        self._global_get_next_move(frameNum)
        # use the merge function
        self._global_check_overlapping(frameNum)

        # finalize on the last frame
        if frameNum == self.universe_life_time-1:
            self._global_finalize(frameNum)

    def animation_update(self, frameNum, img, grid, ax):
        # update the current canvas by running evolution for each object
        # call to update the current frame
        self._engine_update_frame(frameNum)
        # get the new grid
        new_grid = self.get_grid_from_loc_map()
        # logging.debug(f"updated frame is {new_grid}")
        img.set_data(new_grid)

        # somehow, we have to clear the ax and draw again --> the animation process is quite manual
        # need to figure out how to better utilize the lib call, presumbly that is faster
        ax.clear()
        ax.set_xlabel(frameNum)

        # draw the merge locations
        for x, y in self.merge_locations:
            ax.scatter(y, x, marker="*", c="r", s=500)

        # turn off the values on the axis
        # ax.get_yaxis().set_visible(False)
        # ax.get_xaxis().set_visible(False)
        #
        ax.set_title("WELCOME TO THE SYMBIOSIS WORLD")
        ax.imshow(new_grid, interpolation="nearest")

        return (img,)

    def play_music(self, path):
        """ The engine will handle music player --> cell just save the music and
            The sound can be played at any time

            potentially allow sound playing to be managed by a different thread
        """
        # define stream chunk
        chunk = 1024
        # open a wav format music
        logging.debug(f"open path:{path}")
        f = wave.open(path, "rb")
        # instantiate PyAudio
        p = pyaudio.PyAudio()
        # open stream
        stream = p.open(
            format=p.get_format_from_width(f.getsampwidth()),
            channels=2,
            rate=f.getframerate(),
            output=True,
        )
        # read data
        data = f.readframes(chunk)
        # play stream
        while data:
            stream.write(data)
            data = f.readframes(chunk)

        # stop stream
        stream.stop_stream()
        stream.close()
        # close PyAudio
        p.terminate()

    def run(self):
        ## hyper parameters initialized here
        # initialize cells
        self.initilize_cells()

        updateInterval = 100
        # initialize the grid here
        grid = self.get_grid_from_loc_map()
        # logging.debug(f"initial grid is : {grid}")

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.set_tight_layout(True)
        # fig.set_title("symbiosis")

        img = ax.imshow(grid, interpolation="nearest")
        img.set_data(grid)

        ani = animation.FuncAnimation(
            fig,
            self.animation_update,
            fargs=(img, grid, ax),
            frames=self.universe_life_time,
            interval=updateInterval,
            blit=False,
            save_count=50,
            repeat=False,
        )
        # plt.grid(True)
        plt.show(block=True)


if __name__ == "__main__":
    e = Engine(3, 10, run_without_display=True, universe_life_time=100)
    e.run()
