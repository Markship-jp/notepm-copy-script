import requests
import json
import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# .env ファイルから変数を取得
TEAM_DOMAIN = os.getenv("TEAM_DOMAIN")
API_TOKEN = os.getenv("API_TOKEN")
SOURCE_NOTE_CODE = os.getenv("SOURCE_NOTE_CODE")
TARGET_NOTE_CODE = os.getenv("TARGET_NOTE_CODE")

# UTF-8バックスラッシュエスケープに変換する関数
def convert_to_utf8_escape(text):
    return json.dumps(text)

# 1. コピー元ノート内のすべてのフォルダを取得
print(f"コピー元ノート ({SOURCE_NOTE_CODE}) のフォルダを取得中...")
response = requests.get(
    f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/notes/{SOURCE_NOTE_CODE}/folders",
    headers={"Authorization": f"Bearer {API_TOKEN}"}
)

if response.status_code != 200:
    print(f"エラー: フォルダの取得に失敗しました。ステータスコード: {response.status_code}")
    exit(1)

folders = response.json().get("folders", [])

# 2. ノート内のすべてのページを取得
print(f"ノート ({SOURCE_NOTE_CODE}) の全ページを取得中...")
pages_response = requests.get(
    f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/pages",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    params={
        "note_code": SOURCE_NOTE_CODE,
        "per_page": 100
    }
)

all_pages = pages_response.json().get("pages", [])

# 3. フォルダごとにページをコピー
for folder in folders:
    folder_name = folder.get("name")
    folder_id = folder.get("folder_id")

    if not folder_name or not folder_id:
        continue

    utf8_folder_name = convert_to_utf8_escape(folder_name)

    request_data = {
        "name": json.loads(utf8_folder_name)
    }

    print(f"フォルダ '{folder_name}' をコピー先ノート ({TARGET_NOTE_CODE}) に作成中...")
    new_folder_response = requests.post(
        f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/notes/{TARGET_NOTE_CODE}/folders",
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json; charset=UTF-8"
        },
        data=json.dumps(request_data)
    )

    new_folder = new_folder_response.json().get("folder")
    new_folder_id = new_folder.get("folder_id") if new_folder else None

    if not new_folder_id:
        print(f"エラー: フォルダ '{folder_name}' の作成に失敗しました。スキップします。")
        continue

    folder_pages = [page for page in all_pages if page.get("folder_id") == folder_id]

    if not folder_pages:
        print(f"フォルダ '{folder_name}' にページがありません。")
        continue

    print(f"フォルダ '{folder_name}' にページをコピー中...")
    for page in folder_pages:
        page_code = page["page_code"]
        page_title = page["title"]

        page_content_response = requests.get(
            f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/pages/{page_code}",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )

        page_content = page_content_response.json().get("page", {}).get("body", "")

        if not page_content:
            print(f"エラー: ページ '{page_title}' の取得に失敗しました。スキップします。")
            continue

        page_data = {
            "note_code": TARGET_NOTE_CODE,
            "folder_id": new_folder_id,
            "title": page_title,
            "body": page_content,
            "memo": f"Copied from {SOURCE_NOTE_CODE}"
        }

        requests.post(
            f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/pages",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            },
            data=json.dumps(page_data)
        )

    print(f"フォルダ '{folder_name}' のページコピーが完了しました。")

# 4. ルートにあるページ（フォルダに属さないページ）をコピー
print("ルートにあるページをコピー中...")
root_pages = [page for page in all_pages if page.get("folder_id") is None]

if root_pages:
    for page in root_pages:
        page_code = page["page_code"]
        page_title = page["title"]

        page_content_response = requests.get(
            f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/pages/{page_code}",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )

        page_content = page_content_response.json().get("page", {}).get("body", "")

        if not page_content:
            print(f"エラー: ルートページ '{page_title}' の取得に失敗しました。スキップします。")
            continue

        page_data = {
            "note_code": TARGET_NOTE_CODE,
            "title": page_title,
            "body": page_content,
            "memo": f"Copied from {SOURCE_NOTE_CODE}"
        }

        requests.post(
            f"https://{TEAM_DOMAIN}.notepm.jp/api/v1/pages",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            },
            data=json.dumps(page_data)
        )

    print("ルートページのコピーが完了しました。")
else:
    print("ルートページはありません。")

print("すべてのフォルダとページのコピーが完了しました。")
