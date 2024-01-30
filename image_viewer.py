from PIL import ImageTk
import tkinter as tk
from tkinter import filedialog
import threading

import util
import const
from tab import Tab

class ImageViewer(Tab):
    def __init__(self, app, post):
        super().__init__(app)
        self.create_button("Imv")
        self.post = post

        self.__init_variables()
        self.__init_context_frame()
        self.__init_content_frame()
        self.__init_top_frame()
        self.__init_bottom_frame()
        self.__init_popup_menus()

    def __init_variables(self):
        self.tags = self.post["@tags"].strip().split(' ')
        self.image_loaded = False
        self.comments_loaded = False
        self.image = None
        self.comments = []
        self.comment_widgets = []

        thread = threading.Thread(
            target=self.__init_image
        )
        thread.start()

    def __init_image(self):
        self.image = util.download_image(self.post["@file_url"])
        self.image_loaded = True
        self.update_widgets()

    def __init_context_frame(self):
        self.context_frame = tk.Frame(master=self.app.body_frame)
        self.context_canvas = tk.Canvas(master=self.context_frame)
        self.context_canvas_frame = tk.Frame(
            master = self.context_canvas
        )
        self.context_canvas_window = self.context_canvas.create_window(
            (0, 0), window = self.context_canvas_frame,
            anchor = tk.NW
        )

        self.tags_label = tk.Label(
            master=self.context_canvas_frame,
            text="\n".join(self.tags),
            font=("Arial", 12),
            justify="left"
        )

        self.context_scrollbar = tk.Scrollbar(
            master = self.context_frame,
            orient = tk.VERTICAL,
            width = 17,
            command = self.context_canvas.yview
        )
        self.context_canvas.configure(
            yscrollcommand=self.context_scrollbar.set
        )

    def __init_content_frame(self):
        self.content_frame = tk.Frame(master = self.app.body_frame)
        self.canvas = tk.Canvas(master = self.content_frame)
        self.canvas_frame = tk.Frame(
            master = self.canvas
        )
        self.canvas_frame_window = self.canvas.create_window(
            (0, 0), window = self.canvas_frame,
            anchor = tk.NW
        )

        self.scrollbar = tk.Scrollbar(
            master = self.content_frame,
            orient = tk.VERTICAL,
            width = 17,
            command = self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

    def __init_top_frame(self):
        self.top_frame = tk.Frame(master=self.canvas_frame)
        self.image_label = tk.Label(
            master = self.top_frame
        )

    def __init_bottom_frame(self):
        self.bottom_frame = tk.Frame(master=self.canvas_frame)
        thread = threading.Thread(
            target=self.__init_comments
        )
        thread.start()

    def __init_comments(self):
        self.comments = self.app.client.get_comments(
            self.post["@id"]
        )
        for comment in self.comments:
            text_body = comment["@body"]
            comment_text = tk.Label(
                master=self.bottom_frame,
                text=text_body
            )
            self.comment_widgets.append(comment_text)
        self.comments_loaded = True
        self.pack_comments()
        self.update_widgets()

    def __init_popup_menus(self):
        self.image_menu = tk.Menu(self.app.window, tearoff=0)
        self.image_menu.add_command(label="Save As", command=self.save_as)
        self.image_menu.add_command(label="Download", command=self.download_image)
        self.image_menu.add_command(label="Archive", command=self.archive)

    def focus(self):
        self.bind_widgets()
        self.pack_widgets()
        self.update_widgets()

    def unfocus(self):
        self.unbind_widgets()
        self.forget_widgets()

    def bind_widgets(self):
        self.tags_label.bind("<MouseWheel>", self.on_context_mousewheel)
        self.image_label.bind("<MouseWheel>", self.on_content_mousewheel)
        self.image_label.bind("<Button-3>", 
            lambda event: self.image_menu.post(event.x_root, event.y_root)
        )
        self.app.window.bind("<Configure>", lambda _: self.on_configure())

    def unbind_widgets(self):
        self.tags_label.unbind("<MouseWheel>")
        self.image_label.unbind("<MouseWheel>")
        self.image_label.unbind("<Button-3>")
        self.app.window.unbind("<Configure>")

    def pack_widgets(self):
        self.context_frame.pack(side="left", fill=tk.Y)
        self.context_canvas.pack(side="left", fill=tk.Y) 
        self.tags_label.pack(side="top", anchor=tk.NW)
        self.context_scrollbar.pack(side="left", fill=tk.Y)

        self.content_frame.pack(side="left", expand=True, fill=tk.BOTH)
        self.canvas.pack(side="left", expand=True, fill=tk.BOTH) 
        self.scrollbar.pack(side="left", fill=tk.Y)

        self.top_frame.pack(expand=True, fill=tk.BOTH)
        self.image_label.pack(anchor=tk.CENTER)

        self.bottom_frame.pack()
        self.pack_comments()

    def pack_comments(self):
        for comment in self.comment_widgets:
            comment.pack(side="top", 
                expand=True, fill=tk.BOTH, 
                anchor=tk.CENTER
            )

    def forget_widgets(self):
        util.forget_widgets(self.content_frame)
        util.forget_widgets(self.context_frame)
        self.content_frame.pack_forget()
        self.context_frame.pack_forget()

    def update_widgets(self):
        self.update_tags_label()
        self.update_context_canvas()

        if (self.image_loaded):
            self.update_image_label()
        if (self.comments_loaded):
            self.update_comment_widgets()

        self.update_canvas()
        self.update_canvas_frame_window()
        self.arrange_canvas_items()

    def update_tags_label(self):
        width, _ = util.get_widget_size(self.app.body_frame)
        width *= 0.25
        if (width < 150): width = 150
        self.tags_label.configure(wraplength=width)

    def update_context_canvas(self):
        width, _ = util.get_widget_size(self.tags_label)
        self.context_canvas.configure(width=width)
        self.context_canvas.config(
            scrollregion=self.context_canvas.bbox("all") 
        )

    def update_image_label(self):
        image = util.resize_image(self.image, 
            util.get_widget_size(self.content_frame)
        )
        image_tk = ImageTk.PhotoImage(image)
        self.image_label.config(image=image_tk)
        self.image_label.image = image_tk

    def update_comment_widgets(self):
        for widget in self.comment_widgets:
            length, _ = util.get_widget_size(self.content_frame)
            widget.configure(wraplength=length*0.90)

    def update_canvas(self):
        self.canvas.config(
            scrollregion=self.canvas.bbox("all") 
        )

    def update_canvas_frame_window(self):
        canvas_width, _ = util.get_widget_size(self.canvas)
        item = self.canvas_frame_window
        self.canvas.itemconfigure(item, width=canvas_width)

    def arrange_canvas_items(self):
        canvas_width, _ = util.get_widget_size(self.canvas)
        item = self.canvas_frame_window

        bbox = self.canvas.bbox(item)
        item_width = bbox[2] - bbox[0]

        x = (canvas_width - item_width) / 2
        self.canvas.move(item, x - bbox[0], 0)

    def handle_configure(self):
        print("hanlde configure")
        self.update_widgets()

    def download_image(self):
        fname = self.post["@file_url"].split("/")[-1]
        util.assert_dir_exists(const.DEFAULT_DOWNLOAD_DIR)
        self.image.save(f"{const.DEFAULT_DOWNLOAD_DIR}{fname}")

    def save_as(self):
        fname = self.post["@file_url"].split("/")[-1]
        dir = filedialog.askdirectory()
        if (dir): self.image.save(f"{dir}/{fname}")

    def archive(self):
        id = self.post["@id"]
        self.app.archive[id] = self.post

    def on_context_mousewheel(self, event):
        self.context_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_content_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")