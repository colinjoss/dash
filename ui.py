# Author: Colin Joss
# Last date updated: 3-2-2023
# Description: An interface


import tkinter as tk


class DashApp (tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Dash')
        self.geometry('1080x720')

        # MENU BAR -----------------------------------------------------------------------------

        menubar = tk.Menu(self)

        # File tab of menu bar
        file = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file)
        file.add_command(label='Open', command=None)
        file.add_command(label='Save', command=None)
        file.add_separator()
        file.add_command(label='Exit', command=self.destroy)

        # Sort tab of menu bar
        sort = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Sort', menu=sort)
        sort.add_command(label='Date Ascending', command=None)
        sort.add_command(label='Date Descending', command=None)
        sort.add_command(label='Happiness Ascending', command=None)
        sort.add_command(label='Happiness Descending', command=None)

        # Filter tab of menu bar
        filter = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Filter', menu=filter)
        filter.add_command(label='Date', command=None)
        filter.add_command(label='Weekday', command=None)
        filter.add_command(label='Happiness', command=None)
        filter.add_command(label='Recording', command=None)
        filter.add_command(label='People', command=None)

        # Help tab of menu bar
        help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=help)

        self.config(menu=menubar)

        # DATA DISPLAY -----------------------------------------------------------------------------


if __name__ == '__main__':
    dash = DashApp()
    dash.mainloop()
