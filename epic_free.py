import requests
from selenium import webdriver
from threading import Thread,RLock
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import asyncio
import time
import discord


class Epic_Free(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.found = False
        self.close= "N"
        self.url = "https://www.epicgames.com/store/en-US/free-games"
        self.game = []
        self.gameTook = False
        self.error = ""
    def run(self):
        print("Running Epic free thread !")
        while True:
            self.waitTime()
            if self.close == "N":
                if self.found:
                    self.found = False
                    self.gameTook = False
                    self.game = []
                #wait 1 day
                time.sleep(3600*24)
            elif self.close == "A":
                #wait 10 hours
                time.sleep(3600*10)
            elif self.close == "Y":
                #wait 1hours
                time.sleep(3600)
            elif self.close == "F":
                if not self.found:
                    self.found = True
                    self.getGames()
                else:
                    time.sleep(60)
                # Found the good time to execute


    def waitThursday(self):
        return datetime.today().strftime("%A")=="Thursday"
    def waitWednesday(self):
        return datetime.today().strftime("%A")=="Wednesday"

    def wait14PM(self):
        today = datetime.today()
        today = today.strftime("%H")
        return int(today) >= 14

    def waitTime(self):
        if self.waitWednesday():
            self.close = "A"
        elif self.waitThursday():
            if self.wait14PM():
                self.close = "F"
            else:
                self.close = "Y"
        else:
            self.close = "N"
    def getGames(self):
        l = []
        try:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Firefox('.',options=options)
            driver.get(self.url)
            start = time.time()
            while True:
                try:
                    a = driver.find_element_by_class_name('css-1u5k6xy')
                    break
                except:
                    if time.time() - start > 60:
                        return None
                    pass

            i = driver.find_element_by_class_name('CardGrid-groupWrapper_e669488f')
            for j in i.find_elements_by_tag_name('a'):
                if j.get_attribute('href') != "https://www.epicgames.com/store/en-US/free-games":
                    link = j.get_attribute('href')
                    game = link.split('/')[-1]

                    k = i.find_element_by_tag_name('img')
                    img = k.get_attribute('src')
                    l.append((game,img,link))
            driver.close()
            self.game = l
            print('[+] found free game')
        except Exception as e:
            self.game = []
            self.error = e
            return None
