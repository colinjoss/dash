# Author: Colin Joss
# Last date updated: 2-1-2021
# Description: A simple python program for my personal diary system, made with the intention to
#              speed up the process of maintaining it.
import datetime
import json
import os
import calendar


my_date = datetime.date(2021, 2, 2)
print(calendar.day_name[my_date.weekday()])


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
        """Records a new diary entry."""
        last_entry = self.get_last_entry()
        if last_entry is None:
            return

        last_date = last_entry["date"]
        if last_date != self.get_date():
            self.catch_up(last_date)

        self.new_entry(self.get_date(), self.get_weekday())

    def catch_up(self, last_date):
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
            year, month, day = self.split_date()
            weekday = datetime.date(year, month, day).strftime("%A")
            self.new_entry(day, weekday)

    def new_entry(self, day, weekday):
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
        date_list = str(date).split("-")
        return int(date_list[0]), int(date_list[1]), int(date_list[2])

    def upload_file(self):
        pass
        # os.chdir(f"/Users/Desktop/Master Folder/Projects/Diary/{date.today().year}/")

    def get_summary_from_user(self, date, weekday):
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
    date = str(test.get_date())
    year, month, day = test.split_date(date)
    print(datetime.date(year, month, day).strftime("%B"))
