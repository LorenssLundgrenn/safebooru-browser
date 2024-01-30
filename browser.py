from PIL import ImageTk
import tkinter as tk
import math
import threading
from concurrent import futures
from datetime import datetime
import traceback

import util
from image_viewer import ImageViewer
from tab import Tab

class Browser(Tab):
    def __init__(self, app):
        super().__init__(app)
        self.create_button("Browser")
        self.__init_variables()
        self.__init_top_frame()
        self.__init_content_frame()
        self.__init_bottom_frame()

        self.update_thumbnail_size_text()
        self.update_page_text()
        self.update_limit_text()
        self.update_entry()

    def __init_variables(self):
        self.win_size = util.get_widget_size(self.app.window)
        self.executor = futures.ThreadPoolExecutor(max_workers=6)
        self.futures = {}
        self.cancel_load = False
        self.image_pad = 5
        self.prompt = ""
        self.page = 0
        self.limit = 12
        self.thumbnail_size = 200
        self.post_cache = {}
        self.active_posts = []
        self.thumbnail_widgets = {}
        self.thumbnail_columns = 1
        self.thumnail_rows = 1
        self.can_search = True

    def __init_top_frame(self):
        self.top_frame = tk.Frame(master = self.app.body_frame)

        self.search_entry = tk.Entry(master = self.top_frame)
        self.search_button = tk.Button(
            text = "Search",
            master = self.top_frame,
            command = self.on_search
        )

    def __del__(self):
        self.cancel_thumbnail_load()

    def __init_content_frame(self):
        self.content_frame = tk.Frame(master = self.app.body_frame)
        self.content_frame.pack_propagate(False)
        self.thumbnail_canvas = tk.Canvas(master = self.content_frame)
        self.thumbnail_frame = tk.Frame(
            master = self.thumbnail_canvas
        )
        self.scrollbar = tk.Scrollbar(
            master = self.content_frame,
            orient = tk.VERTICAL,
            width = 17,
            command = self.thumbnail_canvas.yview
        )
        self.thumbnail_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

    def __init_bottom_frame(self):
        self.bottom_frame = tk.Frame(master = self.app.body_frame)

        self.thumbnail_size_text = tk.Label(
            master = self.bottom_frame
        )
        self.thumbnail_size_entry = tk.Entry(
            master = self.bottom_frame,
            width = 6
        )

        self.page_up_button = tk.Button(
            text = ">>",
            master = self.bottom_frame,
            command = lambda: self.set_page(self.page+1)
        )

        self.page_down_button = tk.Button(
            text = "<<",
            master = self.bottom_frame,
            command = lambda: self.set_page(self.page-1)
        )

        self.page_entry = tk.Entry(
            master = self.bottom_frame,
            width = 6
        )
        self.page_text = tk.Label(
            master = self.bottom_frame
        )

        self.limit_entry = tk.Entry(
            master = self.bottom_frame,
            width = 6
        )
        self.limit_text = tk.Label(
            master = self.bottom_frame
        )

    def focus(self):
        self.bind_widgets()
        self.pack_widgets()

    def unfocus(self):
        self.unbind_widgets()
        self.forget_widgets()

    def bind_widgets(self):
        self.app.window.bind("<Configure>", lambda _: self.on_configure())
        self.search_entry.bind("<Return>", lambda _: self.on_search())
        self.thumbnail_size_entry.bind(
            "<Return>", lambda _:
            self.set_thumbnail_size(int(self.thumbnail_size_entry.get()))
        )
        self.scrollbar.bind_all("<MouseWheel>", self.on_mousewheel)
        self.page_entry.bind("<Return>", lambda _: 
            self.set_page(int(self.page_entry.get())-1)
        )
        self.limit_entry.bind("<Return>", lambda _: 
            self.set_limit(int(self.limit_entry.get()))
        )

    def unbind_widgets(self):
        self.app.window.unbind("<Configure>")
        self.search_entry.unbind("<Return>")
        self.scrollbar.unbind_all("<MouseWheel>")
        self.thumbnail_size_entry.unbind("<Return>")
        self.page_entry.unbind("<Return>")
        self.limit_entry.unbind("<Return>")

    def pack_widgets(self):
        #pack top frame widgets
        self.top_frame.pack(side="top")
        self.search_entry.pack(
            side="left", 
            padx=5, pady=5
        )
        self.search_button.pack(
            side="right", 
            padx=5, pady=5
        )

        #pack content frame widgets
        self.content_frame.pack(expand=True, fill=tk.BOTH)
        self.thumbnail_canvas.pack(side="left", expand=True, fill=tk.BOTH)
        self.thumbnail_canvas.create_window(
            (0, 0), window = self.thumbnail_frame,
            anchor = tk.NW
        )
        self.scrollbar.pack(side="left", fill=tk.Y)

        #pack bottom frame widgets
        self.bottom_frame.pack(side="bottom", fill=tk.X)
        self.thumbnail_size_text.pack(side="left")
        self.thumbnail_size_entry.pack(side="left")
        self.page_up_button.pack(side="right")
        self.page_down_button.pack(side="right")
        self.page_entry.pack(side="right")
        self.page_text.pack(side="right")
        self.limit_entry.pack(side="right")
        self.limit_text.pack(side="right")

    def forget_widgets(self):
        util.forget_widgets(self.top_frame)
        util.forget_widgets(self.content_frame)
        util.forget_widgets(self.bottom_frame)
        self.top_frame.pack_forget()
        self.content_frame.pack_forget()
        self.bottom_frame.pack_forget()

    def set_limit(self, limit):
        if (limit > 0):
            self.limit = limit
            self.update_limit_text()
            self.set_page(0)

    def set_page(self, page):
        if (page >= 0):
            self.page = page
            self.update_page_text()
            self.search()

    def set_thumbnail_size(self, size):
        if (size >= 100 and size <= 300):
            self.thumbnail_size = size
            self.update_thumbnail_size_text()
            self.resize_thumbnails()

    def update_limit_text(self):
        self.limit_text["text"] = f"Limit [{self.limit}]: "

    def update_page_text(self):
        self.page_text["text"] = f"Page [{self.page+1}]: "

    def update_thumbnail_size_text(self):
        self.thumbnail_size_text["text"] = f"Size [{self.thumbnail_size}]: "

    def update_entry(self):
        win_width = util.get_widget_size(self.app.window)[0]
        self.search_entry["width"] = math.floor(win_width / 10)

    def delete_future(self, id):
        if (id in self.futures):
            del self.futures[id]

    def cancel_future(self, id):
        if (id in self.futures):
            self.futures[id].cancel
    
    def destroy_thumbnails(self):
        self.cancel_thumbnail_load()
        self.thumbnail_widgets = {}
        util.destroy_widgets(self.thumbnail_frame)

    def cancel_thumbnail_load(self):
        for post_id in self.active_posts:
            self.cancel_future(post_id)

    def load_thumbnails(self):
        for post_id in self.active_posts:
            future = self.executor.submit(self.load_thumbnail, post_id)
            self.futures[post_id] = future

    def load_thumbnail(self, post_id):
        post = self.post_cache[post_id]
        if (not "@thumbnail_image" in post.keys()):
            preview_url = post["@preview_url"]
            pil_image = util.download_image(preview_url)
            self.post_cache[post_id]["@thumbnail_image"] = pil_image
        self.create_thumbnail_widget(post_id)

    def create_thumbnail_widgets(self):
        for order in self.thumbnail_widgets:
            self.create_thumbnail_widget(self.active_posts[order])

    def create_thumbnail_widget(self, post_id):
        post = self.post_cache[post_id]
        pil_image = post["@thumbnail_image"]
        dest_size = (self.thumbnail_size, self.thumbnail_size)
        thumbnail = util.resize_image(pil_image, dest_size)
        tk_image = ImageTk.PhotoImage(thumbnail)

        widget = tk.Button(
            master = self.thumbnail_frame,
            image = tk_image,
            command = lambda post=post: 
                self.open_imv_tab(post)
        )
        widget.image = tk_image
        order = self.active_posts.index(post_id)
        self.thumbnail_widgets[order] = widget
        self.delete_future(post_id)
        self.update_thumbnails()

    def arrange_thumbnail_widgets(self):
        for order in list(self.thumbnail_widgets.keys()):
            thumbnail = self.thumbnail_widgets[order]
            thumbnail.grid(
                row=int(order/self.thumbnail_columns), 
                column=math.floor(order%self.thumbnail_columns),
                padx=self.image_pad, 
                pady=self.image_pad
            )

    def calc_real_thumbnail_size(self):
        real_image_size = self.thumbnail_size + self.image_pad*2
        return real_image_size

    def update_thumbnail_columns(self):
        canvas_width, _ = util.get_widget_size(self.thumbnail_canvas)
        canvas_width -= int(self.scrollbar["width"])
        possible_columns = max(
            math.floor(
                canvas_width / self.calc_real_thumbnail_size()
            ), 1
        )
        actual_columns = min(possible_columns, len(self.active_posts))
        actual_columns = max(actual_columns, 1)
        self.thumbnail_columns = actual_columns

    def update_thumbnail_grid_config(self):
        for column in range(self.thumbnail_columns):
            self.thumbnail_frame.grid_columnconfigure(
                column, 
                weight = 1,
                minsize = self.thumbnail_size
            )

    def create_thumbnails(self):
        self.destroy_thumbnails()
        self.load_thumbnails()

    def resize_thumbnails(self):
        self.destroy_thumbnails()
        self.create_thumbnail_widgets()

    def update_thumbnails(self):
        self.update_thumbnail_columns()
        self.update_thumbnail_grid_config()
        self.arrange_thumbnail_widgets()
        self.update_scrollregion()

    def update_scrollregion(self):
        self.thumbnail_canvas.configure(
            scrollregion=self.thumbnail_frame.bbox("all")
        )

    def extract_timestamp(self, key):
        created_at = self.post_cache[key].get("@created_at", "")
        return datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')

    def sort_active_posts(self):
        self.active_posts = sorted(
            self.active_posts, 
            key=self.extract_timestamp, 
            reverse=True
        )

    def retrieve_posts(self):
        self.active_posts = []
        posts = self.app.client.get_posts(
            tags = self.prompt,
            pid = self.page,
            limit = self.limit
        )
        for post in posts:
            post_id = post["@id"]
            self.active_posts.append(post_id)
            post_ids = self.post_cache.keys()
            if (post_id not in post_ids):
                self.post_cache[post_id] = post
        self.sort_active_posts()

    def search_thread(self):
        try:
            self.retrieve_posts()
            self.create_thumbnails()
        except Exception: traceback.print_exc()
        self.can_search = True

    def search(self):
        if (self.can_search):
            self.can_search = False
            thread = threading.Thread(
                target=self.search_thread
            )
            thread.start()

    def on_search(self):
        prev_prompt = self.prompt
        self.prompt = self.search_entry.get()
        if (self.prompt == prev_prompt):
            self.search()
        else: self.set_page(0)

    def open_imv_tab(self, post):
        thread = threading.Thread(
            target=self.app.add_tab,
            args=(ImageViewer, self.app, post)
        )
        thread.start()

    def handle_configure(self):
        self.update_thumbnails()

    def handle_immediate_configure(self):
        self.update_entry()

    def on_mousewheel(self, event):
        # this just works ¯\_(ツ)_/¯
        self.thumbnail_canvas.yview_scroll(-1 * (event.delta // 120), "units")