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
    'DEF_SIZE': (-1, -1),
    'TEXT_FONT': -1,
    'LABEL_FONT': -1,
    'TEXT_BG': -1,
    'PERSISTENT': False
}

# Holds settings about each individual category
CATS = {
    # Name: (Width, height, Text)
}

# This list will be used by the dropdown option menu
CAT_DROP = []
SELECTED = ''


def load_conf():
    print('INFO: Loading configuration info')
    with open('{}'.format(conf_fileloc), 'r') as file:
        for raw_line in file:
            line = raw_line.rstrip()
            if len(line) > 0 and line[0] is not '#':
                sett = line.split(' ')
                if sett[0] == 'DefaultSize':
                    OPT['DEF_SIZE'] = (int(sett[1]), int(sett[2]))
                elif sett[0] == 'TextFont':
                    OPT['TEXT_FONT'] = (sett[1], int(sett[2]))
                elif sett[0] == 'LabelFont':
                    OPT['LABEL_FONT'] = (sett[1], int(sett[2]))
                elif sett[0] == 'TextAreaBg':
                    OPT['TEXT_BG'] = sett[1]
                elif sett[0] == 'Cat':
                    if len(sett) == 4:
                        setting = sett
                    else:
                        setting = [sett[0], ' '.join(sett[i] for i in range(1, len(sett) - 2)), sett[-2], sett[-1]]
                    text = ''
                    with open('{}{}.txt'.format(data_folder, setting[1]), 'r') as t_file:
                        for raw_t_line in t_file:
                            text += raw_t_line
                    CATS[setting[1]] = (setting[2], setting[3], text)
    file.close()

    # Check if everything was configured correctly
    for key, value in OPT.items():
        if value is -1:
            print('ERROR: Failed to load configuration info. Exiting')
            return False

    CAT_DROP.append('')
    for key, _ in CATS.items():
        CAT_DROP.append(key)
    print('INFO: Loaded successfully. Starting application')
    return True


def persistent_mode(root, button):
    if not OPT['PERSISTENT']:
        root.wm_attributes('-topmost', 1)
        OPT['PERSISTENT'] = True
        button.config(style='PersPressed.TButton')
    else:
        root.wm_attributes('-topmost', 0)
        OPT['PERSISTENT'] = False
        button.config(style='PersUnpressed.TButton')


def on_close(root):
    # What happens when there is a close window event
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        on_save(root)
        print('INFO: Shutting down the application')
        root.quit()


def on_save(root):
    print('INFO: Saving current state')
    CATS[SELECTED] = (root.winfo_width(), root.winfo_height(), root.text_area.get(1.0, 'end-1c'))
    for cat in CAT_DROP:
        if cat != '':

            # Save on the text data
            file = open('{}{}.txt'.format(data_folder, cat), 'w')
            file.write(CATS[cat][2])
            file.close()

            # Update the .conf file
            text = ''
            with open('{}'.format(conf_fileloc), 'r') as file:
                for raw_line in file:
                    to_write = raw_line
                    line = raw_line.rstrip()
                    if len(line) > 0 and line[0] is not '#':
                        setting = line.split(' ')
                        if setting[0] == 'Cat':
                            cat = ' '.join(setting[i] for i in range(1, len(setting) - 2))
                            if cat == SELECTED:
                                to_write = 'Cat {} {} {}\n'.format(SELECTED, CATS[SELECTED][0], CATS[SELECTED][1])
                    text += to_write
            file.close()

            file = open('{}'.format(conf_fileloc), 'w')
            file.write(text)
            file.close()


def on_change_cat(root, new_c):
    global SELECTED

    # Save
    on_save(root)

    #
    print('INFO: Switching from "{}" to "{}"'.format(SELECTED, new_c))

    # Load the new text area
    root.geometry('{}x{}'.format(CATS[new_c][0], CATS[new_c][1]))
    root.text_area.delete(1.0, tk.END)
    root.text_area.insert(1.0, CATS[new_c][2])

    # Update the current category
    SELECTED = new_c


