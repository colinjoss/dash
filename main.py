# Author: Colin Joss
# Last date updated: 2-1-2021
# Description: A simple python program for my personal diary system, made with the intention to
#              speed up the process of maintaining it.
import datetime
import json
import os
import shutil
import inquirer
import calendar


# print(calendar.setfirstweekday(6))
# print(calendar.month(2021, 2))


class Diary:
    def __init__(self):
        with open("save_data.json", "r") as infile:
            data = json.load(infile)
            self._entries = data[0]
            self._stats = []

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

    def get_first_entry(self):
        """Returns the first ever diary entry, or None if there are no entries."""
        if not self._entries:
            return None
        return self._entries[0]

    def get_last_entry(self):
        """Returns the most recent diary entry, or None if there are
        no entries."""
        if not self._entries:
            return None
        return self._entries[-1]

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
                    if entry["file"] != None:
                        count += 1
        return count

    def get_happiest_year(self):
        pass

    def get_happiest_month(self):
        pass

    def get_happiest_weekday(self):
        pass

    def get_most_mentioned_person(self):
        pass

    def add_first_entry(self):
        self.new_entry(self.get_date(), self.get_weekday())

    def update_diary(self):
        """Records new diary entry(s)."""
        last_entry = self.get_last_entry()
        if last_entry is None:
            self.add_first_entry()
            return

        last_date = last_entry["date"]
        if last_date != self.get_current_date():
            self.catch_up(last_date)

        year = self.get_current_year()
        if year not in self._entries:
            self._entries[year] = {}

        month = self.get_current_month()
        if month not in self._entries[year]:
            self._entries[year][month] = []

        entry = self.new_entry(self.get_current_date(), self.get_current_weekday())
        self._entries[year][month].append(entry)

    def catch_up(self, last_date):
        """If update_diary determines the current date and the last date the diary was updated
        don't match, catch_up is called to prompt the user to update for multiple previous days."""
        match = False
        catch_up_days = []
        while match is False:
            one_less_day = datetime.date.today() - datetime.timedelta(days=1)
            if one_less_day == last_date:
                match = True
            else:
                catch_up_days.append(one_less_day)

        for day in catch_up_days:
            date = day
            year, month, day = self.split_date(date)
            weekday = datetime.date(year, month, day).strftime("%A")
            self.new_entry(day, weekday)

    def new_entry(self, day, weekday):
        """Prompts the user through the components of a diary entry, and
        then adds the entry to the list of all entries."""
        date = day
        weekday = weekday
        file = self.upload_file(day, weekday)
        summary = self.get_summary_from_user(date, weekday)
        happiness = self.get_happiness_from_user()
        people = self.get_people_from_user()
        return {"date": date,
                "weekday": weekday,
                "file": file,
                "summary": summary,
                "happiness": happiness,
                "people": people}

    def get_summary_from_user(self, date, weekday):
        """Prompts the user through a detailed summary for a given date."""
        print(f"This is the summary for {weekday}, {date}.")
        print("Remember to be as detailed as possible - and to use as many "
              "KEYWORDS as you can!")
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

    def upload_file(self, date, weekday):
        """Prompts the user to select a file and automatically moves that file
        to my diary folder of the correct year."""
        confirm = self.list_selection(["Yes", "No"],
                                      f"Would you like to upload a file for {weekday}, {date}?")
        if confirm == "No":
            return

        os.chdir(os.getcwd() + "\\new-update-files")
        files = []
        files += os.listdir()
        if not files:
            return print("There are no files to upload.")
        files.append("Cancel")

        selection = self.list_selection(files, "Which file?")
        if selection == "Cancel":
            return

        root = f'{os.getcwd()}\\new-update-files\\'
        dest = f'C:\\Users\\Colin\\Desktop\\Master Folder\\Projects\\Diary\\{datetime.date.today().year}'
        self.move_file(root + selection, dest)
        return f"{dest}\\selection"

    def split_date(self, date):
        """Splits a hyphenated date into its year/month/day parts, and returns each as an int."""
        date_list = str(date).split("-")
        return int(date_list[0]), int(date_list[1]), int(date_list[2])

    def move_file(self, file, dest):
        """Accepts a file and a destination and moves that file to the destination."""
        shutil.copy(file, dest)

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
        if search_date in self._entries:
            search_match.append(self._entries[search_date])
        return search_match

    def search_by_keyword(self, search_keyword):
        """Accepts a search keyword and returns a list of matches."""
        search_match = []
        for entry in self._entries:
            if search_keyword in entry["summary"]:
                search_match.append(entry)

    def advanced_search(self):
        pass


if __name__ == '__main__':
    test = Diary()
    print(test.get_total_entries())
