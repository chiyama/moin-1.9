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

## 既知の制約
- `test_wikiutil.py`, `test_wsgiapp.py` は yield-based テスト (deprecated)
  - → `@pytest.mark.parametrize` への書き換えが必要 (TODO)
- **真実源**: テストファイル自体と `python -m pytest` の実行結果
