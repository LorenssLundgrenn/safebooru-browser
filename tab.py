import tkinter as tk
import uuid

import util

class Tab:
    def __init__(self, app):
        self.app = app
        self.id = uuid.uuid4()
        self.menu = tk.Menu(self.app.window, tearoff=0)
        self.menu.add_command(label="Close", 
            command=lambda id=self.id: self.app.delete_tab(id)
        )

        self.win_size = util.get_widget_size(self.app.window)
        self.after_configure_id = None
        self.configure_delay = 200

    def destroy(self):
        self.app = None
        self.menu.destroy()
        self.button.destroy()

    def create_button(self, tab_name):
        self.button = tk.Button(
            master=self.app.tab_frame,
            text=tab_name,
            command=lambda: self.app.focus_tab(self.id)
        )
        self.button.pack(side="left")
        self.button.bind("<Button-3>", 
            lambda event: self.menu.post(event.x_root, event.y_root)
        )

    def focus(self): pass
    def unfocus(self): pass

    #wait to handle window resize, delay resize operation when a
    #resize operation is requested within that time
    def on_configure(self):
        win_size_now = util.get_widget_size(self.app.window)
        if not (win_size_now == self.win_size):
            self.win_size = win_size_now

            self.handle_immediate_configure()

            if (self.after_configure_id): 
                self.app.window.after_cancel(self.after_configure_id)
            self.after_configure_id = self.app.window.after(
                self.configure_delay, 
                lambda: self.handle_configure()
            )

    def handle_immediate_configure(self): pass
    def handle_configure(self): pass