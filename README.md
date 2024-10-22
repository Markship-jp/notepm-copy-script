# NotePM API コピー スクリプト

NotePMのAPIを使って、指定したノート内のフォルダとページを別のノートにコピーするPythonスクリプト。

## 準備

### 1. リポジトリのクローン

リポジトリをクローンする。

```bash
git clone https://github.com/your-username/notepm-copy-script.git
cd notepm-copy-script
```

### 2. 必要なライブラリのインストール

Pythonライブラリをインストールする。

```bash
pip install -r requirements.txt
```

### 3. `.env` ファイルの作成

プロジェクトルートに `.env` ファイルを作成する。まず、`.env.example` をコピーする。

```bash
cp .env.example .env
```

次に、`.env` ファイルを編集し、以下の情報を入力する。

```bash
TEAM_DOMAIN=your_team_domain   # 例: markship
API_TOKEN=your_api_token       # NotePMのAPIトークン
SOURCE_NOTE_CODE=source_note_code   # コピー元ノートのコード
TARGET_NOTE_CODE=target_note_code   # コピー先ノートのコード
```

## 実行

スクリプトを実行して、指定したノートのフォルダとページをコピーする。

```bash
python copy_notepm.py
```

