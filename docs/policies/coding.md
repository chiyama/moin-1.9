# コーディングポリシー

このプロジェクトで守るべきルール。根拠となる ADR へのリンクを付記する。

## ファイルエンコーディング
- 全テキストファイルは UTF-8
- 旧 `# -*- coding: iso-8859-1 -*-` ヘッダは削除してよい
- テキスト読み書き: `open(path, encoding='utf-8')`
- バイナリ読み書き: `open(path, 'rb')` / `open(path, 'wb')`
- `codecs.open()` は使わない → [ADR-003](../adr/003-string-bytes-boundary.md)

## str/bytes 境界
→ [ADR-003](../adr/003-string-bytes-boundary.md) に従う

## import スタイル
- vendored ライブラリは直接 import: `import werkzeug`
  - `from MoinMoin.support import ...` は使わない → [ADR-002](../adr/002-vendored-libs.md)
- optional 依存は try/except ImportError で guard:
  `ldap`, `openid`, `xapian`, `MySQLdb`, `gdchart`

## Python 2 → 3 で消えた API
修正時に参照するリスト。**真実源はコード**。ここに無い問題もありうる。

| 旧 | 新 | 備考 |
|---|---|---|
| `time.clock()` | `time.perf_counter()` | |
| `array.tostring()` | `array.tobytes()` | |
| `except T, v:` | `except T as v:` | |
| `string.maketrans` | `str.maketrans` | |
| `dircache` | `os.listdir()` | モジュール削除 |
| `UserDict.DictMixin` | `collections.abc.MutableMapping` | |
| `HTMLParseError` | (削除) | Py 3.5 で除去 |
| `imp` | `importlib` | 移行 TODO あり |
| `ImportError` メッセージ | `'foo' in str(err)` | Py3 ではクォート付き |
