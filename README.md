# CodeSmith Project

CodeSmithは、フローチャートを簡単に作成できるビジュアルプログラミング環境を提供するPythonアプリケーションです。フレームとブロックを使用して、視覚的にプログラムやデータを構築することができます。

## 機能

### インターフェース
- モダンなダークテーマのGUI
- 3つの主要セクション：
  - メニューバー（左端）
  - サイドバー（左側）
  - メインバー（右側）
- ウィンドウサイズ: 600x400ピクセル

### 主要機能
1. フレーム・ブロック管理
   - フレームの追加と管理
   - ブロック内でのテキスト編集
   - フレームサイズの調整（%指定）

2. ファイル操作
   - テキストファイル（.txt）の読み込み
   - JSONファイル（.json）の保存と読み込み
   - ファイルリストの管理

3. ユーザーインターフェース
   - マウスホイールによるスクロール
   - フレーム・ブロックの選択状態の視覚的フィードバック
   - ドラッグ＆ドロップによるブロック配置

## 必要条件
- Python 3.x
- 必要なパッケージ:
  - customtkinter
  - Pillow (PIL)

## インストール方法

1. リポジトリをクローン
```bash
git clone https://github.com/misoudon956/CodeSmith-Project.git
```

2. 必要なパッケージをインストール
```bash
pip install customtkinter Pillow
```

## 使用方法

1. プログラムの実行
```bash
python maincode/CodeSmith.py
```

2. メニューバーの操作
   - ファイルアイコン：ファイル操作メニューを表示
   - ブロックアイコン：ブロック操作メニューを表示

3. フレーム・ブロックの作成
   - フレーム追加：「frame」ボタンをクリック
   - ブロック追加：「block」ボタンをクリック
   - フレーム内でブロックを選択して編集

4. ファイルの保存と読み込み
   - テキストファイルの読み込み：「open_txt_file」
   - JSONファイルの保存：「save_file」
   - JSONファイルの読み込み：「open_file」

## プロジェクト構造
```
CodeSmith Project/
├── README.md
├── maincode/
│   └── CodeSmith.py
├── image/
│   └── menubar/
│       ├── block_icon.png
│       └── file_icon.png
└── test_json/
```
