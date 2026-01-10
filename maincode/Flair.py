import sys
import json
import os
from pathlib import Path
from PySide6.QtCore import Qt, QSize, Signal, QRect, QTimer, QEvent, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QLabel, QSplitter, QScrollArea, QPushButton, QToolButton, QTextEdit, QFileDialog,
    QScrollBar, QSizePolicy
)
from PySide6.QtGui import QPalette, QColor, QIcon, QPainter, QPen

# --- カスタムウィジェット ---
class QtBlock(QFrame):
    # QtBlockウィジェットを初期化します。
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #333333; border: 1px solid #4A4A4A; border-radius: 4px;")
        self.setMinimumWidth(1000)
        # self.setFixedSize(width, height) # ブロックのサイズを固定 (コメントアウト)
        self.setFixedHeight(height) # ブロックの高さを固定し、幅はレイアウトに任せる
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("border: none;")
        layout.addWidget(self.text_edit)

class QtFrame(QFrame):
    # QtFrameウィジェットを初期化します。
    def __init__(self, number, scroll_area, parent=None):
        super().__init__(parent)
        self.scroll_area = scroll_area
        self.number = number
        self.blocks = []
        self.setStyleSheet("background-color: #2C2C2C; border: 1px solid #4A4A4A; border-radius: 5px;")
        self.setMinimumWidth(300) # 最低のフレームの横幅を決める

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10) # 左、上、右、下の順でフレームと要素の間を決める
        self.main_layout.setSpacing(10) # フレームの要素と要素の間の空白を決める
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel(f"Frame {self.number}")
        title_label.setStyleSheet("color: #AAAAAA; padding: 5px;")
        title_label.setMinimumHeight(30) # 最低のラベルの横幅を決める

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.main_layout.addLayout(title_layout)
        self.main_layout.addStretch(1) # 余白を吸収するストレッチを追加

        self.is_resizing = False
        self.resizing_edge = None
        self.resize_edge_width = 5
        self.prev_sibling_widget = None # 前のフレームを格納するため
        self.setMouseTracking(True)

        self.resize_timer = QTimer(self)
        self.resize_timer.timeout.connect(self.auto_resize_step)
        self.auto_resize_direction = None

    # フレームに新しいブロックを追加します。
    def add_block(self, width, height):
        block = QtBlock(width, height)
        # ストレッチ(常に最後の要素)の前にブロックを挿入する
        insert_index = self.main_layout.count() - 1
        self.main_layout.insertWidget(insert_index, block, 0, Qt.AlignmentFlag.AlignTop)
        self.blocks.append(block) # リストの末尾に追加
        
        # 追加したブロックの幅も即座に更新する
        margins = self.main_layout.contentsMargins()
        block_width = self.contentsRect().width() - margins.left() - margins.right()
        if block_width < 0:
            block_width = 0
        block.setFixedWidth(block_width)
        
        self.update() # フレームを再描画して線を追加

        return block

    def paintEvent(self, event):
        super().paintEvent(event)
        if len(self.blocks) < 2:
            return

        painter = QPainter(self)
        pen = QPen(QColor("#555555"))
        pen.setWidth(2)
        painter.setPen(pen)

        for i in range(len(self.blocks) - 1):
            start_block = self.blocks[i]
            end_block = self.blocks[i+1]

            # 開始点: start_blockの下部中央
            start_pos = start_block.geometry().bottomLeft()
            start_pos.setX(start_pos.x() + start_block.width() / 2)

            # 終了点: end_blockの上部中央
            end_pos = end_block.geometry().topLeft()
            end_pos.setX(end_pos.x() + end_block.width() / 2)

            painter.drawLine(start_pos, end_pos)

    def resizeEvent(self, event):
        """フレームのリサイズ時に呼び出されるイベントハンドラ"""
        super().resizeEvent(event)
        # フレームの左右のマージン (10px * 2) を考慮
        margins = self.main_layout.contentsMargins()
        block_width = self.contentsRect().width() - margins.left() - margins.right()
        
        if block_width < 0:
            block_width = 0

        for block in self.blocks:
            block.setFixedWidth(block_width)

    def auto_resize_step(self):
        if not self.is_resizing or self.auto_resize_direction is None:
            return

        scroll_step = 10
        current_width = self.width()
        
        if self.auto_resize_direction == 'right':
            self.setFixedWidth(current_width + scroll_step)
            current_scroll_value = self.scroll_area.horizontalScrollBar().value()
            self.scroll_area.horizontalScrollBar().setValue(current_scroll_value + scroll_step)
        
        elif self.auto_resize_direction == 'left':
            if self.prev_sibling_widget:
                prev_width = self.prev_sibling_widget.width()
                if prev_width > scroll_step and current_width > -scroll_step:
                    self.prev_sibling_widget.setFixedWidth(prev_width - scroll_step)
                    self.setFixedWidth(current_width + scroll_step)
                    current_scroll_value = self.scroll_area.horizontalScrollBar().value()
                    self.scroll_area.horizontalScrollBar().setValue(current_scroll_value - scroll_step)


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
            viewport = self.scroll_area.viewport()
            viewport_rect = QRect(viewport.mapToGlobal(viewport.rect().topLeft()), viewport.mapToGlobal(viewport.rect().bottomRight()))
            cursor_pos_x = event.globalPosition().x()

            edge_zone_width = 40 # 自動リサイズ用の境界領域を定義する

            if cursor_pos_x > viewport_rect.right() - edge_zone_width:
                self.auto_resize_direction = 'right'
                if not self.resize_timer.isActive():
                    self.resize_timer.start(50)
            elif cursor_pos_x < viewport_rect.left() + edge_zone_width:
                self.auto_resize_direction = 'left'
                if not self.resize_timer.isActive():
                    self.resize_timer.start(50)
            else:
                if self.resize_timer.isActive():
                    self.resize_timer.stop()
                self.auto_resize_direction = None

                # Manual resize logic
                delta = event.globalPosition().toPoint() - self.resize_start_pos
                if self.resizing_edge == 'right':
                    new_width = self.original_width + delta.x()
                    if new_width > 0:
                        self.setFixedWidth(new_width)
                elif self.resizing_edge == 'left' and self.prev_sibling_widget:
                    new_prev_width = self.original_prev_sibling_width + delta.x()
                    new_self_width = self.original_width - delta.x()
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
            if self.resize_timer.isActive():
                self.resize_timer.stop()
            self.auto_resize_direction = None
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

        # --- ブロックのデフォルトサイズ ---
        self.block_width = 280
        self.block_height = 80

        # --- スタイル変数 ---
        self.sidebar_button_color = "#65F4D4"

        self.script_dir = Path(__file__).parent.parent
        
        self.pressed_keys = set() # 押されているキーを追跡するためのセット

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
        self.mainbar_layout.addStretch(1)

        # --- レイアウトへの追加 ---
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.mainbar_scroll_area)
        splitter.setSizes([150, 650])

        main_layout.addWidget(self.menubar)
        main_layout.addWidget(splitter)

        QApplication.instance().installEventFilter(self)

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
        new_frame = QtFrame(frame_number, self.mainbar_scroll_area)
        # ストレッチ以外のウィジェットの数を挿入インデックスとする
        insert_index = self.mainbar_layout.count() - 1
        self.mainbar_layout.insertWidget(insert_index, new_frame)
        self.frames.append(new_frame)
        self.select_frame(new_frame)

    # 現在選択されているフレームにブロックを追加します。
    def add_block_to_selected_frame(self):
        if self.selected_frame:
            self.selected_frame.add_block(self.block_width, self.block_height)

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

    # 選択されたブロックをハイライトします。
    def select_block(self, block_to_select):
        self.selected_block = block_to_select
        # すべてのフレームのすべてのブロックをチェック
        for frame in self.frames:
            for block in frame.blocks:
                if block == block_to_select:
                    # 選択時のスタイル
                    block.setStyleSheet("background-color: #333333; border: 2px solid #4A90E2; border-radius: 4px;")
                    # 対応するテキストボックスにフォーカスを当てる
                    block.text_edit.setFocus()
                else:
                    # 非選択時のスタイル
                    block.setStyleSheet("background-color: #333333; border: 1px solid #4A4A4A; border-radius: 4px;")

    # すべてのブロックの選択を解除します。
    def deselect_all_blocks(self):
        self.select_block(None)

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
            self.add_frame()
            new_frame = self.frames[-1] # Get the newly added frame
            for block_texts in frame_data:
                new_block = new_frame.add_block(self.block_width, self.block_height)
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

    def select_frame_left(self):
        """選択されているフレームの選択を一つ左に移します。"""
        if not self.frames:
            return

        if not self.selected_frame:
            self.select_frame(self.frames[-1])
            return

        try:
            current_index = self.frames.index(self.selected_frame)
        except ValueError:
            return

        if current_index > 0:
            self.select_frame(self.frames[current_index - 1])

    def select_frame_right(self):
        """選択されているフレームの選択を一つ右に移します。"""
        if not self.frames:
            return

        if not self.selected_frame:
            self.select_frame(self.frames[0])
            return
            
        try:
            current_index = self.frames.index(self.selected_frame)
        except ValueError:
            return

        if current_index < len(self.frames) - 1:
            self.select_frame(self.frames[current_index + 1])

    def selected_block_up(self):
        """選択されているブロックの選択を一つ上に移します。"""
        if not self.selected_frame or not self.selected_frame.blocks:
            return

        # ブロックが選択されていない場合、最後のブロックを選択する
        if not self.selected_block:
            self.select_block(self.selected_frame.blocks[-1])
            return

        try:
            current_index = self.selected_frame.blocks.index(self.selected_block)
        except ValueError:
            return

        # 一番上でなければ、一つ上のブロックを選択する
        if current_index > 0:
            self.select_block(self.selected_frame.blocks[current_index - 1])

    def selected_block_down(self):
        """選択されているブロックの選択を一つ下に移します。"""
        if not self.selected_frame or not self.selected_frame.blocks:
            return

        # ブロックが選択されていない場合、最初のブロックを選択する
        if not self.selected_block:
            self.select_block(self.selected_frame.blocks[0])
            return
            
        try:
            current_index = self.selected_frame.blocks.index(self.selected_block)
        except ValueError:
            return

        # 一番下でなければ、一つ下のブロックを選択する
        if current_index < len(self.selected_frame.blocks) - 1:
            self.select_block(self.selected_frame.blocks[current_index + 1])

    def eventFilter(self, watched, event):
        # --- キーイベントの処理 ---
        if event.type() == QEvent.Type.KeyPress:
            self.pressed_keys.add(event.key())

            # ブロック選択移動 (Ctrl + Alt + ↑/↓)
            required_keys_block = {Qt.Key.Key_Control, Qt.Key.Key_Alt}
            if required_keys_block.issubset(self.pressed_keys):
                if event.key() == Qt.Key.Key_Up:
                    self.selected_block_up()
                    return True # イベントを消費
                if event.key() == Qt.Key.Key_Down:
                    self.selected_block_down()
                    return True # イベントを消費

            # フレーム選択移動 (Ctrl + Tab + ←/→)
            required_keys_frame = {Qt.Key.Key_Control, Qt.Key.Key_Tab}
            if required_keys_frame.issubset(self.pressed_keys):
                if event.key() == Qt.Key.Key_Left:
                    self.select_frame_left()
                    return True
                if event.key() == Qt.Key.Key_Right:
                    self.select_frame_right()
                    return True

        if event.type() == QEvent.Type.KeyRelease:
            self.pressed_keys.discard(event.key())
        
        # --- マウスプレスイベントの処理 ---
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                clicked_widget = QApplication.widgetAt(event.globalPosition().toPoint())
                
                # ウィンドウ外のクリック
                if not clicked_widget:
                    self.deselect_all_frames()
                    self.deselect_all_blocks()
                    return False

                ancestor = clicked_widget
                clicked_frame = None
                clicked_block = None
                is_on_interactive_widget = False

                # クリックされたウィジェットの祖先をたどり、ブロックとフレームを特定
                while ancestor is not None:
                    if clicked_block is None and isinstance(ancestor, QtBlock):
                        clicked_block = ancestor
                    
                    if isinstance(ancestor, QtFrame):
                        clicked_frame = ancestor
                        break # フレームまで到達したら終了
                    
                    if isinstance(ancestor, (QPushButton, QToolButton, QScrollBar)):
                        is_on_interactive_widget = True
                        break
                    ancestor = ancestor.parent()

                # フレームがクリックされた場合の処理
                if clicked_frame:
                    self.select_frame(clicked_frame)
                    # ブロックもクリックされていれば選択
                    if clicked_block:
                        self.select_block(clicked_block)
                    # フレームのみクリックされた場合はブロックの選択を解除
                    else:
                        self.deselect_all_blocks()
                # インタラクティブなウィジェット以外で、フレームの外側がクリックされた場合
                elif not is_on_interactive_widget:
                    self.deselect_all_frames()
                    self.deselect_all_blocks()

            return False
        
        # このフィルターで処理しない他のすべてのイベント
        return False

    def keyPressEvent(self, event):
        # Ctrlキーが押された場合 (シンプルなショートカットはこちらで処理)
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_B:
                self.add_block_to_selected_frame()
            if event.key() == Qt.Key.Key_F:
                self.add_frame()
        super().keyPressEvent(event)



if __name__ == "__main__":
    # Set QT_IM_MODULE for Japanese input support
    # os.environ['QT_IM_MODULE'] = 'fcitx' 

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