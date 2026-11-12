import sqlite3

# データベースに接続
conn = sqlite3.connect("repositories.db")
cursor = conn.cursor()

# 保存されているデータの総件数を取得
cursor.execute("""
    SELECT COUNT(*)
    FROM repositories
""")

total = cursor.fetchone()[0]

print("===== GoogleのGitHubリポジトリ =====")
print("保存件数:", total)

# スター数が多い上位20件を取得
cursor.execute("""
    SELECT name, language, stars
    FROM repositories
    ORDER BY stars DESC
    LIMIT 20
""")

rows = cursor.fetchall()

print("\n===== スター数ランキング TOP20 =====")

for row in rows:
    print("--------------------")
    print("リポジトリ名:", row[0])
    print("主要言語:", row[1])
    print("スター数:", row[2])

# データベース接続を閉じる
conn.close()