# CLAUDE.md — エージェント作業入口

## 最初に読むもの
1. この文書 (作業の進め方・禁止事項)
2. [docs/policies/coding.md](docs/policies/coding.md) — コーディングルール
3. [docs/policies/testing.md](docs/policies/testing.md) — テスト規約
4. [docs/adr/](docs/adr/) — 採用済み設計判断

## 環境セットアップ
```bash
source .venv/Scripts/activate    # Windows (Git Bash)
# source .venv/bin/activate      # Linux/Mac
```

## 検証コマンド
```bash
# サーバー起動
python wikiserver.py

# テスト実行
python -m pytest MoinMoin/_tests/test_error.py -v
python -m pytest MoinMoin/_tests/ \
  --ignore=MoinMoin/_tests/test_wikiutil.py \
  --ignore=MoinMoin/_tests/test_wsgiapp.py -v
```

## 作業の進め方
1. まず計画を示す
2. 小さく変更する
3. 変更ごとにテストで検証する
4. 現在の作業計画: [docs/runbooks/modernize.md](docs/runbooks/modernize.md)

## 禁止事項
- `codecs.open()` を使うこと → `open(encoding='utf-8')` を使う
- `from MoinMoin.support import ...` → `import werkzeug` 等で直接 import
- コードで確認していない内容を断定的にドキュメントに書くこと
- `MoinMoin/support/` 配下の vendored コードを編集すること

## 真実源の優先順位
コード > テスト > 設定ファイル > ADR > policy > ドキュメント説明文
