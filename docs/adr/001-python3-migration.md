# ADR-001: Python 2 → Python 3 移行

## Status
Accepted (2024)

## Background
MoinMoin 1.9.11 は Python 2.7 専用だった。Python 2 の EOL (2020-01-01) により、
セキュリティパッチの適用やライブラリの更新が困難になっていた。

## Decision
MoinMoin 1.9.11 を Python 3.10+ へ移植する。`py3-migration` ブランチで作業する。

移植方針:
- 2to3 の自動変換 + 手動修正
- bundled ライブラリ (werkzeug, passlib, pygments) は Py3 対応版に更新
- Py2 専用の依存 (flup, xappy) は削除
- 段階的に動作確認: import → テスト → 手動検証

## Alternatives Considered
- MoinMoin 2.0 への移行: 別プロジェクトであり、データ互換性なし
- 新規 wiki エンジンへの置換: 既存データとカスタマイズの移行コストが大きい

## Consequences
- `str` = テキスト、`bytes` = バイナリの境界を全モジュールで明確化する必要がある
- `codecs.open()` → `open(encoding=)` への統一が必要
- テストスイートの近代化 (yield-based → parametrize) が必要
- 詳細ルールは [docs/policies/coding.md](../policies/coding.md) を参照
