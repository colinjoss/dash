# Author: Colin Joss
# Last date updated: 3-31-2023
# Description: A shell-inspired interface for interacting with my digital diary.

import datetime
from datetime import datetime as dt
from pyfiglet import Figlet
import pandas as pd
import random as rand

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)


class Diary:
    def __init__(self):
        self.COMMANDS = {
            'sd': self.specific_date,
            'rd': self.random_date,
            'yr': self.year_dates,
            'all': self.all_dates
        }
        self.ARGUMENTS = {
            '-r': self.reduce,
            '-o': self.output_format,
            '-w': self.with_term,
            '-a': self.average,
            '-s': self.sum
        }
        with open('diary-data.csv', 'r', newline='') as infile:
            data = pd.read_csv(infile)
            self._diary = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        self.title()
        self.shell()

    @staticmethod
    def title():
        """Displays the title of the program."""
        custom_fig = Figlet()
        print(custom_fig.renderText('DASH'))
        print('Dash version 2.0')
        print('Program by Colin Joss')
        print('*** input command \'help\' for list of commands and arguments')
        print('-------------------------------------------------------------\n')

    def shell(self):
        """Primary loop, from which commands are inputted and executed."""
        status = 1
        while status >= 0:
            print(': ', end='')
            user_input = input()
            status = self.process_input(user_input)

    def process_input(self, user_input):
        """Handles primary command."""
        command = user_input.split()
        print(command)

        if len(command) < 1:
            print('error: no command inputted')
            return 1
        if command[0] == 'exit':
            return -1
        if command[0] == 'help':
            self.help()
            return 0
        if self.bad_argument(command[0], self.COMMANDS, f"error: argument {command[0]} nonexistent"):
            return 1
        return self.COMMANDS[command[0]](command)

    @staticmethod
    def help():
        print('KEY')
        print('-----------------------------------------------------------------')
        print('[] replace with indicated input')
        print('() optional')
        print('-  hyphen instead of space')
        print('>  search in')
        print('*  group by')
        print('')
        print('COMMANDS')
        print('command      action              usage')
        print('-----------------------------------------------------------------')
        print('sd           get data for specific date      sd [M/D/YYYY]')
        print('rd           get data for random date        rd')
        print('yr           get data for all year dates     yr [YYYY]')
        print('all          get data for all dates          all')
        print('')
        print('ARGUMENTS')
        print('argument     action              usage')
        print('-----------------------------------------------------------------')
        print('-r           reduce date range   -r [M/D/YYYY] [M/D/YYYY]')
        print('-o           output format       -o [column1-column2-column3]')
        print('-w           with search term    -w [search-term-here] > [column]')
        print('-a           average numbers     -a [column1] (* [column2])')
        print('-s           sum numbers         -s [column1] (* [column2])')

    def specific_date(self, command):
        """Prints data for one specific date unless error. Returns code 0 or 1."""
        if self.missing_argument(1, command, f"error: missing argument at 1"):
            return 1
        if not self.valid_date_format(1, command, f"error: invalid date format at 1"):
            return 1

        data = self._diary.copy(deep=True)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.loc[data['date'] == command[1]]  # Reduce data to only where date matches given

        if len(command) == 2:  # Command has no arguments
            print(data.dropna(axis=1, how='all'))
            return 0

        return self.handle_args(command, data, 2)  # Command has arguments

    def random_date(self, command):
        """Prints data for one random date unless error. Returns code 0 or 1."""
        if self.extra_argument(1, command, f"error: excessive argument at 1"):
            return 1

        data = self._diary.copy(deep=True)
        data = data.iloc[rand.randint(0, len(data.index))]
        print(data.dropna(how='all'))
        return 0

    def year_dates(self, command):
        """Prints all data for one year unless error. Returns code 0 or 1."""
        if self.missing_argument(1, command, f"error: missing argument at 1"):
            return 1
        if not self.is_int(command[1]):
            print('bad argument error: first argument must be a number')
            return

        data = self._diary.copy(deep=True)
        data = data.loc[data['year'] == int(command[1])]
        if len(command) == 2:
            print(data.dropna(axis=1, how='all'))
            return 0

        return self.handle_args(command, data, 2)

    def all_dates(self, command):
        """Prints all data unless error. Returns code 0 or 1."""
        data = self._diary.copy(deep=True)
        if len(command) == 1:
            print(data)
            return 0
        return self.handle_args(command, data, 1)

    def handle_args(self, args, data, index):
        """Secondary loop, from where all command arguments are handled."""
        status = 0
        while index < len(args):
            cur_arg = args[index]
            if self.bad_argument(cur_arg, self.ARGUMENTS, f"error: argument {cur_arg} nonexistent"):
                status = 1
                return status
            status, index, data = self.ARGUMENTS[cur_arg](args, index + 1, data)
            if status == 1:  # Error, exit loop and return status
                return status
            if isinstance(data, int) and index < len(args):  # If data is number but more args exist, error
                print('error: -a or -s must be last argument')
                return status

        if data is not None:
            print(data)
        return status

    def reduce(self, args, index, data):
        """Reduces data by date range."""
        if self.missing_argument(index + 1, args, f"error: missing argument at {index + 1}"):
            return 1, None, None
        if not self.valid_date_format(index, args, f"error: invalid date format at {index}"):
            return 1, None, None
        if not self.valid_date_format(index + 1, args, f"error: invalid date format at {index + 1}"):
            return 1, None, None
        if not self.date_is_less_than(args[index], args[index+1]):
            return 1, None, None
        if not self.date_in_range(args[index], data):
            return 1, None, None
        if not self.date_in_range(args[index+1], data):
            return 1, None, None

        index1 = data.loc[data['date'] == args[index]].index[0]
        index2 = data.loc[data['date'] == args[index + 1]].index[0]
        data = data.iloc[index1:index2 + 1]

        index += 2
        return 0, index, data

    def output_format(self, args, index, data):
        """Formats output to show only specific columns."""
        if self.missing_argument(index, args, f"error: missing argument at {index}"):
            return 1, None, None
        columns = args[index].split('-')
        for col in columns:
            if self.column_does_not_exist(col, data, f"error: column {col} nonexistent"):
                return 1, None, None

        data = data[columns]
        index += 1
        return 0, index, data

    def with_term(self, args, index, data):
        """Filters data to only include search term."""
        if self.missing_argument(index + 1, args, f"error: missing argument at {index}"):  # Search term
            return 1, None, None
        if self.missing_argument(index + 1, args, f"error: missing argument at {index + 1}"):  # > operator
            return 1, None, None
        if self.missing_argument(index + 2, args, f"error: missing argument at {index + 2}"):  # column name
            return 1, None, None
        if self.bad_operator(index + 1, args, '>', f"error: operator {args[index + 1]} is not >"):
            return 1, None, None
        if self.column_does_not_exist(args[index + 2], data, f"error: column {args[index + 2]} nonexistent"):
            return 1, None, None

        search = args[index].split('+')
        search = ' '.join(search)  # Formatted string search term
        column = args[index + 2]

        search_data = data.copy(deep=True)
        search_data = search_data[search_data[column].notna()]
        search_data = search_data.loc[search_data[column].str.contains(search, case=False)]

        return 0, index + 3, search_data

    def average(self, args, index, data):
        """Calculates average of column alone or grouped by other column."""
        if self.missing_argument(index, args, f"error: missing argument at {index}"):
            return 1, None, None
        if self.column_does_not_exist(args[index], data, f"error: column {args[index]} nonexistent"):
            return 1, None, None
        if args[index] != 'happiness':
            print(f"error: {args[index]} does not support -a")
            return 1, None, None

        column1 = args[index]
        if index + 1 < len(args) and args[index + 1] == '*':
            data = self.group_by(data, index, args, column1, 'mean')
            index += 3
        else:
            data = data[column1].mean()
            index += 1

        return 0, index, data

    def sum(self, args, index, data):
        """Calculates sum of column alone or grouped by other column"""
        if self.missing_argument(index, args, f"error: missing argument at {index}"):
            return 1, None, None
        if self.column_does_not_exist(args[index], data, f"error: column {args[index]} nonexistent"):
            return 1, None, None
        if args[index] != 'happiness' or args[index] != 'duration':
            print(f"error: {args[index]} does not support -a")
            return 1, None, None

        column = args[index]
        if column == 'happiness':
            if index + 1 < len(args) and args[index + 1] == '*':
                data = self.group_by(data, index, args, column, 'sum')
                index += 3
            else:
                data = data[column].sum()
                index += 1
        elif column == 'duration':
            data = self.sum_duration(data)
            index += 1
            if index + 1 < len(args) and args[index + 1] == '*':
                print(f"error: {column} does not support *")
                return 1, None, None

        return 0, index, data

    def group_by(self, data, index, args, column1, action):
        """Calculates average or sum and groups by column"""
        if self.missing_argument(index + 2, args, f"error: missing argument at {index}"):
            return 1, None, None
        if self.column_does_not_exist(args[index + 2], data, f"error: column {args[index + 2]} nonexistent"):
            return 1, None, None
        column2 = args[index + 2]

        if action == 'mean':
            data = data.groupby(column2, as_index=False)[column1].mean()
        elif action == 'sum':
            data = data.groupby(column2, as_index=False)[column1].sum()

        return data.sort_values(by=[column1], ascending=False)

    def sum_duration(self, data):
        """Sums the time duration of the recording column"""
        duration_sum = datetime.timedelta(hours=0, minutes=0, seconds=0)
        for item in data['duration'].dropna().tolist():
            hms = item.split(':')
            if self.is_int(hms[0]) and self.is_int(hms[1]) and self.is_int(hms[2]):
                time_obj = datetime.timedelta(hours=int(hms[0]), minutes=int(hms[1]), seconds=int(hms[2]))
                duration_sum += time_obj
        return duration_sum

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

    # ERROR HANDLING ----------------------------------------------------------------------------------

    @staticmethod
    def extra_argument(length, command, error):
        """Returns true if excessive argument, false otherwise."""
        if len(command) != length:
            print(error)
            return True
        return False

    @staticmethod
    def valid_date_format(i, command, error):
        """Returns true if date at position i is in correct format, otherwise returns false."""
        try:
            dt.strptime(command[i], "%m/%d/%Y")
        except ValueError:
            print(error)
            return False
        return True

    @staticmethod
    def bad_argument(arg, possible, error):
        """Returns true if bad argument, false otherwise."""
        if arg not in possible:
            print(error)
            return True
        return False

    @staticmethod
    def missing_argument(i, args, error):
        """Returns true if missing argument, false otherwise."""
        if i > len(args) - 1:
            if error is not None:
                print(error)
            return True
        return False

    @staticmethod
    def bad_operator(i, args, target, error):
        """Returns true if bad operator, false otherwise."""
        if args[i] != target:
            if error is not None:
                print(error)
            return True
        return False

    @staticmethod
    def column_does_not_exist(column, data, error):
        """Returns true if column nonexistent, false otherwise."""
        if column not in data:
            if error is not None:
                print(error)
            return True
        return False

    @staticmethod
    def date_is_less_than(date1, date2):
        """Returns true if date1 came before date2, otherwise false."""
        if dt.strptime(date1, "%m/%d/%Y") < dt.strptime(date2, "%m/%d/%Y"):
            return True
        print('error: dates must be in ascending order')
        return False

    @staticmethod
    def date_in_range(date, data):
        """Returns true if date1 came before date2, otherwise false."""
        if date in data['date'].unique():
            return True
        print('error: date out of range')
        return False


if __name__ == '__main__':
    diary = Diary()
