import sys
import json
import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QLabel, QSplitter, QScrollArea, QPushButton, QToolButton, QTextEdit, QFileDialog
)
from PySide6.QtGui import QPalette, QColor, QIcon

# --- カスタムウィジェット ---
class QtBlock(QFrame):
    # QtBlockウィジェットを初期化します。
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #333333; border: 1px solid #4A4A4A; border-radius: 4px;")
        self.setMinimumHeight(40)
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("border: none;")
        layout.addWidget(self.text_edit)

class QtFrame(QFrame):
    # QtFrameウィジェットを初期化します。
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.number = number
        self.blocks = []
        self.setStyleSheet("background-color: #2C2C2C; border: 1px solid #4A4A4A; border-radius: 5px;")
        self.setMinimumWidth(240)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel(f"Frame {self.number}")
        title_label.setStyleSheet("color: #AAAAAA; padding: 5px;")
        self.main_layout.addWidget(title_label)

        self.is_resizing = False
        self.resizing_edge = None
        self.resize_edge_width = 5
        self.prev_sibling_widget = None # 前のフレームを格納するため
        self.setMouseTracking(True)

    # フレームに新しいブロックを追加します。
    def add_block(self):
        block = QtBlock()
        self.main_layout.addWidget(block)
        self.blocks.append(block)
        return block

    def mousePressEvent(self, event):
        edge = self.get_resize_edge(event.position().toPoint())
        if event.button() == Qt.LeftButton and edge:
            self.is_resizing = True
            self.resizing_edge = edge
            self.resize_start_pos = event.globalPosition().toPoint()
            self.original_width = self.width() # 自身の元の幅を格納

            if self.resizing_edge == 'left':
                # レイアウト内の前のウィジェットを見つける
                parent_layout = self.parentWidget().layout()
                my_index = parent_layout.indexOf(self)
                if my_index > 0:
                    self.prev_sibling_widget = parent_layout.itemAt(my_index - 1).widget()
                    self.original_prev_sibling_width = self.prev_sibling_widget.width()
                else:
                    self.prev_sibling_widget = None
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.is_resizing:
            delta = event.globalPosition().toPoint() - self.resize_start_pos
            
            if self.resizing_edge == 'right':
                new_width = self.original_width + delta.x()
                if new_width > 0:
                    self.setFixedWidth(new_width)
            
            elif self.resizing_edge == 'left' and self.prev_sibling_widget:
                # 前のフレームの新しい幅
                new_prev_width = self.original_prev_sibling_width + delta.x()
                # 現在のフレームの新しい幅
                new_self_width = self.original_width - delta.x()

                # 両方のフレームの幅が0より大きいことを確認してから適用
                if new_prev_width > 0 and new_self_width > 0:
                    self.prev_sibling_widget.setFixedWidth(new_prev_width)
                    self.setFixedWidth(new_self_width)
        
        elif self.get_resize_edge(event.position().toPoint()):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.unsetCursor()
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_resizing:
            self.is_resizing = False
            self.resizing_edge = None
            self.prev_sibling_widget = None
        super().mouseReleaseEvent(event)

    def get_resize_edge(self, pos):
        # フレームの左端をドラッグすることは、スプリッターをドラッグする概念
        # そのため、左端をチェックする
        if self.number > 1 and pos.x() < self.resize_edge_width:
            return 'left'
        # 最も右にあるフレームの右端のリサイズも許可する
        if pos.x() >= self.width() - self.resize_edge_width:
            return 'right'
        return None

# --- メインアプリケーション ---

