import sqlite3

# データベースに接続（存在しなければ新規作成）
conn = sqlite3.connect("repositories.db")

# SQLを実行するためのカーソル
cursor = conn.cursor()

# テーブル作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    language TEXT,
    stars INTEGER
)
""")

# 変更を保存
conn.commit()

# 接続を閉じる
conn.close()

print("データベースとテーブルを作成しました。")