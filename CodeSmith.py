import customtkinter as ctk

# アプリ本体のクラス
class CodeSmithApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#1F1F1F")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("CodeSmithApp")
        self.geometry("600x400")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.bind("<Button>", self.click)

        self.FONT = ("Meiryo", 15)  # フォントの設定
        self.select_frame = None
        self.select_block = None

        #/ 左サイドバーのコード
        self.sidebar = ctk.CTkFrame(
            self,
            width=150,
            fg_color="#1F1F1F",
            border_color="#606060",
            border_width=1,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.blocks = [
            "row", "block", "text", "if", "while", "for", "true", "false", "none", "return", "function"
        ]

        for row in range(len(self.blocks) + 1):
            self.sidebar.grid_rowconfigure(row, weight=1)

        for block in self.blocks:
            btn = ctk.CTkButton(
                self.sidebar,
                text=block,
                font=self.FONT,
                command=lambda b=block: self.add_block_to_canvas(b)
            )
            btn.pack(pady=5, padx=10, fill="x")
        #\

        #/ メインバー（右のバー）のコード
        self.mainbar = ctk.CTkScrollableFrame(self, fg_color="#222222")
        self.mainbar.grid(row=0, column=1, sticky="nsew")
        self.mainbar.grid_columnconfigure(0, weight=1)
        self.mainbar.bind_all("<MouseWheel>", self.on_mousewheel)
        #\

        self.frames = []

    # ブロックをクリックしたときのメソッド
    def add_block_to_canvas(self, block_name):
        if block_name == "row":
            frame_number = len(self.frames) + 1
            new_frame = MyFrame(master=self.mainbar, frames=self.frames, font=self.FONT, number=frame_number)  # ← self.frame → new_frame に変更
            new_frame.grid(row=len(self.frames), column=0, padx=10, sticky="ew")
            self.frames.append(new_frame)

        elif block_name == "block" and self.select_frame:
            self.select_frame.add_block()

    # clickされた時のメソッド
    def click(self, event):
        # クリックされた位置にあるフレームを選択するfor文
        # self.frames内にあるフレームを順にwinfoで位置を把握しif文で確かめていく
        for frame in self.frames:
            y = frame.winfo_rooty()
            h = frame.winfo_height()
            x = frame.winfo_rootx()
            w = frame.winfo_width()
            if y <= event.y_root < y + h and x <= event.x_root < x + w:
                # クリックされてブロックが選択された場合はまた確かめる
                # ブロックが選択されていなかったらフレームを選択する
                self.select_frame = frame
                if frame.blocks:
                    for block in frame.blocks:
                        y = block.winfo_rooty()
                        h = block.winfo_height()
                        x = block.winfo_rootx()
                        w = block.winfo_width()
                        if y <= event.y_root < y + h and x <= event.x_root < x + w:
                            self.select_block = block
                            for b in frame.blocks:
                                b.configure(border_color="#222222")
                            block.configure(border_color="#4A4A4A")
                            return
                # 選択されたフレームのスタイルを変更
                for f in self.frames:
                    f.configure(border_color="#222222")
                frame.configure(border_color="#4A4A4A")
                return

    def on_mousewheel(self, event):
        self.mainbar._parent_canvas.yview_scroll(int(-1 * (event.delta / 2)), "units")
        return "break"


class MyFrame(ctk.CTkFrame):
    def __init__(self, master, frames, font, number, **kwargs):
        self.my_frame_border_width = 2
        self.frames = frames
        self.FONT = font
        self.height = 200
        self.number = number
        self.blocks = []

        super().__init__(
            master,
            fg_color="#222222",
            corner_radius=0,
            border_color="#222222",
            border_width=self.my_frame_border_width,
            height=self.height,
            **kwargs
        )
        self.grid_propagate(False)

        # 高さ200pxの中央に配置するための設定
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # ラベル

        # ラベル（左上だと不自然なので縦中央にする）
        self.frame_number_label = ctk.CTkLabel(
            master=self,
            text=str(number),
            text_color="#7B7B7B",
            font=self.FONT
        )
        self.frame_number_label.grid(row=0, column=0, padx=10, pady=self.my_frame_border_width+5, sticky="nsw")  # ← 左に縦中央で表示

    def add_block(self):
        new_block = MyBlock(master=self, blocks=self.blocks, font=self.FONT, height=self.height)
        new_block.grid(row=0, column=len(self.blocks)+1, padx=10, pady=self.my_frame_border_width)
        self.blocks.append(new_block)

class MyBlock(ctk.CTkFrame):
    def __init__(self, master, blocks, font, **kwargs):
        self.blocks = blocks
        self.FONT = font
        super().__init__(
            master, 
            border_color="#222222", 
            border_width=1,
            fg_color="#222222", 
            **kwargs
            )

if __name__ == "__main__":
    app = CodeSmithApp()
    app.mainloop()
