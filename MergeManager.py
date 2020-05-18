import numpy as np
import os
import wave
import pydub
from pydub import AudioSegment
from pydub.playback import play
import pyaudio
import random
from pydub.playback import play
import logging
from copy import deepcopy

from Music_downloader import Download_Worker

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


        # select based on value --> highest value choose first
        # p (x,y)-> prob to merge
        children = []

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
                cur_cell.history_tracker.add_encounter(frame_num, other_cell)
            # update the current sound
            cur_cell.sound.set_modified_sound(cur_sound)


            # returns a list of new born cells, [] if no merge happens
            return children
    def merge_sound(self, sound_a, sound_b):
        pass


    def merge_algorithm1(self):
        pass

def merge_algo1(s1,s2):
    print(len(s1),len(s2))
    song1 = deepcopy(s1)
    song2 = deepcopy(s2)
    if len(song2) < len(song1):
        # swap to make song1 the shorter one
        temp = song1
        song1 = song2
        song2 = temp
    # merge the two --> divided to k seconds
    # merge with the minimum duration
    l1 = len(song1)
    l2 = len(song2)
    # no need to shorten just divide by less units put on top some where
    # get the shorter one
    # randomly find a part to start with
    # find a sequencing part
    # sample first loc
    # sample a location for song1
    pos = random.randint(0,l2-l1)
    #add padding to song1
    song2_left = song2[:pos]
    song2_right = song2[pos+l1:]
    song2_middle = song2[pos:pos+l1]
    # merge the middle part
    assert len(song2_middle) == l1, "song2 middle length incorrect"
    assert len(song2_left) + len(song2_middle) + len(song2_right) == len(song2), f"{len(song2_left) + len(song2_middle) + len(song2_middle)} != {len(song2)}"

    k = 10
    # basic unit of division
    unit_length = l1 // k
    print(f"unit_length is {unit_length} --> total: {unit_length*k}")
    # selection basis
    s = [random.randint(0,3) for i in range(k)]
    print(s)
    # divide it to k sequences
    # creat a new audio segment
    song3 = None

    # probability to reverse the sound
    p_reverse = 0.3
    prob_reverse1 = np.random.uniform(0,1)
    prob_reverse2 = np.random.uniform(0,1)
    if prob_reverse1 <= p_reverse:
        song1 = song1.reverse()
    if prob_reverse2 <= p_reverse:
        song2 = song2.reverse()

    max_cross_fade = unit_length // 2
    for i in range(k):
        # sample a cross fade
        cross_fade = random.randint(0, max_cross_fade)
        # use the first slice
        six = (i)*unit_length
        eix = (i+1)*unit_length
        if s[i] == 0:
            # we can reverse the sound here
            if not song3:
                song3 = song1[six:eix]
            else:
                # use cross fade
                # song3+= song1[six:eix]
                song3 = song3.append(song1[six:eix],  crossfade = cross_fade)
        elif s[i] == 1:
            if not song3:
                song3 = song2_middle[six:eix]
            else:
                # song3+= song2_middle[six:eix]
                song3 = song3.append(song2_middle[six:eix], crossfade = cross_fade)

        elif s[i]==2:
            # overlay
            temp = song1[six:eix].overlay(song2_middle[six:eix], loop=True)
            if not song3:
                song3 = temp
            else:
                # play(temp)
                print("before",len(song3), len(temp))
                song3 = song3.append(temp, crossfade = cross_fade)
                print("after",len(song3))
        else:
            # increase the sample length
            if not song3:
                song3 = song1[six:eix].append(song2_middle[six:eix], crossfade = cross_fade)
            else:
                song3 = song3.append(song1[six:eix], crossfade = cross_fade).append(song2_middle[six:eix], crossfade = cross_fade)
    # song3 should stay the same length
    # assert len(song3) == len(song2_middle), f"output length wrong {len(song3)}, {len(song2_middle)}"
    # final crossfade parameter
    final_cf = min(cross_fade, len(song2_left), len(song2_right))//2
    out_song = song2_left.append(song3, crossfade=final_cf).append(song2_right, crossfade=final_cf)
    print(len(out_song))
    print("_"*10)
    return out_song


def load_k_songs(k):
    sdir = "processed_sound_inputs"
    files = []
    for file in os.listdir(sdir):
        if "wav" in file:
            files.append(os.path.join(sdir, file))
    selected = np.random.choice(files, k, replace=False)
    return selected

