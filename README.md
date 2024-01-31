
# papersearch

https://papersearch.onrender.com/
## 概要
- このプロジェクトは、学術論文の検索と表示を目的としたWebアプリケーションです。
- Semantic ScholarのAPIを利用して論文情報を取得し、FastAPIとJinja2テンプレートを使用して結果を表示します。

## セットアップ
### 必要条件
- Python 3.8+
- Docker
- Poetry

### インストール手順
1. このリポジトリをクローンします。
   ```
   git clone [リポジトリURL]
   ```
2. 依存関係をインストールします。
   ```
   poetry install
   ```

## 使用方法
### ローカルでの実行
- FastAPIサーバーを起動するには、以下のコマンドを実行します。
   ```
   poetry run uvicorn backend.main:app --reload
   ```
### Dockerを使用した実行
- Dockerを使用してアプリケーションを実行するには、以下のコマンドを実行します。
   ```
   docker build -t myapp .
   docker run -p 8000:8000 myapp
   ```

## テストとリント
- テストを実行するには、以下のコマンドを使用します。
   ```
   poetry run pytest
   ```
- コードのフォーマットとリントチェックには以下のコマンドを使用します。
   ```
   poetry run black .
   poetry run ruff check .
   poetry run mypy .
   ```

## コントリビューション
- コントリビューションを歓迎します。

