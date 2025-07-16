import customtkinter as ctk
import tkinter.filedialog
from PIL import Image  # 画像処理のためにPILをインポート
import os


# 変数、関数の定義
# グローバル変数
select_frame = None
select_block = None
frames = []
FONT = ("Noto Sans JP", 15)  # フォントの設定

# グローバル関数
def search_mouse_cursor(event, master):
    y = master.winfo_rooty()
    h = master.winfo_height()
    x = master.winfo_rootx()
    w = master.winfo_width()
    if y <= event.y_root < y + h and x <= event.x_root < x + w:  # 範囲内にあるか
        return True
    return False


# アプリ本体のクラス
class CodeSmithApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#1F1F1F")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("CodeSmithApp")
        self.geometry("600x400")

        self.grid_rowconfigure(0, weight=1)
        # ← カラム設定を修正
        self.grid_columnconfigure(0, weight=0)  # menubar
        self.grid_columnconfigure(1, weight=0)  # sidebar
        self.grid_columnconfigure(2, weight=1)  # mainbar ← ここにだけweight=1を設定

        self.bind("<Button>", self.click)

        menubar = ctk.CTkFrame(
            self, 
            fg_color="#1C1C1C",
            width=60,
            corner_radius=0
            )
        menubar.grid(row=0, column=0, sticky="nsw")
        menubar.grid_propagate(False)

        # menubar.grid_rowconfigure(0, weight=1)
        menubar.grid_columnconfigure(0, weight=1)

        # メニューバー画像を追加
        menubar_children = [
            "file_icon.png",
            "block_icon.png",
        ]

        # ** 次はクリック用のフレームを作る **
        for i, icon_name in enumerate(menubar_children):
            image_file = Image.open(f"image/menubar/{icon_name}")
            image = ctk.CTkImage(light_image=image_file, dark_image=image_file, size=(30,30))
            image_frame = ctk.CTkFrame(master=menubar, fg_color="transparent")
            image_frame.grid(row=i, column=0, pady=5,sticky="nsew")
            image_frame.grid_propagate(False)
            menu_label = ctk.CTkLabel(master=image_frame, image=image, text="")
            menu_label.pack(fill="both", expand=True)

        #/ 左サイドバーのコード
        self.sidebar = ctk.CTkScrollableFrame(
            self,
            width=150,
            fg_color="#1F1F1F",
            border_color="#606060",
            border_width=1,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=1, sticky="nsw")
        self.sidebar.grid_columnconfigure(0, weight=1)
        # サイドバーのマウスホイールバインド
        self.sidebar.bind("<MouseWheel>", self.sidebar_on_mousewheel)

        self.sidebar_blocks = [
            "frame", "block", "if", "while", "for", "true", "false", "none", "return", "function"
        ]

        for idx, block in enumerate(self.sidebar_blocks):
            block_button = ctk.CTkButton(
                self.sidebar,
                text=block,
                font=FONT,
                command=lambda block=block: self.add_block_to_canvas(block)
            )
            block_button.grid(row=idx, column=0, sticky="ew", padx=5, pady=5)

        # サイドバーにエントリーと%ラベルを横並びで配置
        percent_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        percent_frame.grid(row=len(self.sidebar_blocks)+1, column=0, sticky="w", padx=5, pady=10)

        self.change_frame_size = Change_Frame_Size_Entry(percent_frame, width=60)
        self.change_frame_size.pack(side="left")

        percent_label = ctk.CTkLabel(percent_frame, text="%", font=FONT)
        percent_label.pack(side="left", padx=(5, 0))
        #\

        #/ メインバー（右のバー）のコード
        self.mainbar = ctk.CTkScrollableFrame(self, fg_color="#222222")
        self.mainbar.grid(row=0, column=2, sticky="nsew")
        self.mainbar.grid_columnconfigure(0, weight=1)
        # メインバーのマウスホイールバインド
        self.mainbar.bind("<MouseWheel>", self.mainbar_on_mousewheel)
        #\

    def open_file(self):
        filepath = tkinter.filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # 例: 最初のフレーム・ブロックのテキストボックスに内容を表示
            if frames and frames[0].frame_blocks and frames[0].frame_blocks[0].block_elements:
                textbox = frames[0].frame_blocks[0].block_elements[0]
                textbox.delete("1.0", "end")
                textbox.insert("1.0", content)

    # ブロックをクリックしたときのメソッド
    def add_block_to_canvas(self, block_name):
        global select_frame
        if block_name == "frame":
            frame_number = len(frames) + 1
            new_frame = MyFrame(master=self.mainbar, number=frame_number)
            new_frame.grid(row=len(frames), column=0, padx=10, sticky="ew")
            frames.append(new_frame)
            for all_frame in frames:
                all_frame.configure(border_color="#222222")  # すべてのフレームの枠線を元に戻す 
                for all_block in all_frame.frame_blocks:
                    all_block.configure(border_color="#4A4A4A")  # すべてのブロックの枠線を元に戻す
            new_frame.configure(border_color="#4A4A4A")  # 新しいフレームの枠線を変更
            select_frame = new_frame  # 新しいフレームを選択状態にする 

        elif block_name == "block" and select_frame:
            select_frame.add_block() # フレームにブロックを追加

    # clickされた時のメソッド
    def click(self, event):
        global select_frame, select_block
        # search_mouse_cursor関数を使って、マウスカーソルの位置を確認
        if search_mouse_cursor(event=event, master=self.sidebar):
            # サイドバーがクリックされた場合は何もしない
            return
        for master_frame in frames:
            if search_mouse_cursor(event=event, master=master_frame):
                select_frame = master_frame
                # 選択されたフレームのスタイルを変更
                for all_frame in frames:
                    all_frame.configure(border_color="#222222")
                master_frame.configure(border_color="#4A4A4A")
                if master_frame.frame_blocks:
                    # すべてのブロックのスタイルを元に戻す
                    for all_frame in frames:
                        for all_block in all_frame.frame_blocks:
                            all_block.configure(border_color="#4A4A4A")
                    # クリックされたブロックを選択する
                    for master_block in master_frame.frame_blocks:
                        if search_mouse_cursor(event=event, master=master_block):
                            select_block = master_block
                            master_block.configure(border_color="#7B7B7B")
                            master_block.textbox.focus_set()  # テキストボックスがある場合に文字入力状態にする
                            return

                for all_frame in frames:
                        for all_block in all_frame.frame_blocks:
                            all_block.configure(border_color="#4A4A4A")
                # ブロックの選択を解除
                select_block = None
                app.focus_set()  # アプリ全体にフォーカスを戻す
                return
        # すべての選択を解除
        select_frame = None
        select_block = None
        app.focus_set()  # アプリ全体にフォーカスを戻す
        # すべてのフレームの枠線を元に戻す
        for all_frame in frames:
            all_frame.configure(border_color="#222222")
        # すべてのブロックの枠線を元に戻す
        for all_frame in frames:
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
    def __init__(self, master, number, **kwargs):
        self.my_frame_border_width = 2
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
            font=FONT
        )
        # 左に縦中央で表示
        self.frame_number_label.grid(
            row=0, column=0, padx=10, pady=self.my_frame_border_width+5, sticky="nsw"
        )

    def add_block(self):
        global select_block
        new_block = MyBlock(master=self, height=self.height)
        new_block.grid(row=0, column=len(self.frame_blocks)+1, padx=10, pady=self.my_frame_border_width)
        self.frame_blocks.append(new_block)
        for all_frame in frames:
            for all_block in all_frame.frame_blocks:
                all_block.configure(border_color="#4A4A4A")
        new_block.configure(border_color="#7B7B7B")  # 新しいブロックの枠線を変更
        select_block = new_block  # 新しいブロックを選択状態にする
        new_text = ctk.CTkTextbox(
            master=new_block,
            fg_color="#222222",
            border_color="#222222",
            border_width=1,
            font=FONT,
            width=200,
        )
        new_text.pack(padx=2, pady=2, fill="both", expand=True)
        new_text.focus_set()  # 文字入力状態にする
        self.textbox = new_text  # テキストボックスを保存

class MyBlock(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        self.block_width = 200
        self.block_elements = {}
        super().__init__(
            master, 
            border_color="#4A4A4A", 
            border_width=1,
            fg_color="#222222", 
            width=self.block_width,
            **kwargs
        )
        self.pack_propagate(False)  # ← 追加: 子ウィジェットで幅が変わらないようにする


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


if __name__ == "__main__":
    app = CodeSmithApp()
    app.mainloop()