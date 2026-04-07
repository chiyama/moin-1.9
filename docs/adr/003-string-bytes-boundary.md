# ADR-003: str/bytes 境界ルール

## Status
Accepted

## Background
Python 2 では `str` と `unicode` が暗黙変換されたが、Python 3 では
`str` (テキスト) と `bytes` (バイナリ) は明確に区別される。
MoinMoin は wiki テキスト、ファイル I/O、HTTP、キャッシュ (pickle) など
多様なデータ形式を扱うため、境界を明確にする必要がある。

## Decision

| データ種別 | 型 |
|---|---|
| Wiki ページ内容、ページ名、ユーザー入力 | `str` |
| ファイルシステムパス | `str` |
| HTTP レスポンスボディ | `bytes` |
| キャッシュデータ、pickle データ | `bytes` |
| hashlib / hmac の引数 | `bytes` (文字列は `.encode()` してから渡す) |
| ログファイル I/O | `bytes` (行単位でデコード) |

テキストファイルの読み書き:
- `open(path, encoding='utf-8')` を使う
- `codecs.open()` は使わない (ADR-001 参照)
- バイナリファイルは `open(path, 'rb')` / `open(path, 'wb')`

## Consequences
- 全モジュールで上記境界を遵守する
- 違反箇所は `str`/`bytes` の `TypeError` として実行時に検出される
- 検証: `python -m pytest` でテストを実行し、TypeError が出ないことを確認
