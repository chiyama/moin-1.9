# ADR-002: サードパーティライブラリの vendoring

## Status
Accepted (inherited from upstream MoinMoin)

## Background
MoinMoin は歴史的にサードパーティライブラリを `MoinMoin/support/` に同梱している。
これにより、追加の pip install なしで動作する。

## Decision
vendoring を継続する。`MoinMoin/support/` に配置し、`MoinMoin/__init__.py` で
`sys.path` に追加する。

現在の bundled ライブラリ:
- werkzeug 1.0.1
- passlib 1.7.2
- pygments 2.5.2
- parsedatetime 2.6
- secure_cookie 0.1.0
- htmlmarkup.py (custom, ported from Trac)
- md5crypt.py (custom)
- BasicAuthTransport.py (custom)

**真実源**: `MoinMoin/support/` ディレクトリ内の実ファイル。
バージョンは各ライブラリの `__init__.py` や `_version` で確認すること。

## Alternatives Considered
- pip 依存に切り替え: デプロイの手軽さが失われる
- 一部のみ vendoring: 管理が複雑になる

## Consequences
- `import werkzeug` で直接 import する (`from MoinMoin.support import ...` は使わない)
- ライブラリ更新時は `MoinMoin/support/` 配下を丸ごと差し替える
