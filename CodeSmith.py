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
        self.sidebar = ctk.CTkScrollableFrame(
            self,
            width=150,
            fg_color="#1F1F1F",
            border_color="#606060",
            border_width=1,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_columnconfigure(0, weight=1)
        # サイドバーのマウスホイールバインド
        self.sidebar.bind("<MouseWheel>", self.sidebar_on_mousewheel)

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
        
        # サイドバーにエントリーと%ラベルを横並びで配置
        percent_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        percent_frame.pack(pady=10, padx=10, anchor="w")

        self.change_frame_size = Change_Frame_Size_Entry(percent_frame, width=60)
        self.change_frame_size.pack(side="left")

        percent_label = ctk.CTkLabel(percent_frame, text="%", font=self.FONT)
        percent_label.pack(side="left", padx=(5, 0))
        #\

        #/ メインバー（右のバー）のコード
        self.mainbar = ctk.CTkScrollableFrame(self, fg_color="#222222")
        self.mainbar.grid(row=0, column=1, sticky="nsew")
        self.mainbar.grid_columnconfigure(0, weight=1)
        # メインバーのマウスホイールバインド
        self.mainbar.bind("<MouseWheel>", self.mainbar_on_mousewheel)
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

        elif block_name == "text" and self.select_block:
            self.select_block.add_text()

    # clickされた時のメソッド
    def click(self, event):
        # search_mouse_cursor関数を使って、マウスカーソルの位置を確認
        if search_mouse_cursor(event=event, master=self.sidebar):
            # サイドバーがクリックされた場合は何もしない
            return
        for master_frame in self.frames:
            if search_mouse_cursor(event=event, master=master_frame):
                self.select_frame = master_frame
                # 選択されたフレームのスタイルを変更
                for all_frame in self.frames:
                    all_frame.configure(border_color="#222222")
                master_frame.configure(border_color="#4A4A4A")
                if master_frame.frame_blocks:
                    # すべてのブロックのスタイルを元に戻す
                    for all_frame in self.frames:
                        for all_block in all_frame.frame_blocks:
                            all_block.configure(border_color="#4A4A4A")
                    # クリックされたブロックを選択する
                    for master_block in master_frame.frame_blocks:
                        if search_mouse_cursor(event=event, master=master_block):
                            self.select_block = master_block
                            master_block.configure(border_color="#7B7B7B")
                            return
                
                for all_frame in self.frames:
                        for all_block in all_frame.frame_blocks:
                            all_block.configure(border_color="#4A4A4A")
                # ブロックの選択を解除
                self.select_block = None
                return
        # すべての選択を解除
        self.select_frame = None
        self.select_block = None
        # すべてのフレームの枠線を元に戻す
        for all_frame in self.frames:
            all_frame.configure(border_color="#222222")
        # すべてのブロックの枠線を元に戻す
        for all_frame in self.frames:
            for all_block in all_frame.frame_blocks:
                all_block.configure(border_color="#4A4A4A")

    # サイドバーのマウスホイールを検出するメソッド
    def sidebar_on_mousewheel(self, event):
        if search_mouse_cursor(event=event, master=self.sidebar):
            self.sidebar._parent_canvas.yview_scroll(int(-1 * (event.delta / 2)), "units")
            return
        return

    # メインバーのマウスホイールを検出するメソッド
    def mainbar_on_mousewheel(self, event):
        if search_mouse_cursor(event=event, master=self.mainbar):
            self.mainbar._parent_canvas.yview_scroll(int(-1 * (event.delta)), "units")
            return
        return


class MyFrame(ctk.CTkFrame):
    def __init__(self, master, frames, font, number, **kwargs):
        self.my_frame_border_width = 2
        self.frames = frames
        self.FONT = font
        self.height = 200
        self.number = number
        self.frame_blocks = []

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
        new_block = MyBlock(master=self, blocks=self.frame_blocks, font=self.FONT, height=self.height)
        new_block.grid(row=0, column=len(self.frame_blocks)+1, padx=10, pady=self.my_frame_border_width)
        self.frame_blocks.append(new_block)

class MyBlock(ctk.CTkFrame):
    def __init__(self, master, blocks, font, **kwargs):
        self.blocks = blocks
        self.FONT = font
        super().__init__(
            master, 
            border_color="#4A4A4A", 
            border_width=1,
            fg_color="#222222", 
            **kwargs
            )

    def add_text(self):
        # !作り途中
        new_text = ctk.CTkTextbox(
            master=self,
            fg_color="#222222",
            border_color="#4A4A4A",
            font=self.FONT
        )
        new_text.pack(padx=0, pady=0, fill="both", expand=True)
        # !作り途中


class Change_Frame_Size_Entry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        vcmd = (self.register(self._validate), "%P")
        self.configure(validate="key", validatecommand=vcmd)

    def _validate(self, P):
        if P == "":
            return True
        if P.isdigit():
            value = int(P)
            return 0 <= value <= 100
        return False


# 共有関数
def search_mouse_cursor(event, master):
    y = master.winfo_rooty()
    h = master.winfo_height()
    x = master.winfo_rootx()
    w = master.winfo_width()
    if y <= event.y_root < y + h and x <= event.x_root < x + w:  # 範囲内にあるか
        return True
    return False


if __name__ == "__main__":
    app = CodeSmithApp()
    app.mainloop()
