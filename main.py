# Author: Colin Joss
# Last date updated: 11-9-2021
# Description: A shell-inspired interface for interacting with my digital diary.

import os
import re
import math
import csv
import calendar
import inquirer
from mutagen.mp3 import MP3
import datetime
from datetime import datetime as dt
from pyfiglet import Figlet
import pandas as pd


MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


class Diary:
    def __init__(self):
        with open('diary-data.csv', 'r', newline='') as infile:
            self._diary = pd.read_csv(infile)
            self.shell()

    def shell(self):
        status = 1
        while status:
            print(': ', end='')
            user_input = input()

            if not type(user_input) == str:
                print('That is not an acceptable command. Please try again.')
                continue
            status = self.process_input(user_input)

    def process_input(self, user_input):
        data = self._diary.copy(deep=True)
        command = user_input.split()

        if command[0] == 'sd':
            if len(command) == 1:
                print('no argument error: please include date in the form XXXX-XX-XX')
            else:
                self.handle_sd(command[1], data)

        elif command[0] == 'rd':
            self.get_random_entry(data)

        elif command[0] == 'yr':
            if len(command) == 1:
                print('no argument error: please include year in form XXXX')
            elif len(command) == 2:
                print(data.loc[data['year'] == int(command[1])])
            else:
                self.handle_args(command, data)

        elif command[0] == 'all':
            if len(command) == 1:
                print(data)
            else:
                self.handle_args(command, data)

        elif command[0] == 'exit':
            return 0

        else:
            print('unknown command [', command[0], ']: please try again.')

        return 1

    def handle_sd(self, date, data):
        pass

    def get_random_entry(self, data):
        pass

    def handle_args(self, command, data):
        arg = command[1]
        while arg:
            if arg == '-r':
                pass
            elif arg == '-c':
                pass
            elif arg == '-w':
                pass
            elif arg == '-a':
                pass
            elif arg == '-s':
                pass
            else:
                print('unknown argument [', arg, ']: please try again.')
                break

    def handle_r(self):
        pass

    def handle_c(self):
        pass

    def handle_w(self):
        pass

    def handle_a(self):
        pass

    def handle_s(self):
        pass

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
            selection = self.list_selection(['Update diary', 'Search diary', 'Statistics', 'Exit'])

            # Prompts user through the diary updating process
            if selection == 'Update diary':
                self.update_diary()

            # Prompts user to search and returns a csv with the results
            elif selection == 'Search diary':
                keyword = str(input('Enter a search term: '))
                self.search_by_keyword(keyword)

            # Generates a csv of yearly and monthly statistics
            elif selection == 'Statistics':
                print(f'Total # of data entries:   {self.get_total_entries()}')
                print(f'Total # of recorded files: {self.get_total_files()}')
                print(f'Total recording duration:  {self.get_total_length()} hours')
                print('Statistics csv successfully generated!\n')
                self.update_statistics_csv(self.get_last_date_updated())

            # Exits
            else:
                close_program = True
                print('Goodbye!')

    def update_diary(self):
        """Records new diary entry(s)."""
        today = self.get_current_date()
        last_entry = self.get_last_date_updated()

        # If there are entries missing, prompts the user to do those first!
        if self._diary.empty is False:
            if last_entry != today:
                missing_days = self.get_missing_entry_dates(last_entry, today)
                print(missing_days)
                self.catch_up(missing_days)
                selection = self.list_selection(['Yes', 'No'], 'Would you like to skip today?')
                if selection == 'Yes':
                    return True

        # Prompts user to update the diary for today's date
        entry = self.new_entry(self.get_current_date(), self.get_current_year(),
                               self.get_current_month(), self.get_current_weekday())
        self.append_to_csv(entry)

    @staticmethod
    def get_missing_entry_dates(last_entry, today):
        """Calculates the difference between the date of the last entry and
        the current date, then returns a list of dates."""
        missing = []
        one_less_day = None
        less = 1

        # Collects dates in list between the current date and the date of the last entry
        while one_less_day != last_entry:
            if one_less_day is not None:
                missing.append(one_less_day)
            one_less_day = (dt.strptime(today, '%m/%d/%y') - datetime.timedelta(days=less)).strftime('%m/%d/%Y')
            less += 1
        missing.reverse()
        return missing

    def catch_up(self, missing_days):
        """Prompts the user to catch up on missed days with no diary entries."""
        print('You need to catch up on some days! Update these first. \n')
        for day in missing_days:
            date_object = dt.strptime(day, '%m/%d/%Y')
            date = day
            year = date_object.strftime('%Y')
            month = date_object.strftime('%B')
            weekday = date_object.strftime('%A')
            entry = self.new_entry(date, year, month, weekday)
            self.append_to_csv(entry)

    def new_entry(self, date, year, month, weekday):
        """Prompts the user through the components of a diary entry, and
        then adds the entry to the list of all entries."""
        date = date
        year = year
        month = month
        weekday = weekday
        summary = self.get_summary_from_user(date, weekday)
        happiness = self.get_happiness_from_user()
        duration = self.get_mp3_file_length()
        people = self.get_people_from_user()

        return [date, year, month, weekday, summary, happiness, duration, people]

    def search_by_keyword(self, keyword):
        """Accepts a search keyword and returns a list of matches."""
        # Searches both summary and people columns
        df1 = self._diary[self._diary['summary'].str.contains(re.compile(keyword, re.IGNORECASE), na=False)]
        df2 = self._diary[self._diary['people'].str.contains(re.compile(keyword, re.IGNORECASE), na=False)]
        search_df = pd.concat([df1, df2])

        # Checks if the dataframe is empty
        if search_df.empty:
            print('No results\n')
            return False
        else:
            search_df.to_csv(f'{keyword}.csv')
            print('Search results csv successfully generated!')
            return True

    def update_statistics_csv(self, last_entry):
        """Automatically calculates a set of statistics from my diary and
        organizes it in a csv."""
        if last_entry is None:
            return None

        # Generates list of all complete years (except 2013, a partial)
        current_year = int(self.get_current_year())
        total_years = []
        while current_year != 2013:
            current_year -= 1
            total_years.append(current_year)

        # Calculate key statistics for every available year
        for year in total_years:
            current_year = self._diary.loc[self._diary['year'] == year]
            year_happiness = current_year.describe()['happiness']['mean']

            # Calculate lists of months and weekdays ranked by happiness, people ranked by mentions
            months_ranked = self.calculate_happiest_month(current_year)
            weekdays_ranked = self.calculate_happiest_weekday(current_year)
            people_ranked = self.calculate_most_mentioned(current_year)

            # Updates the stats spreadsheet
            v = 'w' if year == int(self.get_current_year()) - 1 else 'a'
            with open('statistics.csv', f'{v}', newline='') as outfile:
                pd.DataFrame({'': year_happiness}, index=[year]).to_csv(outfile)
                pd.DataFrame(months_ranked, index=[year]).to_csv(outfile)
                pd.DataFrame(weekdays_ranked, index=[year]).to_csv(outfile)
                pd.DataFrame(people_ranked, index=[year])[0:10].to_csv(outfile)

    def calculate_happiest_month(self, current_year):
        """Takes the current year and returns a dictionary of the months in that
        year sorted by their happiness rating."""
        months_ranked = {}
        for month in MONTHS:
            current_month = current_year.loc[current_year['month'] == month]
            month_happiness = current_month.describe()['happiness']['mean']
            months_ranked[month] = month_happiness

        return self.sort_dict_by_value(months_ranked, True)

    def calculate_happiest_weekday(self, current_year):
        """Takes the current year and returns a dictionary of the weekdays in that
        year sorted by their happiness rating."""
        weekdays_ranked = {}
        for weekday in WEEKDAYS:
            current_weekday = current_year.loc[current_year['weekday'] == weekday]
            month_happiness = current_weekday.describe()['happiness']['mean']
            weekdays_ranked[weekday] = month_happiness

        return self.sort_dict_by_value(weekdays_ranked, True)

    def calculate_most_mentioned(self, current_year):
        """Takes the current year and returns a dictionary of the people mentioned
        that year sorted by how many times they were mentioned."""
        people_ranked = {}
        for people in current_year['people'].tolist():
            if isinstance(people, str) is False:
                continue

            for person in people.split(', '):
                if person not in people_ranked:
                    people_ranked[person.title()] = 1
                else:
                    people_ranked[person.title()] += 1

        return self.sort_dict_by_value(people_ranked, True)

    # Getters and helpers --------------------------------------

    @staticmethod
    def get_current_date():
        """Returns the current date."""
        return datetime.date.today().strftime('%m/%d/%y')

    @staticmethod
    def get_current_weekday():
        """Returns the current day of the week as a string."""
        return datetime.date.today().strftime('%A')

    @staticmethod
    def get_current_month():
        """Returns the current month of the year as a string."""
        return datetime.date.today().strftime('%B')

    @staticmethod
    def get_current_year():
        """Returns the current year as a string."""
        return datetime.date.today().strftime('%Y')

    def get_last_date_updated(self):
        """Returns the most recent diary entry, or None if there are
        no entries."""
        if self._diary is None:
            return None
        date_object = dt.strptime(self._diary['date'].iloc[-1], '%m/%d/%Y')
        return date_object.strftime('%m/%d/%Y')

    def get_total_entries(self):
        """Returns the total number of user-submitted entries."""
        return len(self._diary)

    def get_total_files(self):
        """Returns the total number of user-submitted files."""
        duration_df = self._diary['duration'].dropna()
        return len(duration_df)

    def get_total_length(self):
        """Calculates the sum total amount of recording time."""
        duration_df = self._diary['duration'].dropna()
        duration_sum = datetime.timedelta(hours=0, minutes=0, seconds=0)
        for duration in duration_df.tolist():
            if duration == ' ':
                continue
            hms = duration.split(':')
            time_obj = datetime.timedelta(hours=int(hms[0]), minutes=int(hms[1]), seconds=int(hms[2]))
            duration_sum += time_obj

        return duration_sum

    def get_mp3_file_length(self):
        """Prompts user to select an mp3 file and returns the length of
        the linked file if it is an mp3, but None if it is any other file type."""
        main_folder = os.getcwd()
        os.chdir(main_folder + '\\new-update-files')
        selection = self.list_selection(['No file'] + os.listdir(), 'Which file?')
        if selection == 'No file':
            os.chdir(main_folder)
            return None

        audio = MP3(main_folder + '\\new-update-files\\' + selection)
        length = audio.info.length
        hms_string = self.convert_seconds_to_hms(length)
        os.chdir(main_folder)
        return hms_string

    def append_to_csv(self, entry):
        """Adds a new row of data to the diary csv and reloads the csv as a dataframe."""
        # Appends new entry as a row to the data csv
        with open('diary-data.csv', 'a', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(entry)

        # Reloads the newly updated csv into the diary assistant program
        with open('diary-data.csv', 'r', newline='') as infile:
            self._diary = pd.read_csv(infile)

    @staticmethod
    def convert_seconds_to_hms(seconds):
        """Accepts a number of seconds and returns a string of the time,
        with hours and minutes, divided by colons."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f'{math.floor(hours)}:{math.floor(minutes)}:{math.floor(seconds)}'

    @staticmethod
    def get_summary_from_user(date, weekday):
        """Prompts the user through a detailed summary for a given date."""
        print(f'This is the summary for {weekday}, {date}.')
        print('Remember to be as detailed as possible - and to use as many '
              'KEYWORDS as you can! \n')
        morning = str(input('This morning, I... '))
        afternoon = str(input('In the afternoon, I... '))
        evening = str(input('During the evening, I... '))
        opinion = str(input('Overall, I\'d say today was... '))

        summary = f'This morning, I {morning} In the afternoon, I {afternoon} ' \
                  f'During the evening, I {evening} Overall, I\'d say today was {opinion}'
        return summary

    def get_happiness_from_user(self):
        """Prompts users to select from a list of ratings and then returns that rating."""
        selection = self.list_selection([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                                        'How would you rate today?')
        return float(selection)

    def get_people_from_user(self):
        """Prompts users to input the names of people until they exit."""
        done = False
        count = 1
        people = []
        print('Input all the names of people - first and last - who are noteworthy to this day.')
        while done is False:
            selection = self.list_selection(['Continue', 'Cancel'], 'Please enter a name.')
            if selection == 'Cancel':
                done = True
                continue
            person = str(input(f'{count}: '))
            people.append(person)
            count += 1

        return people

    @staticmethod
    def sort_dict_by_value(my_dict, order):
        """Accepts a dictionary and returns the dictionary sorted by value."""
        return {k: v for k, v in sorted(  # Returns a new dictionary
            my_dict.items(),  # Selecting from the dictionary "happiness" as a list of tuples
            key=lambda pair: pair[1],  # Sorting according to the second item in the tuple, AKA the value
            reverse=bool(order))}  # Reversing because by default it sorts in ascending order

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
        return selection['list']


if __name__ == '__main__':
    diary = Diary()
