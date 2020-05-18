
from __future__ import unicode_literals
from __future__ import annotations
from typing import List

import youtube_dl
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

from selenium import webdriver
import time
import json
import numpy as np
import os
from pydub import AudioSegment

sns.set_style("whitegrid")

BASE_URL = 'https://freesound.org'

def dump_html(html):
    with open("html", "w") as f:
        f.write(html)


class SoundInfo(object):
    def __init__(self, name: str, href:str, duration:float, desc:str, tags: List[str],  sp_html=None):
        self._name = name
        self._href = href
        self._duration = duration
        self._sp_html = sp_html
        self._desc = desc
        self._tags = tags


    @property
    def name(self):
        return self._name

    @property
    def href(self):
        return self._href

    @property
    def duration(self):
        return self._duration

    @property
    def sp_html(self):
        return self._sp_html

    @property
    def desc(self):
        return self._desc

    @property
    def tags(self):
        return self._tags

    @property
    def download_link(self):
        return BASE_URL + self._href + "download"

    def __repr__(self):
        out = "----------------------\n"
        out += f"Name: {self.name}\nhref: {self.href}\nDuration: {self.duration}\nDescription: {self.desc}\ntags: {self.tags}\nDownload_link: {self.download_link}\n"
        out += "----------------------\n"
        return out

    def to_json(self):
        j = {'name':self.name, 'href':self.href,  'duration': self.duration,  'description': self.desc, 'tags': self.tags, 'download_link':self.download_link}
        return j




SOUND_LOG_PATH = "download_worker_logs/sound_catalog"
CRASH_LOG_PATH = "download_worker_logs/crash_log"

class Catalog_Worker:
    """worker class """
    def __init__(self, num_pages):
        if not os.path.exists("download_worker_logs"):
            os.mkdir("download_worker_logs")
        self.results = []
        self.num_pages = num_pages
        # create a logger --> load from prev
        # save in the process
        # load from crash log
        self.crash_log = {"next_page":1}
        self.next_page = 1
        if os.path.exists(CRASH_LOG_PATH):
            with open(CRASH_LOG_PATH, "r") as f:
                self.crash_log = json.load(f)

        self.next_page = self.crash_log["next_page"]

        # initialize the driver
        self.driver = webdriver.Chrome('./chromedriver')
        self.interval_save_buffer = False
    def get_page_link_with_num(self, num:int):
        assert num >= 0
        return f"https://freesound.org/search/?page={num}#sound"

    def run(self):
        #user name and password are symbiosis2020
        results = []
        user_name = "symbiosis2020"
        login_page = "https://freesound.org/home/login/?next=/search/"
        home_page = "https://freesound.org/search/"
        self.driver.get(login_page)
        # html = self.driver.page_source
        # elem = self.driver.find_element_by_css_selector('#my-id')
        # html = elem.get_attribute('innerHTML')

        # self.driver.find_element_by_id("Log In").click()
        self.driver.find_element_by_id("id_username").send_keys(user_name)
        self.driver.find_element_by_id("id_password").send_keys(user_name)
        self.driver.find_element_by_name("csrfmiddlewaretoken").submit()

        # get the html information
        # html = self.driver.page_source
        # self.driver.get("https://freesound.org/people/digitalgasim/sounds/415102/")
        # save the information

        # get to the next page
        for i in range(self.next_page,self.next_page+self.num_pages):
            buffer = []
            link = self.get_page_link_with_num(num = i)
            # go to the page
            print(f"go to page number=={i}")
            self.driver.get(link)
            cur_html = self.driver.page_source
            res = self.get_sounds_from_html(cur_html)
            buffer += res

            # append to the log
            self.crash_log["next_page"] = i+1
            # write the output
            with open(SOUND_LOG_PATH,"a") as f:
                # write the results json
                for r in buffer:
                    j = r.to_json()
                    f.write(json.dumps(j)+"\n")

            # save crash log
            with open(CRASH_LOG_PATH, "w") as f:
                json.dump(self.crash_log, f)

            if self.interval_save_buffer:
                # do not save all information
                self.results.extend(buffer)


    def get_sounds_from_html(self, html):
        results = []
        parsed_html = BeautifulSoup(html)
        blocks =  parsed_html.findAll("div", {"class": "sample_player"})

        for block in blocks:
            name = block.findAll("a",{"class": "mp3_file"})[0].text
            duration_line = block.findAll("span",{"class": "duration"})[0]
            duration = duration_line.text

            title_line = block.findAll("a",{"class": "title"})[0]
            assert len(title_line) == 1, "more than 1 title"
            href = title_line.get("href")

            desc_line = block.findAll("p",{"class": "description"})[0]
            desc = desc_line.text

            tags_line = block.findAll("ul",{"class": "tags"})[0]
            # get all tags
            all_tags = [l.text for l in tags_line.findAll("li")]

            si = SoundInfo(name, href, float(duration), desc, all_tags, parsed_html)

            results.append(si)

        return results


    # blocks = html.strip().split("<div class=\"metadata\">")
    # blocks should at least have 2