# need to make the increase and decrease


# make this a simulation
def algo1_evaluate(cur_id):
    if not os.path.exists("simulations"):
        os.mkdir("simulations")
    new_dir = f"simulations/{cur_id}"
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)

    max_duration = 30000 # in ms
    slist = load_k_songs(8)
    #first load all songs
    print(slist)
    loaded_s = []
    for s in slist:
        song = AudioSegment.from_wav(s)
        print(len(song)/1000.0)
        if len(song) > max_duration:
            song = song[:max_duration]
        loaded_s.append(song)


    # merge the songs one by one
    merged_song = loaded_s[0]
    error_count = 0
    for i,s in enumerate(loaded_s):
        try:
            song_path  = os.path.join(new_dir, f"{i}.wav")
            if i>0:
                # only merge after first one
                merged_song = merge_algo1(merged_song,s)
                # save every merge
            merged_song.export(song_path, format="wav")
        except Exception as e:
            error_count += 1
            print(f" error encountered --> continue")
    print(f"encountered {error_count} errors")
    # add fade in and fade out
    fade_in_seconds = 2
    fade_out_seconds = 3
    merged_song = merged_song.fade_in(fade_in_seconds*1000).fade_out(fade_out_seconds*1000)

    print(f"output length is {merged_song.duration_seconds}")
    # save the output
    merged_song.export("merge_algo1.wav", format="wav")

    # play(merged_song)

def test_combine_numerous_sougs():
    sdir = "processed_sound_inputs"
    files = []
    for file in os.listdir(sdir):
        if "wav" in file:
            files.append(os.path.join(sdir, file))
    # have a deterministic list of songs
    duration = 5000
    songs =[]
    for s in files:
        song = AudioSegment.from_wav(s)
        print(len(song)/1000.0)
        if len(song) < duration:
            continue
        if len(song) > duration:
            song = song[:duration]
        songs.append(song)

    basic = songs[0]
    for s in songs[1:10]:
        basic = basic.append(s)

    print(len(basic)/1000)
    play(basic)

def test_overlay_multiple():
    sdir = "processed_sound_inputs"
    files = []
    for file in os.listdir(sdir):
        if "wav" in file:
            files.append(os.path.join(sdir, file))
    # have a deterministic list of songs
    duration = 5000
    songs =[]
    for s in files:
        song = AudioSegment.from_wav(s)
        print(len(song)/1000.0)
        if len(song) < duration:
            continue
        if len(song) > duration:
            song = song[:duration]
        songs.append(song)

    basic = songs[0]
    for s in songs[4:10]:
        basic = basic.overlay(s)

    print(len(basic)/1000)
    play(basic)



def load_all_song_name_containing_tags(load_folder, tags):
    tag_map = get_sid_to_tags_map_from_catalog()
    # check processed sound folders
    # walk through the load_folder
    song_buffer = []
    for f in os.listdir(load_folder):
        # check if f is in the right format
        if f.count("__") != 2:
            continue
        sid = get_sid_from_file_name(f)
        if sid not in tag_map:
            continue
        stags = set(tag_map[sid])
        #check if two sets overlap
        overlap = bool(set(tags) & stags)
        if overlap:
            song_buffer.append(f)
    return song_buffer

def get_sid_from_file_name(name):
    s = name.split("__")
    sid = s[0]
    name = s[1]
    return sid + "-" + name



def get_sid_from_song_json(c):
    #iget id
    href = c['href']
    l = href.split("/")
    name, sid = l[2], l[-2]
    return sid +"-"+name


def get_sid_to_tags_map_from_catalog():
    cata = Download_Worker.read_catalog()
    tag_map = {}
    for c in cata:
        sid = get_sid_from_song_json(c)
        tags = c['tags']
        # make it a set to check overlapping
        tag_map[sid] = tags
        # print(sid)
    return tag_map



def get_id_from_sound_name(sound_name):
    # sound names are standardized as name
    if not "__" in name:
        return None


if __name__ == "__main__":
    # try to see how different merge methods produce
    # s1 = "processed_sound_inputs/animal-market.wav"
    # s2 = "processed_sound_inputs/149196__lmartins__asakusa-religious-cerimony.wav"
    # test_overlay_multiple()

    sb = load_song_name_containing_tags("processed_sound_inputs", ["shaker"])
    print(sb)
