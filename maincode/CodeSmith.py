import customtkinter as ctk
import tkinter.filedialog
from PIL import Image  # 画像処理のためにPILをインポート
import json
from pathlib import Path


# 変数、関数の定義
# グローバル変数
select_frame = None
select_block = None
frames = []
textbox = None
FONT = ("Meiryo", 15)  # フォントの設定

# グローバル関数
def search_mouse_cursor(event, master, **kwargs):
    y = master.winfo_rooty()
    h = master.winfo_height()
    x = master.winfo_rootx()
    w = master.winfo_width()
    padx, pady = 0, 0  # デフォルト値
    if "padx" in kwargs:
        padx = kwargs["padx"]
    if "pady" in kwargs:
        pady = kwargs["pady"]
    if y - pady <= event.y_root < y + h + pady and x - padx <= event.x_root < x + w + padx:  # 範囲内にあるか
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

        self.frame_height = 200

        self.grid_rowconfigure(0, weight=1)
        # ← カラム設定を修正
        self.grid_columnconfigure(0, weight=0)  # menubar
        self.grid_columnconfigure(1, weight=0)  # sidebar
        self.grid_columnconfigure(2, weight=1)  # mainbar ← ここにだけweight=1を設定

        self.bind("<Button>", self.click)

        #**/ メニューバーのコード
        self.menubar = ctk.CTkFrame(
            self, 
            fg_color="#1C1C1C",
            width=60,
            corner_radius=0
            )
        self.menubar.grid(row=0, column=0, sticky="nsw")
        self.menubar.grid_propagate(False)

        # menubar.grid_rowconfigure(0, weight=1)
        self.menubar.grid_columnconfigure(0, weight=1)

        # メニューバー画像を追加
        self.menubar_children = [
            "file_icon.png",
            "block_icon.png",
        ]
        self.menubar_icon_frames = []
        self.sidebar_file_frame_list = []
        self.sidebar_scene = None
        self.select_menubar_icon_frame = None
        self.select_file_frame = None
        #! self.file_displayに入る情報はPathモジュールを使っていなくてファイルのパスがある。
        #! そのため、.stemなどとりだすことはできない。
        self.file_display = None
        self.frame_height = 200

        for i, icon_name in enumerate(self.menubar_children):
            image_file = Image.open(f"image/menubar/{icon_name}")
            image = ctk.CTkImage(light_image=image_file, dark_image=image_file, size=(30,30))
            icon_frame = ctk.CTkFrame(master=self.menubar, fg_color="transparent", corner_radius=0, height=100)
            icon_frame.grid(row=i, column=0, sticky="nsew")
            icon_frame.pack_propagate(False)
            self.menubar_icon_frames.append(icon_frame)
            menu_label = ctk.CTkLabel(master=icon_frame, image=image, text="")
            menu_label.pack(fill="both", expand=True, padx=5, pady=5)
        #**

        #**/ 左サイドバーのコード
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

        self.select_menubar_icon_frame_clean()   # 初期状態では何も表示しない
        self.file_list = []
        #**\

        #**/ 左サイドバーのコード
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

        self.select_menubar_icon_frame_clean()   # 初期状態では何も表示しない
        self.file_list = []
        #**\

        #**/ メインバー（右のバー）のコード
        self.mainbar = ctk.CTkScrollableFrame(self, fg_color="#222222")
        self.mainbar.grid(row=0, column=2, sticky="nsew")
        self.mainbar.grid_rowconfigure(0, weight=1)
        # メインバーのマウスホイールバインド
        self.mainbar.bind("<MouseWheel>", self.mainbar_on_mousewheel)
        self.last_known_height = 0
        #**\

    #**/サイドバーの関数
    # noneの時のサイドバーを表示
    def select_menubar_icon_frame_clean(self):
        self.sidebar_scene = None
        # サイドバーの内容をクリア
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.sidebar_blocks = []

    # file_iconの時のサイドバーを表示
    def select_menubar_icon_frame__file_icon(self):
        self.sidebar_scene = "file_icon"
        self.select_menubar_icon_frame_clean()  # サイドバーをクリア
        self.sidebar_blocks = [
            "open_txt_file",
            "open_file", 
            "save_file", 
            ]
        for idx, block in enumerate(self.sidebar_blocks):
            block_button = ctk.CTkButton(
                self.sidebar,
                text=block,
                font=FONT,
                command=lambda block=block: self.add_file_to_canvas(block)
            )
            block_button.grid(row=idx, column=0, sticky="ew", padx=5, pady=5)
        
        new_text_label = ctk.CTkLabel(
            self.sidebar,
            text="file_list",
            font=FONT,
            text_color="#A8A8A8"
        )
        new_text_label.grid(row=len(self.sidebar_blocks), column=0, sticky="w", padx=10, pady=5)
        self.update_file_list()

    def update_file_list(self, **kwargs):
        # 既存のファイルリストをクリア
        # for widget in self.sidebar.winfo_children():
        #     if isinstance(widget, ctk.CTkLabel) and not widget.cget("text") == "file_list":
        #         widget.destroy()

        if "file_path" in kwargs:
            file_path = Path(kwargs["file_path"])
            if file_path not in self.file_list:
                self.file_list.append(file_path)
        
        if self.file_display:
            file_display = Path(self.file_display)
        else:
            file_display = None

        # 新しいファイルリストを表示
        for idx, file_path in enumerate(self.file_list):
            if file_display and file_display.name == file_path.name:
                color = "#FFFFFF"
            else:
                color = "#A8A8A8"
            file_frame = ctk.CTkFrame(
                self.sidebar,
                fg_color="transparent",
            )
            file_frame.grid(row=len(self.sidebar_blocks) + idx + 2, column=0, sticky="ew")
            file_label = ctk.CTkLabel(
                file_frame,
                text=file_path.name,
                font=FONT,
                text_color=color
            )
            file_label.pack()
            self.sidebar_file_frame_list.append(file_frame)
            file_frame_open_button = ctk.CTkButton(
                file_frame,
                text="open",
                font=FONT,
                command=lambda path=file_path: self.open_function(file_path=path)  # ファイルを開く
            )
            file_frame_open_button.pack(side="right", padx=5, pady=5)

    # block_iconの時のサイドバーを表示
    def select_menubar_icon_frame__block_icon(self):
        self.sidebar_scene = "block_icon"
        self.select_menubar_icon_frame_clean()  # サイドバーをクリア
        self.sidebar_blocks = [
        "frame", "block", "none", "if", "while", "for", "true", "false", "return", "function"
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
    #**\

    def add_file_to_canvas(self, block_name):
        if block_name == "open_txt_file":
            self.open_txt_file()
        elif block_name == "open_file":
            self.open_file()
        elif block_name == "save_file":
            self.save_file()

    # ファイルを開くメソッド
    def open_txt_file(self):
        global textbox
        filepath = tkinter.filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.* אמיתי") ]
        )
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # 例: 最初のフレーム・ブロックのテキストボックスに内容を表示
            if frames and frames[0].frame_blocks:
                textbox.delete("1.0", "end")
                textbox.insert("1.0", content)
    
    # ファイルを開くメソッド
    def open_file(self):
        filepath = tkinter.filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.* אמיתי אמיתי אמיתי")]
        )
        if not filepath:
            return  # キャンセルされたら何もしない

        self.open_function(file_path=filepath)

    def open_function(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 既存のフレームを削除
        for frame in frames:
            frame.destroy()
        frames.clear()

        self.update_idletasks()
        # 復元
        for i, frame_data in enumerate(data):
            new_frame = MyFrame(master=self.mainbar, number=i + 1, height=self.frame_height)
            new_frame.grid(row=0, column=i, padx=10, pady=10, sticky="n")
            frames.append(new_frame)

            for block_texts in frame_data:
                new_frame.add_block()
                block = new_frame.frame_blocks[-1]
                for widget in block.winfo_children():
                    if isinstance(widget, ctk.CTkTextbox):
                        widget.delete("1.0", "end")
                        for text in block_texts:
                            widget.insert("1.0", text)
        self.file_display = file_path
        self.update_file_list(file_path=file_path)  # ファイルリストを更新

    # ファイルを保存するメソッド
    def save_file(self):
        data = []

        for frame in frames:
            frame_data = []
            for block in frame.frame_blocks:
                block_data = []
                for element in block.winfo_children():
                    if isinstance(element, ctk.CTkTextbox):
                        block_data.append(element.get("1.0", "end").strip())
                frame_data.append(block_data)
            data.append(frame_data)

        # ユーザーに保存先とファイル名を指定させる
        filepath = tkinter.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.* אמיתי אמיתי אמיתי אמיתי")]
        )
        if not filepath:
            return  # ユーザーがキャンセルした場合

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.update_file_list(file_path=filepath)  # ファイルリストを更新

    # ブロックをクリックしたときのメソッド
    def add_block_to_canvas(self, block_name):
        global select_frame
        if block_name == "frame":
            self.update_idletasks()
            height = 200
            new_frame = MyFrame(master=self.mainbar, number=len(frames) + 1, height=height)
            new_frame.grid(row=0, column=len(frames), padx=10, pady=10, sticky="n")
            
            # 新しいフレームをリストの末尾に追加
            frames.append(new_frame)
        elif block_name == "block":
            if select_frame:
                select_frame.add_block()
    
    # クリックイベントのメソッド
    # 説明
    # search_mouse_cursor関数は、指定したウィジェットがクリックしているかどうかを確認します。
    # search_mouse_cursor(event, master)
    # masterは、指定するウィジェット
    # returnは、クリックしている場合はTrue、そうでない場合はFalse
    # kwargsにはpadxとpadyがある
    # padxは、ウィジェットの左右の余白を指定する。
    # padyは、ウィジェットの上下の余白を指定する。
    # これを指定することで余白部分もクリック判定になる。
    def click(self, event):
        global select_frame, select_block
        # search_mouse_cursor関数を使って、マウスカーソルの位置を確認
        if search_mouse_cursor(event=event, master=self.sidebar):
            return  
        if search_mouse_cursor(event=event, master=self.mainbar):
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
        if search_mouse_cursor(event=event, master=self.menubar):
            for master_icon_frame in self.menubar_icon_frames:
                if search_mouse_cursor(event=event, master=master_icon_frame):
                    if master_icon_frame == self.menubar_icon_frames[0] and not self.select_menubar_icon_frame == self.menubar_icon_frames[0]:
                        self.select_menubar_icon_frame__file_icon()
                    if master_icon_frame == self.menubar_icon_frames[1] and not self.select_menubar_icon_frame == self.menubar_icon_frames[1]:
                        self.select_menubar_icon_frame__block_icon()
                    self.select_menubar_icon_frame = master_icon_frame
                    # 選択されたアイコンのスタイルを変更
                    for all_icon_frame in self.menubar_icon_frames:
                        all_icon_frame.configure(fg_color="transparent")
                    master_icon_frame.configure(fg_color="#4A4A4A")
                    return
            # ほかの所にクリックされた場合はなにもしない
            return

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
        self.number = number
        self.frame_blocks = []

        super().__init__(
            master,
            fg_color="#222222",
            corner_radius=0,
            border_color="#222222",
            border_width=self.my_frame_border_width,
            **kwargs
        )
        # 子ウィジェットに合わせてサイズが自動で変わるようにする
        self.grid_propagate(True)

        self.grid_columnconfigure(0, weight=1)

        # ラベル（左上だと不自然なので縦中央にする）
        self.frame_number_label = ctk.CTkLabel(
            master=self,
            text=str(number),
            text_color="#7B7B7B",
            font=FONT
        )
        # 左に縦中央で表示
        self.frame_number_label.grid(
            row=0, column=0, padx=10, pady=self.my_frame_border_width+5, sticky="nw"
        )
        
        self.grid_propagate(False)

    def add_block(self):
        global select_block, textbox
        new_block = MyBlock(master=self)
        new_block.grid(row=len(self.frame_blocks) + 1, column=0, padx=10, pady=self.my_frame_border_width, sticky="ew")
        self.frame_blocks.append(new_block)

        # 高さは子要素に合わせて自動調整させる（手動調整を削除）

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
        textbox = new_text  # テキストボックスを保存

        self.grid_propagate(True)

class MyBlock(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        self.block_elements = {}
        super().__init__(
            master, 
            border_color="#4A4A4A", 
            border_width=1,
            fg_color="#222222", 
            **kwargs
        )
        # デフォルトのサイズ伝播を維持し、子に合わせて自動リサイズ


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
