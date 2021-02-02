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

    def get_date(self):
        """Returns the current date."""
        return datetime.date.today()

    def get_weekday(self):
        """Returns the current day of the week."""
        return datetime.date.today().strftime("%A")

    def get_last_entry(self):
        """Returns the most recent diary entry, or None if there are
        no entries."""
        if not self._entries:
            return None

        return self._entries[-1]

    def update_diary(self):
        """Records new diary entry(s)."""
        last_entry = self.get_last_entry()
        if last_entry is None:
            return

        last_date = last_entry["date"]
        if last_date != self.get_date():
            self.catch_up(last_date)

        self.new_entry(self.get_date(), self.get_weekday())

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
        file = self.upload_file()
        summary = self.get_summary_from_user(date, weekday)
        happiness = int(input("Please enter today's happiness score: "))
        self._entries.append({"date": date,
                              "weekday": weekday,
                              "file": file,
                              "summary": summary,
                              "happiness": happiness})

    def split_date(self, date):
        """Splits a hyphenated date into its year/month/day parts, and returns each as an int."""
        date_list = str(date).split("-")
        return int(date_list[0]), int(date_list[1]), int(date_list[2])

    def upload_file(self, date, weekday):
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

        dest = f'C:\\Users\\Colin\\Desktop\\Master Folder\\Projects\\Diary\\{datetime.date.today().year}'
        self.move_file(selection, dest)
        return f"{dest}\\selection"

    def move_file(self, file, dest):
        src = f'{os.getcwd()}\\new-update-files\\'
        shutil.copy(src + file, dest)

    def list_selection(self, choices, message=""):
        options = [
            inquirer.List('list',
                          message=message,
                          choices=choices
                          )]
        selection = inquirer.prompt(options)
        return selection["list"]


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


if __name__ == '__main__':
    test = Diary()
    # print(test.get_summary_from_user(datetime.date.today(), "Tuesday"))