class Download_Worker:
    def __init__(self, num_to_download, output_dir="StreamSounds"):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        self.output_dir = output_dir
        self.num_to_download = num_to_download
        self.catalog = self.read_catalog()

        chromeOptions = webdriver.ChromeOptions()
        cwd = os.getcwd()
        out_path = os.path.join(cwd, output_dir)
        print(f"output path is {output_dir}")
        prefs = {"download.default_directory" : out_path}
        chromeOptions.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chromeOptions)

        #### download configurations
        self.min_duration = 20000
        self.max_duration = 30000
        self.shuffle = False


    @classmethod
    def read_catalog(self):
        catalog = []
        with open(SOUND_LOG_PATH, "r") as f:
            for line in f:
                j = json.loads(line)
                catalog.append(j)
        return catalog

    def run(self):
        # read crra
        user_name = "symbiosis2020"
        login_page = "https://freesound.org/home/login/?next=/search/"
        self.driver.get(login_page)
        # html = self.driver.page_source
        # elem = self.driver.find_element_by_css_selector('#my-id')
        # html = elem.get_attribute('innerHTML')

        # self.driver.find_element_by_id("Log In").click()
        self.driver.find_element_by_id("id_username").send_keys(user_name)
        self.driver.find_element_by_id("id_password").send_keys(user_name)
        self.driver.find_element_by_name("csrfmiddlewaretoken").submit()


        # filter the catalog
        selected = []
        for s in self.catalog:
            duration = s['duration']
            if self.min_duration <= duration <=self.max_duration:
                selected.append(s)
            if len(selected) >= self.num_to_download:
                break

        for i,j in enumerate(selected):
            link = j['download_link']
            self.driver.get(link)



def analyze_sound_catalog():
    cata = Download_Worker.read_catalog()
    durations = []
    for c in cata:
        seconds = c['duration']/1000
        durations.append(seconds)
    n = len(durations)
    mind = min(durations)
    maxd = max(durations)
    avgd = np.mean(durations)

    selected_duration = [s for s in durations if 20<=s <= 30]
    print(len(selected_duration))
    exit()
    print(f"collected {n} sounds, min duration is {mind}s, max duration is {maxd}s, average duration is {avgd}s")

    plt.title("sound catalog length analysis")
    sns.distplot(selected_duration, kde=False, rug=False);
    plt.xlabel("duration (seconds)")
    plt.ylabel("count")
    # plt.hist(selected_duration)
    plt.show()


# def remove_duplicates(path):
#     for os.




if __name__ == "__main__":
    # play_list_link = "https://www.youtube.com/user/dr0alexander"
    # download_link(play_list_link)
    # url = 'https://freesound.org/people/juanto9889/sounds/414875/download'
    # myfile = requests.get(url)
    # open('test.wav', 'wb').write(myfile.content)
    # exit()
    dworker = Download_Worker(200)
    dworker.run()
    # worker = Catalog_Worker(num_pages=9735)
    # worker.run()
    # analyze_sound_catalog()
