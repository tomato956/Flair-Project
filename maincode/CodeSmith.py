import sys
import json
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QLabel, QSplitter, QScrollArea, QPushButton, QToolButton, QTextEdit, QFileDialog
)
from PySide6.QtGui import QPalette, QColor, QIcon

# --- カスタムウィジェット ---
class QtBlock(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #333333; border: 1px solid #4A4A4A; border-radius: 4px;")
        self.setMinimumHeight(40)
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("border: none;")
        layout.addWidget(self.text_edit)

class QtFrame(QFrame):
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

    def add_block(self):
        block = QtBlock()
        self.main_layout.addWidget(block)
        self.blocks.append(block)
        return block

# --- メインアプリケーション ---
class CodeSmithApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeSmithApp (Qt)")
        self.setGeometry(100, 100, 800, 600)

        self.frames = []
        self.selected_frame = None

        self.script_dir = Path(__file__).parent.parent

        self.init_ui()

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

    def add_tool_button(self, layout, icon_name, tooltip):
        button = QToolButton()
        icon_path = self.script_dir / "image" / "menubar" / icon_name
        if icon_path.exists():
            button.setIcon(QIcon(str(icon_path)))
        button.setIconSize(QSize(30, 30))
        button.setToolTip(tooltip)
        layout.addWidget(button)
        return button

    def clear_sidebar(self):
        for i in reversed(range(self.sidebar_layout.count())): 
            widget = self.sidebar_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

    def setup_file_sidebar(self):
        self.clear_sidebar()
        file_ops = ["Open File", "Save File"]
        for op in file_ops:
            button = QPushButton(op)
            if op == "Open File":
                button.clicked.connect(self.open_file)
            elif op == "Save File":
                button.clicked.connect(self.save_file)
            self.sidebar_layout.addWidget(button)

# ブロックサイドバーの設定
    def setup_block_sidebar(self):
        self.clear_sidebar()
        block_types = ["frame", "block", "none", "if", "while", "for", "true", "false", "return", "function"]
        for block_type in block_types:
            button = QPushButton(block_type)
            if block_type == "frame":
                button.clicked.connect(self.add_frame)
            elif block_type == "block":
                button.clicked.connect(self.add_block_to_selected_frame)
            self.sidebar_layout.addWidget(button)

    def add_frame(self):
        frame_number = len(self.frames) + 1
        new_frame = QtFrame(frame_number)
        self.mainbar_layout.addWidget(new_frame)
        self.frames.append(new_frame)
        self.select_frame(new_frame)

    def add_block_to_selected_frame(self):
        if self.selected_frame:
            self.selected_frame.add_block()

    def select_frame(self, frame_to_select):
        self.selected_frame = frame_to_select
        for frame in self.frames:
            if frame == frame_to_select:
                frame.setStyleSheet("background-color: #2C2C2C; border: 2px solid #4A90E2; border-radius: 5px;")
            else:
                frame.setStyleSheet("background-color: #2C2C2C; border: 1px solid #4A4A4A; border-radius: 5px;")

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

    def mousePressEvent(self, event):
        self.select_frame(None)
        super().mousePressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("white"))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("white"))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor("white"))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor("red"))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("black"))
    app.setPalette(dark_palette)

    window = CodeSmithApp()
    window.show()
    sys.exit(app.exec())