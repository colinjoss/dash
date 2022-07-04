# Author: Colin Joss
# Last date updated: 12-29-2021
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
        self.COMMANDS = {'sd': self.specific_date, 'rd': self.random_date, 'yr': self.year_dates,
                         'all': self.all_dates}
        self.ARGUMENTS = {'-r': self.reduce, '-o': self.output_format, '-w': self.with_term,
                          '-a': self.average, '-s': self.sum}
        with open('diary-data.csv', 'r', newline='') as infile:
            self._diary = pd.read_csv(infile)
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
        status = 1
        while status >= 0:
            print(': ', end='')
            user_input = input()
            status = self.process_input(user_input)

    def process_input(self, user_input):
        command = user_input.split()

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
        print('>  search in')
        print('*  group by')
        print('')
        print('COMMANDS')
        print('command      action              usage')
        print('-----------------------------------------------------------------')
        print('sd           get specific date   sd [M/D/YYYY]')
        print('rd           get random date     rd [M/D/YYYY]')
        print('yr           get year dates      yr [YYYY]')
        print('all          get all dates       all')
        print('')
        print('ARGUMENTS')
        print('argument     action              usage')
        print('-----------------------------------------------------------------')
        print('-r           reduce date range   -r [M/D/YYYY] [M/D/YYYY]')
        print('-o           output format       -o [column1, column2, ...]')
        print('-w           with search term    -w [search+term+here] > [column]')
        print('-a           average numbers     -a [column1] (* [column2])')
        print('-s           sum numbers         -s [column1] (* [column2])')

    def specific_date(self, command):
        if self.missing_argument(1, command, f"error: missing argument at 1"):
            return 1

        data = self._diary.copy(deep=True)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.loc[data['date'] == command[1]]
        if len(command) == 2:
            if not self.check_date_format(command[1]):
                return 1
            print(data.dropna(axis=1, how='all'))
            return 0

        return self.handle_args(command, data, 2)

    def random_date(self, command):
        if len(command) != 1:
            print('error: excessive argument at 1')
            return 1

        data = self._diary.copy(deep=True)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.iloc[rand.randint(0, len(data.index))]
        print(data.dropna(how='all'))
        return 0

    def year_dates(self, command):
        if self.missing_argument(1, command, f"error: missing argument at 1"):
            return 1

        if not self.is_int(command[1]):
            print('bad argument error: first argument must be a number')
            return

        data = self._diary.copy(deep=True)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        data = data.loc[data['year'] == int(command[1])]
        if len(command) == 2:
            print(data.dropna(axis=1, how='all'))
            return 0

        return self.handle_args(command, data, 2)

    def all_dates(self, command):
        data = self._diary.copy(deep=True)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        if len(command) == 1:
            print(data)
            return 0
        return self.handle_args(command, data, 1)

    def handle_args(self, args, data, index):
        status = 0
        while index < len(args):
            cur_arg = args[index]
            if self.bad_argument(cur_arg, self.ARGUMENTS, f"error: argument {cur_arg} nonexistent"):
                status = 1
                return status
            status, index, data = self.ARGUMENTS[cur_arg](args, index+1, data)
            if status == 1:
                return status
            if self.is_int(data) and index < len(args):
                print('error: -a or -s must be last argument')
                return status

        if data is not None:
            print(data)
        return status

    def reduce(self, args, index, data):
        if self.missing_argument(index+1, args, f"error: missing argument at {index+1}"):
            return 1, None, None
        date_1 = args[index]
        if self.check_date_format(date_1) is False:
            return 1, None, None
        date_2 = args[index+1]
        if self.check_date_format(date_2) is False:
            return 1, None, None

        # MISSING: Check that dat1 and date2 are in current dataframe (may have been reduced)
        # MISSING: Check that date1 < date2

        index1 = data.loc[data['date'] == date_1].index[0]
        index2 = data.loc[data['date'] == date_2].index[0]
        data = data.iloc[index1:index2+1]

        index += 2
        return 0, index, data

    def output_format(self, args, index, data):
        if self.missing_argument(index, args, f"error: missing argument at {index}"):
            return 1, None, None

        columns = args[index].split(',')
        for col in columns:
            if self.column_does_not_exist(col, data, f"error: column {col} nonexistent"):
                return 1, None, None

        data = data[columns]
        index += 1
        return 0, index, data

    def with_term(self, args, index, data):
        status, index, data = self.with_term_recursive(args, index, data)
        return status, index, data

    def with_term_recursive(self, args, index, data):
        if self.missing_argument(index+2, args, f"error: missing argument at {index+2}"):
            return 1, None, None
        if self.bad_operator(index+1, args, '>', f"error: operator {args[index+1]} is not >"):
            return 1, None, None
        if self.column_does_not_exist(args[index+2], data, f"error: column {args[index+2]} nonexistent"):
            return 1, None, None

        search = args[index].split('+')
        search = ' '.join(search)
        column = args[index+2]
        status = 0

        search_df = data.copy(deep=True)
        search_df = search_df[search_df[column].notna()]
        if self.is_int(search):
            search_df = search_df[search_df[column] == int(search)]
        elif self.is_float(search):
            search_df = search_df[search_df[column] == float(search)]
        else:
            search_df = search_df.loc[search_df[column].str.contains(search, case=False)]

        if not self.missing_argument(index+3, args, None):
            if not self.bad_operator(index+3, args, '&', None):
                status, index, result = self.with_term_recursive(args, index+4, data)
                if status == 1:
                    return 1, None, None
                search_df = pd.merge(search_df, result, how='inner',
                                     on=['date', 'year', 'month', 'weekday', 'summary',
                                         'happiness', 'duration', 'people']).drop_duplicates()
            elif not self.bad_operator(index+3, args, '|', None):
                status, index, result = self.with_term_recursive(args, index+4, data)
                if status == 1:
                    return 1, None, None
                search_df = pd.concat([search_df, result]).drop_duplicates()
            index += 3
        else:
            index += 3

        return status, index, search_df

    def average(self, args, index, data):
        if self.missing_argument(index, args, f"error: missing argument at {index}"):
            return 1, None, None
        if self.column_does_not_exist(args[index], data, f"error: column {args[index]} nonexistent"):
            return 1, None, None

        column1 = args[index]
        if column1 == 'happiness':
            if index + 1 < len(args) and args[index + 1] == '*':
                data = self.group_by(data, index, args, column1, 'mean')
                index += 3
            else:
                data = data[column1].mean()
                index += 1
        else:
            print(f"error: {column1} does not support -a")
            return 1, None, None

        return 0, index, data

    def sum(self, args, index, data):
        if self.missing_argument(index, args, f"error: missing argument at {index}"):
            return 1, None, None
        if self.column_does_not_exist(args[index], data, f"error: column {args[index]} nonexistent"):
            return 1, None, None

        column1 = args[index]
        if column1 == 'happiness':
            if index + 1 < len(args) and args[index + 1] == '*':
                data = self.group_by(data, index, args, column1, 'sum')
                index += 3
            else:
                data = data[column1].sum()
                index += 1

        elif column1 == 'duration':
            data = self.sum_duration(data)
            index += 1
            if index + 1 < len(args) and args[index + 1] == '*':
                print(f"error: {column1} does not support *")
                return 1, None, None

        else:
            print(f"error: {column1} does not support -s")
            return 1, None, None

        return 0, index, data

    def group_by(self, data, index, args, column1, action):
        if self.missing_argument(index+2, args, f"error: missing argument at {index}"):
            return 1, None, None
        if self.column_does_not_exist(args[index+2], data, f"error: column {args[index+2]} nonexistent"):
            return 1, None, None
        column2 = args[index+2]

        if action == 'mean':
            data = data.groupby(column2, as_index=False)[column1].mean()
        elif action == 'sum':
            data = data.groupby(column2, as_index=False)[column1].sum()

        return data.sort_values(by=[column1], ascending=False)

    def sum_duration(self, data):
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

    @staticmethod
    def check_date_format(date):
        try:
            dt.strptime(date, "%m/%d/%Y")
        except ValueError:
            print('error: date format must be m/d/yyyy')
            return False
        return True
    
    @staticmethod
    def bad_argument(arg, possible, error):
        if arg not in possible:
            print(error)
            return True
        return False

    @staticmethod
    def missing_argument(i, args, error):
        if i > len(args)-1:
            if error is not None:
                print(error)
            return True
        return False

    @staticmethod
    def bad_operator(i, args, target, error):
        if args[i] != target:
            if error is not None:
                print(error)
            return True
        return False

    @staticmethod
    def column_does_not_exist(column, data, error):
        if column not in data:
            if error is not None:
                print(error)
            return True
        return False

    @staticmethod
    def is_int(search):
        try:
            int(search)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def is_float(search):
        try:
            float(search)
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    diary = Diary()
