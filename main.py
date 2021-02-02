# Author: Colin Joss
# Last date updated: 2-1-2021
# Description: A simple python program for my personal diary system, made with the intention to
#              speed up the process of maintaining it.
from datetime import date
import json


class Diary:
    def __init__(self):
        with open("save_data.json", "r") as infile:
            data = json.load(infile)
            self._entries = data[0]
        self._date = date.today().strftime("%m-%d-%Y")
        self._day_of_the_week = date.today().strftime("%A")


if __name__ == '__main__':
    pass
