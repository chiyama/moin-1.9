# MoinMoin

MoinMoin wiki エンジンの Python 3 移植版。
オリジナル MoinMoin 1.9.11 (Python 2.7) をフォークし、**Python 3.10+** で動作するよう移植した。

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows

# 初回のみ: underlay データの展開
python -c "import tarfile; tarfile.open('wiki/underlay.tar').extractall('wiki/')"

# 開発サーバー起動
python wikiserver.py
# → http://localhost:8080/
```

## 主要コマンド

| コマンド | 用途 |
|---|---|
| `python wikiserver.py` | 開発サーバー起動 |
| `python -m pytest MoinMoin/_tests/test_error.py -v` | テスト実行 (単体) |
| `pip install -e .` | 開発用インストール |

## ドキュメントマップ

| パス | 内容 |
|---|---|
| [CLAUDE.md](CLAUDE.md) | AI エージェント向け作業入口 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | モジュール構造・成熟度 |
| [docs/adr/](docs/adr/) | 採用済み設計判断 (ADR) |
| [docs/policies/](docs/policies/) | コーディング・テスト規約 |
| [docs/runbooks/modernize.md](docs/runbooks/modernize.md) | 近代化作業計画 |
| [docs/REQUIREMENTS](docs/REQUIREMENTS) | 依存関係 |
| [docs/INSTALL.html](docs/INSTALL.html) | インストール手順 (Py3 向け更新 TODO) |
| [docs/licenses/](docs/licenses/) | ライセンス |

## License

GNU GPL v2 or later. See [LICENSE](LICENSE) for details.
