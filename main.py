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
        self._weekday = date.today().strftime("%A")

    def get_date(self):
        """Returns the current date."""
        return self._date

    def get_weekday(self):
        """Returns the current day of the week."""
        return self._weekday

    def get_last_entry(self):
        """Returns the most recent diary entry, or None if there are
        no entries."""
        if not self._entries:
            return None

        return self._entries[-1]

    def update_diary(self):
        last_update = self.get_last_entry()
        if last_update is None:
            return

        last_date = last_update["date"]
        if last_date != self._date:
            self.catch_up()

        date = self._date
        weekday = self._weekday
        file = self.upload_file()
        summary = self.get_summary_from_user()
        happiness = int(input("Please enter today's happiness score: "))
        self._entries.append({"date": date,
                              "weekday": weekday,
                              "file": file,
                              "summary": summary,
                              "happiness": happiness})

    def catch_up(self):
        pass

    def upload_file(self):
        pass

    def get_summary_from_user(self):
        pass


if __name__ == '__main__':
    test = Diary()
