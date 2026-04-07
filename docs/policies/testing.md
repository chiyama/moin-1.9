# テストポリシー

## フレームワーク
pytest 9.x

## テストファイルの配置
`MoinMoin/<package>/_tests/test_*.py`

## テスト実行
```bash
# 単体
python -m pytest MoinMoin/_tests/test_error.py -v

# コアテスト (既知の問題ファイルを除外)
python -m pytest MoinMoin/_tests/ \
  --ignore=MoinMoin/_tests/test_wikiutil.py \
  --ignore=MoinMoin/_tests/test_wsgiapp.py -v
```

## テストインフラ
- `conftest.py` の `pytest_runtest_setup` が `self.request` を inject する
- テストクラスは `self.request` 経由で wiki コンテキストにアクセスする

## スモークテスト / 全量スキャン
```bash
# スモークテスト (常時): 既知のPy3回帰パターン 7件, <3秒
python -m pytest MoinMoin/_tests/test_smoke.py::TestSmoke -v

# 全量スキャン (マイルストーン時): 全ページGET, 500でないことを検証, ~70秒
python -m pytest MoinMoin/_tests/test_smoke.py --run-slow -v

# クローラー (リリース前): 実サーバーでリンクを辿りながら検査
python wikiserver.py &
python scripts/crawl-wiki.py --fail-on-500 --report crawl-report.json
```

## 既知の制約
- `test_wikiutil.py`, `test_wsgiapp.py` は yield-based テスト (deprecated)
  - → `@pytest.mark.parametrize` への書き換えが必要 (TODO)
- **真実源**: テストファイル自体と `python -m pytest` の実行結果
