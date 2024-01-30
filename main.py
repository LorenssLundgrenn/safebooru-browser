import tkinter as tk
import os
import pickle

from browser import Browser
from image_viewer import ImageViewer
import const
from client import Client
import util

class App:
    def __init__(self):
        self.__init_variables()
        self.__init_frames()
        self.__init_popup_menus()
        self.bind_widgets()
        self.pack_widgets()

        self.add_tab(Browser, self)
        self.focus_tab(self.get_first_tab_id())

        self.window.mainloop()
        
        self.terminating = True
        self.save_archive()

    def __init_variables(self):
        self.window = tk.Tk()
        self.window.title("Safebooru Browser")
        self.window.geometry("900x600")
        self.window.minsize(*const.WINDOW_MIN_SIZE)

        self.client = Client()
        self.tabs = {}
        self.archive = {}
        self.focus_id = None
        self.last_tab_id = None
        self.terminating = False

        self.load_archive()

    def __init_frames(self):
        self.tab_frame = tk.Frame(master = self.window)
        self.body_frame = tk.Frame(master = self.window)

    def __init_popup_menus(self):
        """self.new_tab_menu = tk.Menu(self.window, tearoff=0)
        self.new_tab_menu.add_command(label = "Browser", 
            command=lambda: self.add_tab(Browser, self)
        )"""

        self.tab_frame_menu = tk.Menu(self.window, tearoff=0)
        self.tab_frame_menu.add_command(label="New Tab", 
            command=lambda: self.add_tab(Browser, self)
        )
        self.tab_frame_menu.add_command(label="Search by ID", 
            command=lambda: Popup(self)
        )

    def bind_widgets(self):
        self.tab_frame.bind("<Button-3>", 
            lambda event: self.tab_frame_menu.post(event.x_root, event.y_root)
        )

    def pack_widgets(self):
        self.tab_frame.pack(fill=tk.X)
        self.body_frame.pack(expand=True, fill=tk.BOTH)

    def add_tab(self, tab, *params):
        tab_instance = tab(*params)
        tab_id = tab_instance.id
        self.tabs[tab_id] = tab_instance
        self.focus_tab(tab_id)

    def focus_tab(self, id):
        if (not (id == self.focus_id) and self.tab_exists(id)):
            self.panic_toggle = False
            self.unfocus_tab(self.focus_id)
            self.tabs[id].focus()
            self.last_tab_id = self.focus_id
            self.focus_id = id

    def unfocus_tab(self, id):
        if (not (id == None) and self.tab_exists(id)):
            self.tabs[id].unfocus()

    def get_first_tab_id(self):
        return list(self.tabs.keys())[0]
    
    def tab_exists(self, id):
        return (id in list(self.tabs.keys()))

    def delete_tab(self, id):
        if (len(self.tabs) > 1 and self.tab_exists(id)):                
            is_current_tab = id == self.focus_id
            if (is_current_tab):
                self.tabs[id].unfocus()

            self.tabs[id].destroy()
            del self.tabs[id]
            if (is_current_tab):
                self.switch_after_delete()

    def switch_after_delete(self):
        if (self.tab_exists(self.last_tab_id)):
            self.focus_tab(self.last_tab_id)
            self.last_tab_id = self.get_first_tab_id()
        else:
            id = self.get_first_tab_id()
            self.last_tab_id = id
            self.focus_tab(id)

    def load_archive(self):
        util.assert_file_exists(const.ARCHIVE_PATH)
        with open(const.ARCHIVE_PATH, "rb") as f:
            binary = f.read()
            if (binary): 
                self.archive = pickle.loads(binary)
        
    def save_archive(self):
        util.assert_file_exists(const.ARCHIVE_PATH)
        data = pickle.dumps(self.archive)
        with open(const.ARCHIVE_PATH, "wb") as f:
            f.write(data)

class Popup:
    def __init__(self, app):
        self.app = app

        x, y = app.window.winfo_pointerxy()
        self.popup = tk.Toplevel(self.app.window)
        self.popup.geometry(f"100x50+{x}+{y}")
        self.popup.overrideredirect(True)
        self.popup.title("Input Popup")

        self.frame = tk.Frame(
            master=self.popup,
            bd=2, relief=tk.SOLID,
        )
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.entry = tk.Entry(
            master=self.frame,
            width=150
        )
        self.entry.bind("<Return>", lambda _: self.destroy())
        self.entry.pack()

        self.button = tk.Button(
            master=self.frame,
            command=lambda: self.popup.destroy(),
            text="Cancel"
        )
        self.button.pack(anchor=tk.E)

    def destroy(self):
        id = self.entry.get()
        if (id.isdigit()):
            post = self.app.client.get_post_by_id(self.entry.get())
            if (post): self.app.add_tab(ImageViewer, self.app, post)
        self.popup.destroy()

App()