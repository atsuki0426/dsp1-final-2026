import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# GoogleのGitHubリポジトリ一覧
BASE_URL = "https://github.com/orgs/google/repositories"

# User-Agent
headers = {
    "User-Agent": "UniversitySitemapStudentBot/1.0"
}

# スター数を整数に変換する関数
def convert_stars(stars):
    stars = stars.replace(",", "").strip().lower()

    if stars.endswith("k"):
        return int(float(stars[:-1]) * 1000)

    if stars.endswith("m"):
        return int(float(stars[:-1]) * 1000000)

    return int(stars)


# SQLiteデータベースに接続
conn = sqlite3.connect("repositories.db")
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

conn.commit()

# 初期設定
page = 41
total = 0
seen_names = set()

try:
    # 最後のページまで繰り返す
    while True:

        # 2ページ目以降は5秒待機
        if page > 1:
            time.sleep(5)

        # ページ番号を指定
        url = f"{BASE_URL}?page={page}"

        print(f"\n===== {page}ページ目 =====")
        print("アクセスURL:", url)

        # HTML取得
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        print("ステータスコード:", response.status_code)

        response.raise_for_status()

        # HTML解析
        soup = BeautifulSoup(response.text, "html.parser")

        # リポジトリ一覧
        repositories = soup.select("h3")

        count = 0
        data = []

        # 各リポジトリの情報を取得
        for repo in repositories:

            # Googleのリポジトリか確認
            link = repo.select_one('a[href^="/google/"]')

            if link is None:
                continue

            # リポジトリ名
            name = link.get_text(strip=True)

            # 親要素
            parent = repo.find_parent("li")

            if parent is None:
                continue

            # 主要言語
            language_tag = parent.select_one(
                '[class*="PrimaryLanguageName"]'
            )

            if language_tag:
                language = language_tag.get_text(strip=True)
            else:
                language = "不明"

            # スター数
            stars_tag = parent.select_one(
                'a[href$="/stargazers"]'
            )

            if stars_tag:
                stars_text = stars_tag.get_text(" ", strip=True)

                try:
                    stars = convert_stars(stars_text)
                except ValueError:
                    print("スター数の変換に失敗:", name)
                    continue
            else:
                stars = 0

            # 取得したデータを一時保存
            data.append((name, language, stars))

        # リポジトリが取得できなければ終了
        if len(data) == 0:
            print("リポジトリが取得できなかったため終了します。")
            break

        # 同じページを繰り返していないか確認
        names = set(row[0] for row in data)

        if names.issubset(seen_names):
            print("既に取得したリポジトリだけだったため終了します。")
            break

        # データベースに保存
        for name, language, stars in data:

            cursor.execute("""
                INSERT INTO repositories (name, language, stars)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    language = excluded.language,
                    stars = excluded.stars
            """, (name, language, stars))

            print(name, language, stars)

            count += 1

        # 保存
        conn.commit()

        seen_names.update(names)
        total += count

        print("このページの取得件数:", count)
        print("累計取得件数:", total)

        # 次のページがあるか確認
        next_link = None

        for a in soup.select("a[href]"):
            if a.get_text(" ", strip=True) == "Next":
                next_link = a
                break

        if next_link is None:
            print("最後のページに到達しました。")
            break

        # 次のページへ
        page += 1

except KeyboardInterrupt:
    print("\nスクレイピングを中断しました。")

except requests.RequestException as e:
    print("\n通信エラー:", e)

finally:
    conn.commit()
    conn.close()

    print("\n===== スクレイピング終了 =====")
    print("今回の取得件数:", total)