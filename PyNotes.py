import sys
import os

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog

conf_fileloc = './info.conf'
data_folder = './data/'

# Holds general settings
OPT = {
    'TEXT_FONT': -1,
    'LABEL_FONT': -1,
    'TEXT_BG': -1,
    'PERSISTENT': False
}

# Holds settings about each individual category
CATS = {
    # Name: (Lines, Width, Text)
}

# This list will be used by the dropdown option menu
CAT_DROP = []
SELECTED = ''


def load_conf():
    with open('{}'.format(conf_fileloc), 'r') as file:
        for raw_line in file:
            line = raw_line.rstrip()
            if len(line) > 0 and line[0] is not '#':
                setting = line.split(' ')
                if setting[0] == 'TextFont':
                    OPT['TEXT_FONT'] = (setting[1], int(setting[2]))
                elif setting[0] == 'LabelFont':
                    OPT['LABEL_FONT'] = (setting[1], int(setting[2]))
                elif setting[0] == 'TextAreaBg':
                    OPT['TEXT_BG'] = setting[1]
                elif setting[0] == 'Cat':
                    text = ''
                    with open('{}{}.txt'.format(data_folder, setting[1]), 'r') as t_file:
                        for raw_t_line in t_file:
                            t_line = raw_t_line
                            text += t_line
                        CATS[setting[1]] = (setting[2], setting[3], text)
    file.close()

    # Check if everything was configured correctly
    for key, value in OPT.items():
        if value is -1:
            return False

    for key, _ in CATS.items():
        CAT_DROP.append(key)
    return True


def on_close(root):
    # What happens when there is a close window event
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        on_save(root)
        print('INFO: Shutting down the application')
        root.quit()


def on_save(root):
    print('INFO: Saving current state')
    root.save()


def persistent_mode(root, button):
    if not OPT['PERSISTENT']:
        root.wm_attributes('-topmost', 1)
        OPT['PERSISTENT'] = True
        button.config(relief=tk.SUNKEN)
    else:
        root.wm_attributes('-topmost', 0)
        OPT['PERSISTENT'] = False
        button.config(relief=tk.RAISED)


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        global SELECTED
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'PyNotes')

        tool_frame = tk.Frame(self)
        tool_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        def swap_cats(to_t):
            global SELECTED
            CATS[SELECTED] = (CATS[SELECTED][0], CATS[SELECTED][1], self.text_area.get(1.0, tk.END))
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, CATS[to_t][2])
            SELECTED = to_t

        def new_cat():
            global SELECTED

            # Get the new name
            while True:
                new_name = simpledialog.askstring('New Name', 'Enter the new name')
                if new_name != '':
                    break

            if new_name is not None:

                self.text_area.delete(1.0, tk.END)

                # Update the category list
                CAT_DROP.append(new_name)

                # Add a new element in te category info
                CATS[new_name] = (CATS[SELECTED][0], CATS[SELECTED][1], '')
                var.set(new_name)
                droplist['menu'].delete(0, tk.END)
                for cat in CAT_DROP:
                    droplist['menu'].add_command(label=cat, command=tk._setit(var, cat, swap_cats))

                # Update the .conf file
                text = ''
                with open('{}'.format(conf_fileloc), 'r') as file:
                    for raw_line in file:
                        to_write = raw_line
                        line = raw_line.rstrip()
                        if len(line) > 0 and line[0] is not '#':
                            setting = line.split(' ')
                            if setting[0] == 'END':
                                to_write = 'Cat {} {} {}\n'.format(new_name, CATS[new_name][0], CATS[new_name][1])
                                to_write += 'END\n'
                        text += to_write
                file.close()

                file = open('{}'.format(conf_fileloc), 'w')
                file.write(text)
                file.close()

                # Create a new data file
                file = open('{}{}.txt'.format(data_folder, new_name), 'w+')
                file.write('')
                file.close()

                SELECTED = new_name

        new_cat_button = tk.Button(tool_frame)
        new_cat_button.config(text='+', command=new_cat)
        new_cat_button.pack(side=tk.LEFT)

        var = tk.StringVar()
        droplist = tk.OptionMenu(tool_frame, var, *CAT_DROP, command=swap_cats)
        var.set(CAT_DROP[0])
        SELECTED = var.get()
        droplist.pack(side=tk.LEFT)

        rename_button = tk.Button(tool_frame)

        def rename_cat():
            global SELECTED

            # Get the new name
            while True:
                new_name = simpledialog.askstring('New Name', 'Enter the new name')
                if new_name != '':
                    break

            if new_name is not None:

                # Update the list that is used by the optionmenu
                for index in range(len(CAT_DROP)):
                    if CAT_DROP[index] == SELECTED:
                        CAT_DROP[index] = new_name

                # Update the dictionary and the option menu
                CATS[new_name] = CATS.pop(SELECTED)
                var.set(new_name)
                droplist['menu'].delete(0, tk.END)
                for cat in CAT_DROP:
                    droplist['menu'].add_command(label=cat, command=tk._setit(var, cat, swap_cats))

                # Update the .conf file
                text = ''
                with open('{}'.format(conf_fileloc), 'r') as file:
                    for raw_line in file:
                        to_write = raw_line
                        line = raw_line.rstrip()
                        if len(line) > 0 and line[0] is not '#':
                            setting = line.split(' ')
                            if setting[0] == 'Cat' and setting[1] == SELECTED:
                                to_write = 'Cat {} {} {}\n'.format(new_name, setting[2], setting[3])
                        text += to_write
                file.close()

                file = open('{}'.format(conf_fileloc), 'w')
                file.write(text)
                file.close()

                # Rename the file
                os.rename('{}{}.txt'.format(data_folder, SELECTED), '{}{}.txt'.format(data_folder, new_name))

                SELECTED = new_name

        rename_button.config(text='R', command=rename_cat)
        rename_button.pack(side=tk.LEFT)

        pers_button = tk.Button(tool_frame, text='Pers', command=lambda: persistent_mode(self, pers_button))
        pers_button.pack(side=tk.RIGHT)

        text_frame = tk.Frame(self)
        text_frame.pack(side=tk.TOP)

        self.text_area = tk.Text(text_frame)
        self.text_area.config(font=OPT['TEXT_FONT'], bg=OPT['TEXT_BG'], bd=0)
        self.text_area.config(height=CATS[var.get()][0], width=CATS[var.get()][1])
        self.text_area.insert(1.0, CATS[var.get()][2])
        self.text_area.pack()

    def save(self):
        # Save the current category open and write the data in the files
        CATS[SELECTED] = (CATS[SELECTED][0], CATS[SELECTED][1], self.text_area.get(1.0, tk.END))
        for cat in CAT_DROP:
            file = open('{}{}.txt'.format(data_folder, cat), 'w')
            file.write(CATS[cat][2])
            file.close()

if __name__ == '__main__':

    print('INFO: Loading configuration info')
    if not load_conf():
        print('ERROR: Failed to load configuration info. Exiting')
        sys.exit()

    window = MainWindow()

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))
    window.bind('<Control-S>', lambda event: on_save(window))
    window.bind('<Control-s>', lambda event: on_save(window))

    window.iconphoto(True, tk.PhotoImage(file='./icon.gif'))
    window.mainloop()
