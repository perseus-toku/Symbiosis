import numpy as np
from PIL import Image, ImageTk
import os
import sys
import random


# use pyaudio
import wave
import pydub
from pydub import AudioSegment
from pydub.playback import play
import pyaudio


if (
    sys.version_info[0] == 2
):  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter

    tkinter = Tkinter  # I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter


RAW_SOUND_PATH = "sound_inputs"
BASE_SCENE_FOLDER = "scene_inputs"
PROCESSED_SOUND_PATH = "processed_sound_inputs"


# some good reference for pydub is https://medium.com/better-programming/simple-audio-processing-in-python-with-pydub-c3a217dabf11


def play_music(path):
    # define stream chunk
    chunk = 1024
    # open a wav format music
    print(f"open path:{path}")
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


def join_wavs(waves):
    combined = None
    for w in waves:
        try:
            pw = AudioSegment.from_wav(w)
        except Exception as e:
            print(f"{w} is problematic")
            continue

        if not combined:
            combined = pw
        else:
            try:
                ### should add some variaty as where to mix in
                print(f"track length is {len(pw)}")
                print(f"mixed track length is {len(combined)}")
                # mix to random posiiton of the combined
                lb = len(combined)
                pos = random.randint(0, lb // 2)
                print(f"mix at position {pos}")
                combined = combined.overlay(pw, loop=True, position=pos)
            except Exception as e:
                print(f"{w} is problematic")

    # more complicated join logic can be implemented later

    # export to local
    output_file_name = "mixed_sound.wav"
    combined.export(output_file_name, format="wav")
    play_music(output_file_name)


def process_sound_inputs():
    if not os.path.exists(PROCESSED_SOUND_PATH):
        os.mkdir(PROCESSED_SOUND_PATH)
    processed_files = [
        file for file in os.listdir(PROCESSED_SOUND_PATH) if "wav" in file
    ]
    for file in os.listdir(RAW_SOUND_PATH):
        if file not in processed_files and "wav" in file:
            # need to process file first
            orig_path = os.path.join(RAW_SOUND_PATH, file)
            dest_path = os.path.join(PROCESSED_SOUND_PATH, file)
            cmd = f"sox {orig_path} -b 16 -e signed-integer {dest_path}"
            print(cmd)
            os.system(cmd)
    print("complete processing raw sound inputs")


def construct_scene():
    pass


def installation():
    os.system("brew install ffmpeg")


def select_waves():
    max_num = 5
    files = []
    for file in os.listdir(PROCESSED_SOUND_PATH):
        if "wav" in file:
            files.append(os.path.join(PROCESSED_SOUND_PATH, file))

    selected = np.random.choice(files, max_num, replace=False)
    print(f"selected {selected}")
    return selected


def showPIL(pilImage):
    pilImage = Image.open(pilImage)
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root, width=w, height=h)
    canvas.pack()
    canvas.configure(background="black")
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w / imgWidth, h / imgHeight)
        imgWidth = int(imgWidth * ratio)
        imgHeight = int(imgHeight * ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)
    print("got to this step")
    image = ImageTk.PhotoImage(pilImage.convert("RGB"))

    imagesprite = canvas.create_image(w / 2, h / 2, image=image)

    gmail = tkinter.Label(root, image=image)
    gmail.pack()

    print("showing image")
    root.mainloop()


### should start a web server to show the constructed scenes


if __name__ == "__main__":
    process_sound_inputs()
    sel_waves = select_waves()
    join_wavs(sel_waves)
    play_music("modified_audio.wav")
