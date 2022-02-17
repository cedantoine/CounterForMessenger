import os
import json
import glob
from os.path import exists
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import timedelta, datetime
# from tkhtmlview import HTMLLabel

userMess = 0
allMess = 0
pathDir = ""
username = ""


# Create a loading window
def openLoading(lenNum, root):
    Window = Toplevel(root)
    Window.title("Ładowanie...")
    center_window(300, 100, Window)
    Window.resizable(False, False)
    Window.focus_set()
    Window.grab_set()
    progress = ttk.Progressbar(Window, orient="horizontal", maximum=int(lenNum), length=200, mode="determinate")
    label = ttk.Label(Window, text="Ładowanie konwersacji 0/" + str(lenNum))
    progress.pack(side=TOP)
    label.pack(side=TOP)
    # Window.protocol("WM_DELETE_WINDOW", disable_event)
    return progress, label, Window


# Disable event
def disable_event():
    pass


# Count messages per person
def countPerPerson(data, path, uname):
    global userMess
    global allMess
    totalNum = 0
    callTime = 0
    participants = []
    result = glob.glob(path + data + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for msg in data['messages']:
                totalNum += 1
                if msg['sender_name'] == uname:
                    userMess += 1
                allMess += 1
                if msg['type'] == 'Call':
                    callTime += msg['call_duration']
            for k in data['participants']:
                if k['name'].encode('iso-8859-1').decode('utf-8') not in participants:
                    participants.append(k['name'].encode('iso-8859-1').decode('utf-8'))
            title = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
    if thread_type == "Regular":
        thread_type = "Czat Prywatny"
    elif thread_type == "RegularGroup":
        thread_type = "Grupa"

    return title, participants, thread_type, totalNum, callTime


# Sort by number
def treeview_sort_msg(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(key=lambda t: int(t[0]), reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col,
               command=lambda: treeview_sort_msg(tv, col, not reverse))


# Sort by string
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


# Search values from table
def search(search_entry, t):
    query = search_entry.get()
    selections = []
    for child in t.get_children():
        for i in t.item(child)['values']:
            if str(i).find(query) != -1:
                selections.append(child)
    print('znaleziono: ', len(selections))
    t.selection_set(selections)


# Unselect all items in table
def unselect(t):
    t.selection_remove(t.selection())


# Count all messages
def countAll(path, uname, t, root):
    t.delete(*t.get_children())
    x, label, window = openLoading(len(os.listdir(path)), root)
    for i in os.listdir(path):
        try:
            conf = countPerPerson(i, path, uname)
            t.insert(parent='', index=END, values=(conf[0], conf[1], conf[2], conf[3], conf[4], i))
        except Exception as e:
            print(e)
            continue
        try:
            x['value'] += 1
            x.update()
            label['text'] = "Ładowanie konwersacji " + str(int(x['value'])) + "/" + str(len(os.listdir(path)))
            label.update()
        except:
            continue
    window.destroy()
    t.heading('msg', command=lambda _col='msg': treeview_sort_msg(t, _col, False))
    t.heading('name', command=lambda _col='name': treeview_sort_column(t, _col, False))
    t.heading('type', command=lambda _col='type': treeview_sort_column(t, _col, False))
    t.heading('call', command=lambda _col='call': treeview_sort_msg(t, _col, False))


# Select directory with data
def selectDir(label):
    global pathDir
    pathDir = filedialog.askdirectory() + "/"
    label.config(text=pathDir)


# Load information about user
def loadInfo():
    global username
    global pathDir
    with open("config.txt", "r") as f:
        username = f.readline().strip()
        pathDir = f.readline()
        f.close()


# Save information about user
def saveInfo(userName, where):
    global username
    global pathDir
    username = userName.get()
    with open("config.txt", "w") as f:
        f.write(f"{username}\n{pathDir}")
        f.close()
        where.destroy()
        Main()


# Save information about user
def updateInfo(userName, window):
    global username
    global pathDir
    username = userName.get()
    with open("config.txt", "w") as f:
        f.write(f"{username}\n{pathDir}")
        f.close()
        window.destroy()
        messagebox.showinfo("Zapisano", "Zapisano ustawienia, aby zastosowac zmiany kliknij przycisk pokaż wiadomości")


# Center window on screen
def center_window(width=300, height=200, win=None):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    win.geometry('%dx%d+%d+%d' % (width, height, x, y))


# Show window on first time using app
def firstTime():
    window = Tk()
    window.title("Konfiguracja początkowa")
    window.iconbitmap(r'assets\CFM.ico')
    center_window(600, 400, window)
    window.focus_set()
    window.grab_set()
    Label(window, text="Konfiguracja początkowa:", font=("Ariel", 24)).pack(side=TOP, pady=20)
    Label(window, text="Wskaż folder inbox z danymi:").pack(side=TOP, pady=5)
    label = Label(window, text=pathDir)
    label.pack(side=TOP, pady=5)
    ttk.Button(window, text="Otwórz ekspolator plików", padding=5, command=lambda: selectDir(label)).pack(side=TOP,
                                                                                                          pady=5)
    Label(window, text="Wpisz imię i nazwisko z facebooka(dokładnie):").pack(side=TOP, pady=15)
    username_entry = ttk.Entry(window, width=25)
    username_entry.pack(side=TOP, pady=5)
    ttk.Button(window, text="Zapisz", padding=7, command=lambda: saveInfo(username_entry, window)).pack(side=TOP,
                                                                                                        pady=40)
    window.mainloop()


# Show settings window
def settings(root):
    Window = Toplevel(root)
    Window.iconbitmap(r'assets\CFM.ico')
    Window.title("Ustawienia")
    Window.focus_set()
    Window.grab_set()
    center_window(800, 600, Window)
    Label(Window, text="Wskaż folder inbox z danymi:").pack(side=TOP, pady=16)
    label = Label(Window, text=pathDir)
    label.pack(side=TOP, pady=15)
    ttk.Button(Window, text="Otwórz ekspolator plików", padding=5, command=lambda: selectDir(label)).pack(side=TOP,
                                                                                                          pady=5)
    Label(Window, text="Zmień imię i nazwisko z facebooka:").pack(side=TOP, pady=15)
    username_entry = ttk.Entry(Window, width=25)
    username_entry.pack(side=TOP, pady=5)
    username_entry.insert(0, username)
    ttk.Button(Window, text="Zapisz", padding=7, command=lambda: updateInfo(username_entry, Window)).pack(side=TOP, pady=40)


# Get messages from specified conversation
def getMessages(t):
    global pathDir
    messages = [0, 0, {}, 0, 0, 0]
    try:
        path = pathDir+str(t.item(t.selection())['values'][5])
    except:
        path = pathDir+str(t.item("I001")['values'][5])
    result = glob.glob(path + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for k in data['participants']:
                if k['name'].encode('iso-8859-1').decode('utf-8') not in messages[2].keys():
                    messages[2][k['name'].encode('iso-8859-1').decode('utf-8')] = 0
            for msg in data['messages']:
                messages[3] += 1
                if msg['type'] == 'Call':
                    messages[4] += msg['call_duration']
                if msg['sender_name'].encode('iso-8859-1').decode('utf-8') in messages[2].keys():
                    messages[2][msg['sender_name'].encode('iso-8859-1').decode('utf-8')] += 1
                else:
                    messages[2][msg['sender_name'].encode('iso-8859-1').decode('utf-8')] = 1
                messages[5] = msg['timestamp_ms']
            messages[0] = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
    if thread_type == "Regular":
        messages[1] = "Czat Prywatny"
    elif thread_type == "RegularGroup":
        messages[1] = "Grupa"
    return messages


# Show window with messages stats
def showStats(root, t):
    if t.item(t.selection())['values'] == '':
        return
    Window = Toplevel(root)
    Window.iconbitmap(r'assets\CFM.ico')
    Window.title("Statystyki")
    Window.focus_set()
    Window.grab_set()
    center_window(800, 600, Window)
    messages = getMessages(t)
    Label(Window, text="Statystyki wiadomości:").pack(side=TOP, pady=16)
    Label(Window, text="Nazwa: " + str(messages[0])).pack(side=TOP, pady=5)
    Label(Window, text="Typ konwersacji: " + str(messages[1])).pack(side=TOP, pady=5)
    if messages[1] == "Grupa":
        Label(Window, text="Wszyscy uczestnicy i wiadomości: "+str(len(messages[2]))).pack(side=TOP, pady=5)
        listbox = Listbox(Window, width=30, height=15)
        listbox.pack(side=TOP, pady=5)
        scrollbar = Scrollbar(Window)
        scrollbar.pack(side=RIGHT, fill=BOTH)
    else:
        Label(Window, text="Osoby i wiadomości:").pack(side=TOP, pady=5)
        listbox = Listbox(Window, width=30, height=2)
        listbox.pack(side=TOP, pady=5)
    for i in messages[2]:
        listbox.insert(END, i+" - "+str(messages[2][i]))
    Label(Window, text="Łączna liczba wiadomości: " + str(messages[3])).pack(side=TOP, pady=5)
    Label(Window, text="Łączna długość rozmów: " + str(timedelta(seconds=messages[4]))).pack(side=TOP, pady=5)
    Label(Window, text="Data pierwszej wiadomości: " + str(datetime.fromtimestamp(messages[5]/1000))).pack(side=TOP, pady=5)


# Show my profile window
def myProfile():
    window = Tk()
    window.title("Mój profil")
    window.iconbitmap(r'assets\CFM.ico')
    center_window(600, 400, window)
    window.focus_set()
    window.grab_set()
    Label(window, text="Moje dane:", font=("Ariel", 24)).pack(side=TOP, pady=20)
    Label(window, text="Imię i nazwisko: " + username).pack(side=TOP, pady=10)
    Label(window, text="Liczba konwersacji: " + str(len(os.listdir(pathDir)))).pack(side=TOP, pady=10)
    Label(window, text="Liczba wszystkich twoich wiadomości: " + str(userMess)).pack(side=TOP, pady=10)
    Label(window, text="Liczba wszystkich wiadomości: " + str(allMess)).pack(side=TOP, pady=10)
    ttk.Button(window, text="Zamknij", padding=7, command=window.destroy).pack(side=TOP, pady=40)
    window.mainloop()


# Show main window
def Main():
    root = Tk()
    root.title("Counter for messenger")
    root.iconbitmap(r'assets\CFM.ico')
    center_window(1224, 700, root)
    root.configure(background='#232323')
    s = ttk.Style()
    s.configure('Nav.TFrame', background='#131313')
    s.configure('Main.TFrame', background='#232323')
    s.configure('Custom.Treeview', background='#232323', foreground='#ffffff')
    nav = ttk.Frame(root, padding=20, style='Nav.TFrame')
    main = ttk.Frame(root, style='Main.TFrame')
    home_icon = PhotoImage(file='./assets/home.png')
    settings_icon = PhotoImage(file='./assets/settings.png')
    exit_icon = PhotoImage(file='./assets/exit.png')
    vis_icon = PhotoImage(file='./assets/visible.png')
    search_icon = PhotoImage(file='./assets/search.png')
    person_icon = PhotoImage(file='./assets/person.png')
    v = Scrollbar(main)
    t = ttk.Treeview(main, height=20, yscrollcommand=v.set, style='Custom.Treeview')
    t.column("#0", width=0, stretch=NO)
    t['columns'] = ('name', 'pep', 'type', 'msg', 'call')
    t.heading("name", text="Nazwa", anchor=CENTER)
    t.heading("pep", text="Uczestnicy", anchor=CENTER)
    t.heading("type", text="Typ", anchor=CENTER)
    t.heading("msg", text="Liczba wiadomości", anchor=CENTER)
    t.heading("call", text="Łączna długość rozmów", anchor=CENTER)
    t.bind("<Button-3>", lambda event: unselect(t))
    t.bind('<Double-1>', lambda event: showStats(root, t))
    ttk.Button(nav, image=home_icon, text="Strona główna", compound=LEFT, padding=5).pack(side=TOP, pady=10)
    ttk.Button(nav, image=vis_icon, text="Załaduj wiadomości", compound=LEFT, padding=5,
               command=lambda: countAll(pathDir, username, t, root)).pack(side=TOP, pady=10)
    search_entry = ttk.Entry(nav, width=15)
    search_entry.pack(side=TOP, pady=10)
    ttk.Button(nav, image=search_icon, text="Szukaj", compound=LEFT, command=lambda: search(search_entry, t)).pack(
        side=TOP, pady=10)
    ttk.Button(nav, image=exit_icon, text="Wyjście", compound=LEFT, padding=5, command=root.destroy).pack(side=BOTTOM)
    ttk.Button(nav, image=settings_icon, text="Ustawienia", compound=LEFT, padding=5,
               command=lambda: settings(root)).pack(side=BOTTOM, pady=15)
    ttk.Button(nav, image=person_icon, text="Mój profil", compound=LEFT, padding=5, command=myProfile).pack(side=BOTTOM)
    ttk.Label(main, text="Liczba wiadomości: ", foreground='#ffffff', background='#232323', font=('Arial', 15)).pack(
        side=TOP, pady=10)
    v.pack(side=RIGHT, fill=Y)
    t.pack(side=LEFT, fill=BOTH, expand=1)
    v.config(command=t.yview)
    nav.pack(side=LEFT, fill=Y)
    main.pack(side=RIGHT, fill=BOTH, expand=True)
    loadInfo()
    root.mainloop()


# Check if app is first time using
if __name__ == '__main__':
    file_exists = exists("config.txt")
    if file_exists:
        Main()
    else:
        firstTime()
