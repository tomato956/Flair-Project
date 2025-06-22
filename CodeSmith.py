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

        self.FONT = ("Meiryo", 15) # フォントの設定
        
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

        # サイドバーのブロックのリスト
        self.blocks = [
            "row", "text", "if", "while", "for", "true", "false", "none", "return", "function"
            ]

        for row in range(len(self.blocks)+1): #サイドバーのすべての行を可変にした。
            self.sidebar.grid_rowconfigure(row ,weight=1)  

        # サイドバーにブロックのボタンを追加
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
        # マウスホイールのイベントをバインド
        # 77行目にある
        self.mainbar.bind_all("<MouseWheel>", self.on_mousewheel)
        #\ 

        self.frames = []

    # ブロックをクリックしたときのメソッド
    def add_block_to_canvas(self, block_name):
        if block_name == self.blocks[0]: # rowブロック
            # フレーム番号を計算
            frame_number = len(self.frames) + 1
            # MyFrameでフレームを作る（番号を渡す）
            self.frame = MyFrame(master=self.mainbar, frames=self.frames, font=self.FONT, number=frame_number)
            self.frame_padx = 10 # self.frame.gridのpadxの値
            self.frame.grid(row=self.frames.__len__(), column=0, padx=self.frame_padx, sticky="ew")
            self.frames.append(self.frame)
            self.frames

        if block_name == self.blocks[1]: # textブロック
            if not hasattr(self, 'select_frame') or self.select_frame is None:
                return
            else:
                # 選択されたフレームにテキストブロックを追加
                self.select_frame.add_text_block()


    # clickされた時のメソッド
    def click(self, event):
        # event.x, event.y はウィンドウ（self）内での座標
        for frame in self.frames:
            y = frame.winfo_rooty()
            h = frame.winfo_height()
            x = frame.winfo_rootx()
            w = frame.winfo_width()
            if y <= event.y_root < y + h and x <= event.x_root < x + w:
                self.select_frame = frame # 選択されたフレームを保存
                for f in self.frames:
                    f.configure(border_color="#222222")
                self.select_frame.configure(border_color="#4A4A4A")
                break

    # マウスホイールのイベントを処理するメソッド
    def on_mousewheel(self, event):
        # マウスホイールの回転量に応じてスクロール
        self.mainbar._parent_canvas.yview_scroll(int(-1*(event.delta/2)), "units")
        # mainbarだけがスクロールし、他のウィジェットや親フレームにはイベントが伝わらないようにする。
        return "break"

# フレームの処理をするクラス
class MyFrame(ctk.CTkFrame):

    # 初期化メソッド
    def __init__(self, master, frames, font, number, **kwargs):  # numberを追加
        # 値を受け取る　変数を定義する
        self.my_frame_border_width = 2 # border_widthの値を変数にする winfoで調べられないため
        self.frames = frames # フレームのリストを受け取る
        self.FONT = font # フォントを受け取る　文字は変えないため大文字にする

        super().__init__(
            master, 
            fg_color="#222222", 
            corner_radius=0, 
            border_color="#222222", 
            border_width=self.my_frame_border_width, 
            height=200, 
            **kwargs
        )
        self.grid_propagate(False) # 高さを固定

        #/ フレームに番号（ラベル）を追加
        frame_text = number  # ここを変更
        self.frame_number_label = ctk.CTkLabel(
            master=self, text=frame_text, text_color="#7B7B7B", font=self.FONT, 
            )
        self.grid_rowconfigure(0, weight=1)
        self.frame_number_label.grid(
            row=0, column=0, padx=self.my_frame_border_width
            )
        #\

    def add_text_block(self):
        text_block = ctk.CTkTextbox(
            master=self, 
            height=150, 
            width=200, 
            font=self.FONT, 
            )
        text_block.grid(
            row=0, column=1, padx=10
        )



if __name__ == "__main__":
    app = CodeSmithApp()
    app.mainloop()