class FlairApp(QMainWindow):
    # メインアプリケーションウィンドウを初期化します。
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlairApp (Qt)")
        self.setGeometry(100, 100, 800, 600)

        self.frames = []
        self.selected_frame = None
        self.selected_block = None

        # --- スタイル変数 ---
        self.sidebar_button_color = "#65F4D4"

        self.script_dir = Path(__file__).parent.parent

        self.init_ui()

    # ユーザーインターフェースを初期化します。
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- メニューバー ---
        self.menubar = QFrame()
        self.menubar.setFixedWidth(60)
        self.menubar.setStyleSheet("background-color: #1C1C1C;")
        menubar_layout = QVBoxLayout(self.menubar)
        menubar_layout.setContentsMargins(5, 5, 5, 5)
        menubar_layout.setSpacing(5)
        menubar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        file_button = self.add_tool_button(menubar_layout, "file_icon.png", "File Operations")
        block_button = self.add_tool_button(menubar_layout, "block_icon.png", "Block Operations")
        file_button.clicked.connect(self.setup_file_sidebar)
        block_button.clicked.connect(self.setup_block_sidebar)

        # --- スプリッター ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- サイドバー ---
        self.sidebar = QScrollArea()
        self.sidebar.setWidgetResizable(True)
        self.sidebar.setMinimumWidth(150)
        self.sidebar.setStyleSheet("background-color: #1F1F1F; border: none;")
        
        self.sidebar_content = QWidget()
        self.sidebar.setWidget(self.sidebar_content)
        self.sidebar_layout = QVBoxLayout(self.sidebar_content)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setup_file_sidebar() # 初期表示

        # --- メインバー ---
        self.mainbar_scroll_area = QScrollArea()
        self.mainbar_scroll_area.setWidgetResizable(True)
        self.mainbar_scroll_area.setStyleSheet("background-color: #222222; border: none;")
        
        mainbar_content = QWidget()
        self.mainbar_scroll_area.setWidget(mainbar_content)
        self.mainbar_layout = QHBoxLayout(mainbar_content)
        self.mainbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # --- レイアウトへの追加 ---
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.mainbar_scroll_area)
        splitter.setSizes([150, 650])

        main_layout.addWidget(self.menubar)
        main_layout.addWidget(splitter)

    # メニューバーにツールボタンを追加します。
    def add_tool_button(self, layout, icon_name, tooltip):
        button = QToolButton()
        icon_path = self.script_dir / "image" / "menubar" / icon_name
        if icon_path.exists():
            button.setIcon(QIcon(str(icon_path)))
        button.setIconSize(QSize(30, 30))
        button.setToolTip(tooltip)
        layout.addWidget(button)
        return button

    # サイドバーのコンテンツをクリアします。
    def clear_sidebar(self):
        for i in reversed(range(self.sidebar_layout.count())): 
            widget = self.sidebar_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

    # ファイル操作サイドバーをセットアップします。
    def setup_file_sidebar(self):
        self.clear_sidebar()
        file_ops = ["Open File", "Save File"]
        for op in file_ops:
            button = QPushButton(op)
            if op == "Open File":
                button.clicked.connect(self.open_file)
            if op == "Save File":
                button.clicked.connect(self.save_file)
            button.setStyleSheet(f"background-color: {self.sidebar_button_color}; color: #000000; border: 1px solid #555555; border-radius: 4px; padding: 5px;")
            self.sidebar_layout.addWidget(button)

    # ブロック操作サイドバーをセットアップします。
    def setup_block_sidebar(self):
        self.clear_sidebar()
        block_types = ["frame", "block", "none", "if", "while", "for", "true", "false", "return", "function"]
        for block_type in block_types:
            button = QPushButton(block_type)
            if block_type == "frame":
                button.clicked.connect(self.add_frame)
            if block_type == "block":
                button.clicked.connect(self.add_block_to_selected_frame)
            button.setStyleSheet(f"background-color: {self.sidebar_button_color}; color: #000000; border: 1px solid #555555; border-radius: 4px; padding: 5px;")
            self.sidebar_layout.addWidget(button)

    # メインバーに新しいフレームを追加します。
    def add_frame(self):
        frame_number = len(self.frames) + 1
        new_frame = QtFrame(frame_number)
        self.mainbar_layout.addWidget(new_frame)
        self.frames.append(new_frame)
        self.select_frame(new_frame)

    # 現在選択されているフレームにブロックを追加します。
    def add_block_to_selected_frame(self):
        if self.selected_frame:
            self.selected_frame.add_block()

    # 選択されたフレームをハイライトします。
    def select_frame(self, frame_to_select):
        self.selected_frame = frame_to_select
        for frame in self.frames:
            if frame == frame_to_select:
                frame.setStyleSheet("background-color: #2C2C2C; border: 2px solid #4A90E2; border-radius: 5px;")
            else:
                frame.setStyleSheet("background-color: #2C2C2C; border: 1px solid #4A4A4A; border-radius: 5px;")

    # すべてのフレームの選択を解除します。
    def deselect_all_frames(self):
        self.select_frame(None)

    # JSONファイルを開き、データを読み込みます。
    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for frame in self.frames:
            frame.setParent(None)
        self.frames.clear()

        for i, frame_data in enumerate(data):
            new_frame = self.add_frame()
            for block_texts in frame_data:
                new_block = new_frame.add_block()
                if block_texts:
                    new_block.text_edit.setText(block_texts[0])

    # 現在のデータをJSONファイルに保存します。
    def save_file(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return

        data = []
        for frame in self.frames:
            frame_data = []
            for block in frame.blocks:
                block_data = [block.text_edit.toPlainText()]
                frame_data.append(block_data)
            data.append(frame_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # クリックされたウィジェットまたはその親をたどって、指定された型のウィジェットを見つけます。
    def get_ancestor_widget(self, event, widget_type):
        widget = QApplication.widgetAt(event.globalPosition().toPoint())
        while widget is not None:
            if isinstance(widget, widget_type):
                return widget
            widget = widget.parent()
        return None

    def mousePressEvent(self, event):
        # クリックされた場所にあるQtFrameを探す
        clicked_frame = self.get_ancestor_widget(event, QtFrame)

        # QtFrameまたはその子ウィジェットがクリックされた場合
        if clicked_frame:
            self.select_frame(clicked_frame)
        # QtFrame以外の場所がクリックされた場合
        else:
            # サイドバーのボタン上でなければ選択を解除
            # （ボタンクリックで選択解除されるのを防ぐ）
            if not self.get_ancestor_widget(event, (QPushButton, QToolButton)):
                self.deselect_all_frames()

        super().mousePressEvent(event)


if __name__ == "__main__":
    # Set QT_IM_MODULE for Japanese input support
    os.environ['QT_IM_MODULE'] = 'fcitx' 

    app = QApplication(sys.argv)

    # # Read and log the QT_IM_MODULE value for debugging
    # im_module = os.environ.get('QT_IM_MODULE')
    # temp_dir = Path("/home/tomato956/.gemini/tmp/31a8f51bf6d8ebee52b27e0211d95ad2059460949f68cf9f424b1848985535cb")
    # debug_file = temp_dir / "qt_im_module.log"
    # with open(debug_file, "w", encoding="utf-8") as f:
    #     f.write(f"QT_IM_MODULE: {im_module}")

    # app.setStyle("Fusion")
    # dark_palette = QPalette()
    # dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
    # dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    # dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("white"))
    # dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("white"))
    # dark_palette.setColor(QPalette.ColorRole.Text, QColor("white"))
    # dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))

    window = FlairApp()
    window.show()
    sys.exit(app.exec())