def on_new_cat(root):
    global SELECTED

    # Get the new name
    while True:
        new_name = simpledialog.askstring('New Name', 'Enter the new name')
        if new_name in CAT_DROP:
            messagebox.showerror('Error', 'There is already a category named "{}"'.format(new_name))
        elif new_name != '':
            break

    if new_name is not None:

        new_name = ' '.join(string for string in new_name.split())
        print('INFO: Creating new category with name "{}"'.format(new_name))

        # Prepare the new text area
        root.geometry('{}x{}'.format(OPT['DEF_SIZE'][0], OPT['DEF_SIZE'][1]))
        root.text_area.delete(1.0, tk.END)

        # Update the category list
        CAT_DROP.append(new_name)

        # Add a new element in te category info
        CATS[new_name] = (CATS[SELECTED][0], CATS[SELECTED][1], '')
        root.var.set(new_name)
        root.droplist['menu'].delete(0, tk.END)
        for cat in CAT_DROP:
            if cat != '':
                root.droplist['menu'].add_command(label=cat,
                                                  command=tk._setit(root.var, cat, lambda n: on_change_cat(root, n)))

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


def on_rename_cat(root):
    global SELECTED

    # Get the new name
    while True:
        new_name = simpledialog.askstring('New Name', 'Enter the new name')
        if new_name in CAT_DROP:
            messagebox.showerror('Error', 'There is already a category named "{}"'.format(new_name))
        elif new_name != '':
            break

    # If the user did not press cancel
    if new_name is not None:
        new_name = ' '.join(string for string in new_name.split())
        print('INFO: Renaming "{}" to "{}"'.format(SELECTED, new_name))
        # Update the list that is used by the optionmenu
        for index in range(len(CAT_DROP)):
            if CAT_DROP[index] == SELECTED:
                CAT_DROP[index] = new_name

        # Update the dictionary and the option menu
        CATS[new_name] = CATS.pop(SELECTED)
        root.var.set(new_name)
        root.droplist['menu'].delete(0, tk.END)
        for cat in CAT_DROP:
            if cat != '':
                root.droplist['menu'].add_command(label=cat,
                                                  command=tk._setit(root.var, cat, lambda n: on_change_cat(root, n)))

        # Update the .conf file
        text = ''
        with open('{}'.format(conf_fileloc), 'r') as file:
            for raw_line in file:
                to_write = raw_line
                line = raw_line.rstrip()
                if len(line) > 0 and line[0] is not '#':
                    setting = line.split(' ')
                    if setting[0] == 'Cat':
                        cat = ' '.join(setting[i] for i in range(1, len(setting) - 2))
                        if cat == SELECTED:
                            to_write = 'Cat {} {} {}\n'.format(new_name, setting[-2], setting[-1])
                text += to_write
        file.close()

        file = open('{}'.format(conf_fileloc), 'w')
        file.write(text)
        file.close()

        # Rename the file
        os.rename('{}{}.txt'.format(data_folder, SELECTED), '{}{}.txt'.format(data_folder, new_name))

        SELECTED = new_name


