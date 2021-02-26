# Author: Colin Joss
# Last date updated: 2-15-2021
# Description: A simple python program for my personal diary system, made with the intention to
#              speed up the process of maintaining it.

import datetime
import json
import os
import inquirer
from mutagen.mp3 import MP3
import math
import csv
from pyfiglet import Figlet
import calendar
import pandas as pd


class Diary:
    def __init__(self):
        with open("diary-data.csv", "r", newline="") as infile:
            data = csv.reader(infile)
            self._entries = []
            for row in data:
                self._entries.append(row)

        self.title()
        self.calendar()
        self.main_menu()

    @staticmethod
    def title():
        """Displays the title of the program."""
        custom_fig = Figlet(font='slant')
        print(custom_fig.renderText('AUTO - DIARY'))
        print("Program by Colin Joss")
        print("-----------------------------------------\n")

    @staticmethod
    def calendar():
        """Displays the current calendar."""
        date = datetime.date.today().strftime("%B %d %Y")
        weekday = datetime.date.today().strftime("%A")
        print(f"Today is {weekday} {date}\n")
        year = datetime.date.today().year
        month = datetime.date.today().month
        print(calendar.month(year, month))

    def main_menu(self):
        """Presents a main menu to the user in the terminal."""
        close_program = False
        while close_program is False:
            selection = self.list_selection(["Update", "Search", "Close"])

            # Prompts user through the diary updating process
            if selection == "Update":
                # self.update_diary()

            # Prompts user to search and returns a csv with the results
            elif selection == "Search":
                keyword = str(input("Enter a search term: "))
                # results = self.search_by_keyword(keyword)
                # self.create_search_csv(keyword, results)

            # Exits, saves, and updates the yearly csv and stats csv
            else:
                close_program = True
                # self.save_to_json()
                # self.update_yearly_csv(self.get_last_entry())
                # self.update_statistics_csv(self.get_last_entry())
                print("Goodbye!")

    def update_diary(self):
        """Records new diary entry(s)."""
        today = self.get_current_date()
        last_entry = self.get_last_date_updated()

        # catch_up to update the missing entries first
        if last_entry != today:
            missing_days = self.get_missing_entry_dates(last_entry, today)
            self.catch_up(missing_days)
            selection = self.list_selection(["Yes", "No"], "Would you like to skip today?")
            if selection == "Yes":
                return True

        entry = self.new_entry(self.get_current_date(), self.get_current_weekday())
        self.append_to_csv(entry)

    @staticmethod
    def get_missing_entry_dates(last_entry, today):
        missing = []
        one_less_day = None
        less = 1
        while one_less_day != last_entry:  # Processes the missing entries between the last update and current day
            one_less_day = today - datetime.timedelta(days=less)
            missing.append(one_less_day)
            less += 1

        return missing.reverse()

    def catch_up(self, missing_days):
        """If update_diary determines the current date and the last date the diary was updated
        don't match, catch_up is called to prompt the user to update for multiple previous days."""
        print('You need to catch up on some days! Update these first. \n')
        for day in missing_days:   # Cycles through the missing entries, prompting user to update them
            date = str(day)
            weekday = day.strftime('%A')
            entry = self.new_entry(date, weekday)
            self.append_to_csv(entry)

    def new_entry(self, date, weekday):
        """Prompts the user through the components of a diary entry, and
        then adds the entry to the list of all entries."""
        date = date
        weekday = weekday
        summary = self.get_summary_from_user(date, weekday)
        happiness = self.get_happiness_from_user()
        duration = self.get_mp3_file_length()
        people = self.get_people_from_user()

        return [date, weekday, summary, happiness, duration, people]

    def search_by_keyword(self, keyword):
        """Accepts a search keyword and returns a list of matches."""
        matches = []
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if entry["summary"] is None or isinstance(entry["summary"], str) is False:
                        continue
                    elif keyword.lower() in entry["summary"].lower():
                        matches.append(entry)
        return matches

    @staticmethod
    def create_search_csv(keyword, matches):
        """Creates a csv file based on search results."""
        if not matches:
            return print("No results.\n")

        with open(f"{keyword.lower()}_{datetime.date.today()}.csv", "w", newline="") as infile:
            csv_writer = csv.writer(infile)

            rows = [["Date", "Weekday", "Summary", "Happiness", "File length", "People"]]
            for entry in matches:   # Formats all search match entries for display in a csv file
                row = [entry["date"], entry["weekday"], entry["summary"],
                       entry["happiness"], entry["length"]]
                row += entry["people"]
                rows.append(row)

            csv_writer.writerows(rows)
        return print("Search results successfully generated!\n")

    def edit_entry(self, entry):
        """Take an entry and prompts the user through editing parts or all of it."""
        selection = self.list_selection(["summary", "happiness", "people", "cancel"],
                                        "Which part do you want to edit?")
        print(entry[selection])
        if selection == "summary":
            entry[selection] = self.get_summary_from_user(entry["date"], entry["weekday"])
        elif selection == "happiness":
            entry[selection] = self.get_happiness_from_user()
        elif selection == "people":
            entry[selection] = self.get_people_from_user()
        else:
            return

    def save_to_json(self):
        """Records entry data to json."""
        with open("save_data.json", "w") as outfile:
            all_data = [self._entries]
            json.dump(all_data, outfile)

    def update_yearly_csv(self, last_entry):
        """Creates a spreadsheet and saves the most updated year data to it."""
        year = self.get_current_year()
        if last_entry is None:
            return None
        if str(year) not in last_entry["date"]:
            return None

        with open(f"{year}.csv", "w", newline="") as infile:
            csv_writer = csv.writer(infile)

            rows = [["Date", "Weekday", "Summary", "Happiness", "File length", "People"]]
            for month in self._entries[str(year)]:
                for entry in self._entries[str(year)][month]:
                    row = [entry["date"], entry["weekday"], entry["summary"],
                           entry["happiness"], entry["length"]]
                    row += entry["people"]
                    rows.append(row)

            csv_writer.writerows(rows)
        return print("Yearly spreadsheet successfully updated.\n")

    def update_statistics_csv(self, last_entry):
        """Automatically calculates a set of statistics from my diary and
        organizes it in a csv."""
        if last_entry is None:
            return None

        rows = [["GENERAL STATISTICS"],
                ["Entries: ", self.get_total_entries()],
                ["Files: ", self.get_total_files()],
                ["Sum file length: ", self.get_total_length()],
                [""]]

        years = [year for year in self._entries]
        rows.append(["YEARS RANKED"])
        h_year = self.get_happiest_year()
        for key in h_year:
            rows.append([key, h_year[key]])
        rows.append("")

        for year in years:
            h_month = self.get_happiest_month(year)
            h_week = self.get_happiest_weekday(year)
            m_people = self.get_most_mentioned_people(year)
            rows.append([f"MONTHS RANKED {year}", "", f"WEEKDAYS RANKED {year}", "", f"MOST MENTIONED {year}"])
            this_year = []
            for month in h_month:
                this_year.append([month, h_month[month]])

            index = 0
            for weekday in h_week:
                try:
                    this_year[index] += [weekday, h_week[weekday]]
                    index += 1
                except IndexError:
                    pass

            index = 0
            for person in m_people:
                try:
                    if index > 6:
                        continue
                    this_year[index] += [person, m_people[person]]
                    index += 1
                except IndexError:
                    pass

            for row in this_year:
                rows.append(row)
            rows.append([""])

        with open(f"statistics.csv", "w", newline="") as infile:
            csv_writer = csv.writer(infile)
            csv_writer.writerows(rows)

        return print("Statistics spreadsheet successfully updated.\n")

    # Getters and helpers --------------------------------------

    @staticmethod
    def append_to_csv(entry):
        with open('diary-data.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(entry)

    @staticmethod
    def get_current_date():
        """Returns the current date."""
        return datetime.date.today().strftime("%m/%d/%y")

    @staticmethod
    def get_current_weekday():
        """Returns the current day of the week as a string."""
        return datetime.date.today().strftime("%A")

    @staticmethod
    def get_current_month():
        """Returns the current month of the year as a string."""
        return datetime.date.today().strftime("%B")

    @staticmethod
    def get_current_year():
        """Returns the current year as a string."""
        return datetime.date.today().strftime("%Y")

    def get_last_date_updated(self):
        """Returns the most recent diary entry, or None if there are
        no entries."""
        return datetime.datetime.strptime(self._entries[-1][0], "%m/%d/%y")

    def get_total_entries(self):
        """Returns the total number of user-submitted entries."""
        count = 0
        for year in self._entries:
            for month in self._entries[year]:
                count += len(self._entries[year][month])
        return count

    def get_total_files(self):
        """Returns the total number of user-submitted files."""
        count = 0
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if entry["length"] is not None:
                        count += 1
        return count

    def get_total_length(self):
        """Calculates the sum total amount of recording time."""
        sum_in_seconds = 0
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if entry["length"] is None or entry["length"] == " ":
                        continue
                    hours, minutes, seconds = self.split_time(entry["length"])
                    hours = self.times_sixty(self.times_sixty(hours))
                    minutes = self.times_sixty(minutes)
                    sum_in_seconds += (hours + minutes + seconds)

        return self.convert_seconds_to_hms(sum_in_seconds)

    def get_mp3_file_length(self):
        """Prompts user to select an mp3 file and returns the length of
        the linked file if it is an mp3, but None if it is any other file type."""
        main_folder = os.getcwd()
        os.chdir(main_folder + "\\new-update-files")
        selection = self.list_selection(["No file"] + os.listdir(), "Which file?")
        if selection == "No file":
            os.chdir(main_folder)
            return None

        audio = MP3(main_folder + "\\new-update-files\\" + selection)
        length = audio.info.length
        hms_string = self.convert_seconds_to_hms(length)
        os.chdir(main_folder)
        return hms_string

    @staticmethod
    def convert_seconds_to_hms(seconds):
        """Accepts a number of seconds and returns a string of the time,
        with hours and minutes, divided by colons."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{math.floor(hours)}:{math.floor(minutes)}:{math.floor(seconds)}"

    @staticmethod
    def split_time(time):
        """Accepts a string formatted as "H:M:S:" and returns the hours,
        minutes, and seconds separately."""
        time_list = str(time).split(":")
        return int(time_list[0]), int(time_list[1]), int(time_list[2])

    @staticmethod
    def split_date(date):
        """Splits a hyphenated date into its year/month/day parts, and returns each as an int."""
        date_list = str(date).split("-")
        return int(date_list[0]), int(date_list[1]), int(date_list[2])

    @staticmethod
    def times_sixty(num):
        """Accepts a number and returns the product of it and 60."""
        return num * 60

    def check_new_year(self, year):
        """Checks if the current year is contained in self._entries, and if not, creates a new year."""
        if year not in self._entries:
            self._entries[year] = {}

    def check_new_month(self, year, month):
        """Checks if the current month is contained in self._entries, and if not, creates a new month."""
        if month not in self._entries[year]:
            self._entries[year][month] = []

    def get_happiest_year(self):
        """Returns a sorted dictionary of the happiest years and their averages."""
        happiness = {}
        for year in self._entries:
            happiness[year] = [0, 0]
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if entry["happiness"] is None:
                        continue
                    happiness[year][0] += entry["happiness"]
                    happiness[year][1] += 1

            if happiness[year][1] == 0:
                happiness[year] = 0
            else:
                happiness[year] = happiness[year][0] / happiness[year][1]

        return self.sort_dict_by_value(happiness, True)

    def get_happiest_month(self, year):
        """Returns a sorted dictionary of the happiest months
        (in a given year) and their averages."""
        happiness = {}
        for month in self._entries[year]:
            happiness[month] = [0, 0]
            for entry in self._entries[year][month]:
                if entry["happiness"] is None:
                    continue
                happiness[month][0] += entry["happiness"]
                happiness[month][1] += 1

            if happiness[month][1] == 0:
                happiness[month] = 0
            else:
                happiness[month] = happiness[month][0] / happiness[month][1]

        return self.sort_dict_by_value(happiness, True)

    def get_happiest_weekday(self, year):
        """Returns a dictionary of the happiest weekdays
        (in a given year) and their averages."""
        happiness = {"Sunday": [0, 0], "Monday": [0, 0], "Tuesday": [0, 0],
                     "Wednesday": [0, 0], "Thursday": [0, 0], "Friday": [0, 0],
                     "Saturday": [0, 0]}
        for month in self._entries[year]:
            for entry in self._entries[year][month]:
                if entry["happiness"] is None:
                    continue
                happiness[entry["weekday"]][0] += entry["happiness"]
                happiness[entry["weekday"]][1] += 1

        for weekday in happiness:
            if happiness[weekday][1] == 0:
                happiness[weekday] = 0
            else:
                happiness[weekday] = happiness[weekday][0] / happiness[weekday][1]

        return self.sort_dict_by_value(happiness, True)

    def get_most_mentioned_people(self, year):
        """Returns a sorted dictionary of mentioned people and
        their averages."""
        people = {}
        for month in self._entries[year]:
            for entry in self._entries[year][month]:
                for person in entry["people"]:
                    if person not in people:
                        people[person.title()] = 1
                    else:
                        people[person.title()] += 1

        return self.sort_dict_by_value(people, True)

    @staticmethod
    def get_summary_from_user(date, weekday):
        """Prompts the user through a detailed summary for a given date."""
        print(f"This is the summary for {weekday}, {date}.")
        print("Remember to be as detailed as possible - and to use as many "
              "KEYWORDS as you can! \n")
        morning = str(input("This morning, I... "))
        afternoon = str(input("In the afternoon, I... "))
        evening = str(input("During the evening, I... "))
        opinion = str(input("Overall, I'd say today was... "))

        summary = f"This morning, I {morning} In the afternoon, I {afternoon} " \
                  f"During the evening, I {evening} Overall, I'd say today was {opinion}"
        return summary

    def get_happiness_from_user(self):
        """Prompts users to select from a list of ratings and then returns that rating."""
        selection = self.list_selection([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                                        "How would you rate today?")
        return float(selection)

    def get_people_from_user(self):
        """Prompts users to input the names of people until they exit."""
        done = False
        count = 1
        people = []
        print("Please input all the names of people - first and last - who are noteworthy to this day.")
        while done is False:
            person = str(input(f"{count}: "))
            people.append(person)
            count += 1
            selection = self.list_selection(["Yes", "No"], "Add another name?")
            if selection == "No":
                done = True
        return people

    def get_year_from_user(self):
        """Prompts the user to input a valid year (contained within self._entries).
        Returns None if year is invalid."""
        year = str(input("Please input a year as a four-digit number: "))
        if len(year) != 4 or year not in self._entries:
            return None
        return year

    @staticmethod
    def sort_dict_by_value(my_dict, order):
        """Accepts a dictionary and returns the dictionary sorted by value."""
        return {k: v for k, v in sorted(  # Returns a new dictionary
            my_dict.items(),  # Selecting from the dictionary "happiness" as a list of tuples
            key=lambda pair: pair[1],  # Sorting according to the second item in the tuple, AKA the value
            reverse=bool(order))}  # Reversing because by default it sorts in ascending order

    def add_first_entry(self):
        self.new_entry(self.get_current_date(), self.get_current_weekday())

    @staticmethod
    def list_selection(choices, message=""):
        """Receives a list of choices and an optional message, and users the inquirer
        module to present those options to the user. Returns the user selection."""
        options = [
            inquirer.List('list',
                          message=message,
                          choices=choices
                          )]
        selection = inquirer.prompt(options)
        return selection["list"]

    def search_by_date(self, search_date):
        """Accepts a search date and returns a list of matches."""
        matches = []
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if search_date in entry["date"]:
                        matches.append(entry)
        return matches

    @staticmethod
    def convert_num_to_month(num):
        """Accepts a number between 1-12 and returns matching month, or None if no match."""
        month_list = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        if 1 <= num <= 12:
            return month_list[int(num) - 1]
        return None

    # Extra functions for top-secret highly dangerous dev use ---------------------------------

    def import_stats_from_csv(self, filepath):
        """Takes a csv file, and if the file is formatted properly,
        pulls requisite data to create diary entries."""
        file = csv.reader(open(filepath))  # Opens the given file
        rows = list(file)

        for row in rows:  # Cycles through the rows, pulling data
            date = row[0]
            year, month, day = self.split_date(date)
            weekday = datetime.date(year, month, day).strftime("%A")
            month = self.convert_num_to_month(month)

            summary = None
            if row[1] != "" and row[1] is not None:
                summary = row[1].strip()

            happiness = None
            if row[2] != "" and row[2] is not None:
                happiness = float(row[2])

            length = None
            if row[3] != "" and row[3] is not None:
                length = row[3]

            people = []
            try:  # Gathers list of relevant people, or handles if none
                i = 4
                while row[i]:
                    people.append(str(row[i]))
                    i += 1
            except IndexError:
                pass

            if str(year) not in self._entries:  # Creates correct dicts / lists if new year / month
                self._entries[str(year)] = {}
            if str(month) not in self._entries[str(year)]:
                self._entries[str(year)][str(month)] = []

            self._entries[str(year)][str(month)].append({  # Creates a new diary entry
                "date": date,
                "weekday": weekday,
                "summary": summary,
                "happiness": happiness,
                "people": people,
                "length": length
            })
        self.save_to_json()

    def remove_string_from_summary(self, string):
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if entry["summary"] is None or entry["summary"] == "":
                        continue
                    if string.lower() in entry["summary"].lower():
                        new_summary = entry["summary"].replace(string, "")
                        entry["summary"] = new_summary

    def find_and_replace(self, find, replace):
        """Finds a string and replaces it with a new string."""
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if entry["people"] is None:
                        continue
                    for name in entry["people"]:
                        name.replace(find, replace)


if __name__ == '__main__':
    diary = Diary()
