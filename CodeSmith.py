import customtkinter as ctk

#アプリ本体のクラス
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
        
        #/左サイドバーのコード
        self.blocks = ["row", "none", "text", "if", "while", "for", "true", "false"]
        
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
        for row in range(len(self.blocks)+1): #サイドバーのすべての行を可変にした。
            self.sidebar.grid_rowconfigure(row ,weight=1)

        for block in self.blocks:
            btn = ctk.CTkButton(self.sidebar, text=block, command=lambda b=block: self.add_block_to_canvas(b))
            btn.pack(pady=5, padx=10, fill="x")
        #\

        #/メインバー（右のバー）のコード
        self.mainbar = ctk.CTkFrame(self, fg_color="#222222")
        self.mainbar.grid(row=0, column=1, sticky="nsew")
        self.mainbar.grid_columnconfigure(0, weight=1)
        #\

        self.frames = []

    #ブロックをクリックしたときのメソッド
    def add_block_to_canvas(self, block_name):
        if block_name == self.blocks[0]:
            #Myflameでフレームを作る
            self.frame = Myflame(master=self.mainbar, frames=self.frames)
            self.frame_padx = 10 #self.frame.gridのpadxの値
            self.frame.grid(row=self.frames.__len__(), column=0, padx=self.frame_padx, sticky="ew")
            self.frames.append(self.frame)
            self.frames

    #chickされた時のメゾット    
    def click(self, event):
        # event.x, event.y はウィンドウ（self）内での座標
        for frame in self.frames:
            y = frame.winfo_rooty()
            h = frame.winfo_height()
            x = frame.winfo_rootx()
            w = frame.winfo_width()
            if y <= event.y_root < y + h and x <= event.x_root < x + w:
                self.frame_select = frame
                for f in self.frames:
                    f.configure(border_color="#222222")
                self.frame_select.configure(border_color="#4A4A4A")
                break


#フレームの処理をするクラス
class Myflame(ctk.CTkFrame):
    def __init__(self, master, frames,**kwargs):
        self.my_border_width = 2 #border_widthの値を変数にする winfoで調べられないため
        self.frames = frames
        super().__init__(
            master, 
            fg_color="#222222", 
            corner_radius=0, 
            border_color="#222222", 
            border_width=self.my_border_width, 
            height=200, 
            **kwargs
        )
        self.grid_propagate(False) #高さを固定
        frame_text = len(frames) + 1
        self.frame_number_label = ctk.CTkLabel(master=self, text=frame_text, text_color="#3D3D3D")
        self.frame_number_label.grid(row=0, column=0, padx=self.my_border_width, pady=self.my_border_width)


if __name__ == "__main__":
    app = CodeSmithApp()
    app.mainloop()
