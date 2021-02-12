# Author: Colin Joss
# Last date updated: 2-1-2021
# Description: A simple python program for my personal diary system, made with the intention to
#              speed up the process of maintaining it.
import datetime
import json
import os
import shutil
import inquirer
from mutagen.mp3 import MP3
import math
import csv
from pyfiglet import Figlet
import calendar

print("")

class Diary:
    def __init__(self):
        with open("save_data.json", "r") as infile:
            data = json.load(infile)
            self._entries = data[0]
            self.title()
            self.calendar()
            self.main_menu()

    def title(self):
        """Displays the title of the prgoram."""
        custom_fig = Figlet(font='slant')
        print(custom_fig.renderText('AUTO - DIARY'))
        print("Program by Colin Joss")
        print("-----------------------------------------\n")

    def calendar(self):
        """Displays the current calendar."""
        date = datetime.date.today().strftime("%B %d %Y")
        weekday = datetime.date.today().strftime("%A")
        print(f"Today is {weekday} {date}\n")
        year = datetime.date.today().year
        month = datetime.date.today().month
        print(calendar.month(year, month))

    def main_menu(self):
        """Presents a main menu to the user in the terminal."""
        done = False
        while done is False:
            selection = self.list_selection(["Update", "Search", "Edit", "Close"])
            if selection == "Update":
                self.update_diary()

            elif selection == "Search":
                keyword = str(input("Enter a search term: "))
                results = self.search_by_keyword(keyword)
                self.create_search_csv(keyword, results)
            elif selection == "Edit":
                print("YYYY-mm-dd")
                date = str(input("Enter the date of the entry you're editing: "))
                result = self.search_by_date(date)
                if result is None:
                    return print("No results.")
                self.edit_entry(result)
            else:
                done = True
                self.save_to_json()
                self.update_csv(self.get_last_entry())
                print("Goodbye!")

    def update_diary(self):
        """Records new diary entry(s)."""
        if not self._entries:                           # Handles first-ever entry
            self.add_first_entry()
            return

        last_date = self.get_last_entry()["date"]       # If the date of the last entry is not today, calls
        yesterday = self.get_current_date() - datetime.timedelta(days=1)
        if last_date != str(yesterday):                 # catch_up to update the missing entries first
            self.catch_up(last_date)

        year = self.get_current_year()                  # Creates a new year if new year
        if year not in self._entries:
            self._entries[year] = {}

        month = self.get_current_month()                # Creates a new month if new month
        if month not in self._entries[year]:
            self._entries[year][month] = []

        entry = self.new_entry(self.get_current_date(), self.get_current_weekday())
        self._entries[year][month].append(entry)        # Prompts user through entry, saves as dictionary

    def catch_up(self, last_date):
        """If update_diary determines the current date and the last date the diary was updated
        don't match, catch_up is called to prompt the user to update for multiple previous days."""
        match = False
        catch_up_days = []
        less = 1
        while match is False:
            one_less_day = datetime.date.today() - datetime.timedelta(days=less)
            if str(one_less_day) == last_date:
                match = True
            else:
                catch_up_days.append(one_less_day)
            less += 1

        catch_up_days.reverse()
        print("You need to catch up on some days! Update these first. \n")
        for day in catch_up_days:
            date = day
            year, month, day = self.split_date(date)
            weekday = datetime.date(year, month, day).strftime("%A")
            self.new_entry(date, weekday)

    def new_entry(self, date, weekday):
        """Prompts the user through the components of a diary entry, and
        then adds the entry to the list of all entries."""
        date = date
        weekday = weekday
        summary = self.get_summary_from_user(date, weekday)
        happiness = self.get_happiness_from_user()
        people = self.get_people_from_user(),
        length = self.get_mp3_file_length()
        return {"date": date,
                "weekday": weekday,
                "summary": summary,
                "happiness": happiness,
                "people": people,
                "length": length}

    def search_by_keyword(self, search_keyword):
        """Accepts a search keyword and returns a list of matches."""
        search_match = []
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    try:
                        if search_keyword.lower() in entry["summary"].lower():
                            search_match.append(entry)
                    except TypeError:
                        continue
                    except AttributeError:
                        continue

        return search_match

    def create_search_csv(self, search_keyword, search_match):
        """Creates a csv file based on search results."""
        if not search_match:
            return print("No results.\n")

        with open(f"{search_keyword.lower()}_{datetime.date.today()}.csv", "w", newline="") as infile:
            csv_writer = csv.writer(infile)

            rows = [["Date", "Weekday", "Summary", "Happiness", "File length", "People"]]
            for entry in search_match:
                row = [entry["date"], entry["weekday"], entry["summary"],
                       entry["happiness"], entry["length"]]
                row += entry["people"]
                rows.append(row)

            csv_writer.writerows(rows)
        return print("Search results successfully generated!\n")

    def edit_entry(self, entry):
        pass

    def save_to_json(self):
        """Records entry data to json."""
        with open("save_data.json", "w") as outfile:
            all_data = [self._entries]
            json.dump(all_data, outfile)

    def update_csv(self, last_entry):
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

    def get_current_date(self):
        """Returns the current date."""
        return datetime.date.today()

    def get_current_weekday(self):
        """Returns the current day of the week as a string."""
        return datetime.date.today().strftime("%A")

    def get_current_month(self):
        """Returns the current month of the year as a string."""
        return datetime.date.today().strftime("%B")

    def get_current_year(self):
        """Returns the current year as a string."""
        return datetime.date.today().strftime("%Y")

    def get_last_entry(self):
        """Returns the most recent diary entry, or None if there are
        no entries."""
        if not self._entries:
            return None

        entries = []
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    entries.append(entry)

        return entries[-1]

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

    def get_happiest_year(self):
        """Returns a sorted dictionary of the happiest years and their averages."""
        happiness = {}
        for year in self._entries:
            happiness[year] = [0, 0]
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    happiness[year][0] += entry["happiness"]
                    happiness[year][1] += 1
            happiness[year] = happiness[year][0] / happiness[year][1]

        return self.sort_dict_by_value(happiness, True)

    def get_happiest_month(self, year):
        """Returns a sorted dictionary of the happiest months
        (in a given year) and their averages."""
        happiness = {}
        for month in self._entries[year]:
            happiness[month] = [0, 0]
            for entry in self._entries[year][month]:
                happiness[month][0] += entry["happiness"]
                happiness[month][1] += 1
            happiness[month] = happiness[month][0] / happiness[month][1]

        return self.sort_dict_by_value(happiness, True)

    def get_happiest_weekday(self, year):
        """Returns a dictionary of the happiest weekdays
        (in a given year) and their averages."""
        happiness = {"Sunday": [0, 0], "Monday": [0, 0], "Tuesday": [0, 0],
                     "Wednesday": [0, 0], "Thursday": [0, 0], "Friday": [0, 0],
                     "Saturday": [0, 0]}
        for month in self._entries[year]:
            for entry in self._entries[month]:
                happiness[entry["weekday"]][0] += entry["happiness"]
                happiness[entry["weekday"]][0] += 1

        for weekday in happiness:
            happiness[weekday] = happiness[weekday][0] / happiness[weekday][1]

        return self.sort_dict_by_value(happiness, True)

    def get_entries_by_happiness(self, level, year=None, month=None):
        """Returns a list of entries by a given happiness level, limited by
        year or month, depending on what the user inputs."""
        days = []
        if year is None:  # If the user did not input a year, the function
            for year in self._entries:  # returns all matching entries available
                for month in self._entries[year]:
                    for entry in self._entries[year][month]:
                        if entry["happiness"] == level:
                            days.append(entry)

        elif month is None:  # If the user inputted a year but not a month, the
            for month in self._entries[year]:  # function returns all matching entries in that year
                for entry in self._entries[year][month]:
                    if entry["happiness"] == level:
                        days.append(entry)

        else:
            for entry in self._entries[year][month]:  # If the user inputted both a month and a year, the
                if entry["happiness"] == level:  # function returns all matching entries in that month
                    days.append(entry)

    def get_most_mentioned_people(self, year=None, month=None):
        """Returns a sorted dictionary of mentioned people and
        their averages."""
        people = {}
        if year is None:
            for year in self._entries:
                for month in self._entries[year]:
                    for entry in self._entries[year][month]:
                        for person in entry["people"]:
                            if person.title() not in people:
                                people[person.title()] = 1
                            else:
                                people[person.title()] += 1

        elif month is None:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    for person in entry["people"]:
                        if person not in people:
                            people[person.title()] = 1
                        else:
                            people[person.title()] += 1

        else:
            for entry in self._entries[year][month]:
                for person in entry["people"]:
                    if person not in people:
                        people[person.title()] = 1
                    else:
                        people[person.title()] += 1

        return self.sort_dict_by_value(people, True)

    def get_mp3_file_length(self):
        """Prompts user to select an mp3 file and returns the length of
        the linked file if it is an mp3, but None if it is any other file type."""
        main_folder = os.getcwd()
        os.chdir(main_folder + "\\new-update-files")
        selection = self.list_selection(["No file"] + os.listdir(), "Which file?")
        if selection == "No file":
            return None

        audio = MP3(main_folder + "\\" + selection)
        length = audio.info.length
        minutes, seconds = divmod(length, 60)
        hours = math.floor(minutes) / 60
        os.chdir(main_folder)
        return f"{math.floor(hours)}:{math.floor(minutes)}:{math.floor(seconds)}"

    def get_summary_from_user(self, date, weekday):
        """Prompts the user through a detailed summary for a given date."""
        print(f"This is the summary for {weekday}, {date}.")
        print("Remember to be as detailed as possible - and to use as many "
              "KEYWORDS as you can! \n")
        morning = str(input("This morning, I... "))
        afternoon = str(input("In the afternoon, I... "))
        evening = str(input("During the evening, I... "))
        opinion = str(input("Overall, I'd say today was... "))

        summary = f"This morning, I {morning}\nIn the afternoon, I {afternoon}\n" \
                  f"During the evening, I {evening}\nOverall, I'd say today was {opinion}"
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
        people = set()
        print("Please input all the names of people - first and last - who are noteworthy to this day.")
        while done is False:
            person = str(input(f"{count}: "))
            people.add(person.lower())
            count += 1
            selection = self.list_selection(["Yes", "No"], "Add another name?")
            if selection == "No":
                done = True

    def get_year_from_user(self):
        """Prompts the user to input a valid year (contained within self._entries).
        Returns None if year is invalid."""
        year = str(input("Please input a year as a four-digit number: "))
        if len(year) != 4 or year not in self._entries:
            return None
        return year

    def get_month_from_user(self):
        """Prompts the user to input a valid month as a number. Returns the
        number converted to string equivalent or None."""
        month = str(input("Please input a month as a number between 1 - 12: "))
        return self.convert_num_to_month(month)

    def sort_dict_by_value(self, dict, order):
        """Accepts a dictionary and returns the dictionary sorted by value."""
        return {k: v for k, v in sorted(        # Returns a new dictionary
            dict.items(),                       # Selecting from the dictionary "happiness" as a list of tuples
            key=lambda pair: pair[1],           # Sorting according to the second item in the tuple, AKA the value
            reverse=bool(order))}               # Reversing because by default it sorts in ascending order

    def add_first_entry(self):
        self.new_entry(self.get_current_date(), self.get_current_weekday())

    def upload_file(self, date, weekday):
        """Prompts the user to select a file and automatically moves that file
        to my diary folder of the correct year."""
        confirm = self.list_selection(["Yes", "No"],            # Asks the user if they want to upload a file
                                      f"Would you like to upload a file for {weekday}, {date}?")
        if confirm == "No":
            return

        os.chdir(os.getcwd() + "\\new-update-files")            # Changes directory to new-update-files
        # print("The current directory is: " + os.getcwd())
        files = []
        files += os.listdir()                                   # Saves all files in this directory
        if not files:
            return print("There are no files to upload.")
        files.append("Cancel")

        selection = self.list_selection(files, "Which file?")   # Asks user to select file
        if selection == "Cancel":
            return None

        root = f'{os.getcwd()}\\'
        year, month, day = self.split_date(date)
        dest = f'C:\\Users\\Colin\\Desktop\\Master Folder\\Projects\\Diary\\{datetime.date(year, month, day).year}'
        self.move_file(root + selection, dest)                  # Moves target file to appropriate diary folder
        os.chdir("..")
        # print(f"This is what's being saved: {dest}\\{selection}")
        return f"{dest}\\{selection}"

    def split_date(self, date):
        """Splits a hyphenated date into its year/month/day parts, and returns each as an int."""
        date_list = str(date).split("-")
        return int(date_list[0]), int(date_list[1]), int(date_list[2])

    def move_file(self, file, dest):
        """Accepts a file and a destination and moves that file to the destination."""
        shutil.copy(file, dest)
        os.remove(file)

    def list_selection(self, choices, message=""):
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
        search_match = []
        for year in self._entries:
            for month in self._entries[year]:
                for entry in self._entries[year][month]:
                    if search_date in entry["date"]:
                        search_match.append(entry)
        return search_match

    def convert_num_to_month(self, num):
        """Accepts a number between 1-12 and returns matching month, or None if no match."""
        month_list = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        if 1 <= num <= 12:
            return month_list[int(num)-1]
        return None

    # Extra functions ---------------------------------

    def import_stats_from_csv(self, filepath):
        """Takes a csv file, and if the file is formatted properly,
        pulls requisite data to create diary entries."""
        file = csv.reader(open(filepath))                   # Opens the given file
        rows = list(file)

        for row in rows:                                    # Cycles through the rows, pulling data
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
            try:                                            # Gathers list of relevant people, or handles if none
                i = 4
                while row[i]:
                    people.append(str(row[i]))
                    i += 1
            except IndexError:
                pass

            if str(year) not in self._entries:              # Creates correct dicts / lists if new year / month
                self._entries[str(year)] = {}
            if str(month) not in self._entries[str(year)]:
                self._entries[str(year)][str(month)] = []

            self._entries[str(year)][str(month)].append({   # Creates a new diary entry
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
                        new_summmary = entry["summary"].replace(string, "")
                        entry["summary"] = new_summmary


if __name__ == '__main__':
    diary = Diary()