def on_remove_cat(root):
    global SELECTED

    if messagebox.askokcancel("Delete", "Permanently delete this category?"):
        print('INFO: Removing "{}" category'.format(SELECTED))
        to_remove = SELECTED
        emptied = False

        # Update the list that is used by the optionmenu
        CAT_DROP.remove(to_remove)
        if len(CAT_DROP) == 1:
            CAT_DROP.append('Default')

        # Update the dictionary
        CATS.pop(to_remove)
        if not CATS:
            emptied = True
            CATS['Default'] = (8, 25, '')

        # Update the optionmenu
        SELECTED = CAT_DROP[1]
        root.var.set(SELECTED)
        root.droplist['menu'].delete(0, tk.END)
        for cat in CAT_DROP:
            if cat != '':
                root.droplist['menu'].add_command(label=cat,
                                                  command=tk._setit(root.var, cat, lambda n: on_change_cat(root, n)))

        # Update the text area
        root.geometry('{}x{}'.format(CATS[SELECTED][0], CATS[SELECTED][1]))
        root.text_area.delete(1.0, tk.END)
        root.text_area.insert(1.0, CATS[SELECTED][2])

        # Update the .conf file
        text = ''
        with open('{}'.format(conf_fileloc), 'r') as file:
            for raw_line in file:
                to_write = raw_line
                line = raw_line.rstrip()
                if len(line) > 0 and line[0] is not '#':
                    setting = line.split(' ')
                    if setting[0] == 'Cat':
                        cat = ' '.join(setting[i] for i in range(1, len(setting)-2))
                        if cat == to_remove:
                            if emptied:
                                to_write = 'Cat Default 15 40\n'
                            else:
                                to_write = ''
                text += to_write
        file.close()

        file = open('{}'.format(conf_fileloc), 'w')
        file.write(text)
        file.close()

        # Delete the file
        os.remove('{}{}.txt'.format(data_folder, to_remove))
        if emptied:
            file = open('{}{}.txt'.format(data_folder, SELECTED), 'w+')
            file.write('')
            file.close()


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        global SELECTED
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, 'PyNotes')

        # The style of ttk stuff
        ttk_style = ttk.Style()
        ttk_style.configure('AddRemRen.TButton', width=2)
        ttk_style.configure('PersUnpressed.TButton', width=4, relief=tk.RAISED)
        ttk_style.configure('PersPressed.TButton', width=4, relief=tk.SUNKEN)

        # The tool frame will be hodling anything meta
        tool_frame = tk.Frame(self)
        tool_frame.pack(side=tk.TOP, fill=tk.X)

        # Creates a new category
        new_cat_button = ttk.Button(tool_frame)
        new_cat_button.config(text='+', style='AddRemRen.TButton', command=lambda: on_new_cat(self))
        new_cat_button.pack(side=tk.LEFT)

        # Deletes the current category
        remove_button = ttk.Button(tool_frame)
        remove_button.config(text='-', style='AddRemRen.TButton', command=lambda: on_remove_cat(self))
        remove_button.pack(side=tk.LEFT)

        # The category droplist
        self.var = tk.StringVar()
        self.droplist = ttk.OptionMenu(tool_frame, self.var, *CAT_DROP,
                                       command=lambda new_c: on_change_cat(self, new_c))
        self.var.set(CAT_DROP[1])
        SELECTED = self.var.get()
        self.droplist.pack(side=tk.LEFT)

        # Renames the current category
        rename_button = ttk.Button(tool_frame)
        rename_button.config(text='R', style='AddRemRen.TButton', command=lambda: on_rename_cat(self))
        rename_button.pack(side=tk.LEFT)

        # Switches between persistent and non-persistent
        pers_button = ttk.Button(tool_frame, text='Pers', style='PersUnpressed.TButton',
                                 command=lambda: persistent_mode(self, pers_button))
        pers_button.pack(side=tk.RIGHT)

        text_frame = tk.Frame(self, width=400, height=1000)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(text_frame)
        self.text_area.config(font=OPT['TEXT_FONT'], bg=OPT['TEXT_BG'], bd=0)
        self.text_area.config(height=CATS[self.var.get()][0], width=CATS[self.var.get()][1])
        self.text_area.insert(1.0, CATS[self.var.get()][2])
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Set the size of the window
        self.geometry('{}x{}'.format(CATS[SELECTED][0], CATS[SELECTED][1]))


if __name__ == '__main__':

    if not load_conf():
        sys.exit()

    window = MainWindow()

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))
    window.bind('<Control-S>', lambda event: on_save(window))
    window.bind('<Control-s>', lambda event: on_save(window))

    window.iconphoto(True, tk.PhotoImage(file='./icon.gif'))
    window.mainloop()
