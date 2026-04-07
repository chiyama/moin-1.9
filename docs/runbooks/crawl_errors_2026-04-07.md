# クロール調査結果 (2026-04-07)

トップページからリンクを辿り、500 エラーが発生する箇所を調査した結果。
300ページ巡回、5種類のユニークなエラーを検出。

---

## Error 1: AttachFile._get_files — `str.decode()` (影響: 大)

- **症状**: 添付ファイルを持つページの表示が全て 500
- **影響範囲**: WikiSandBox, HelpOnMoinWikiSyntax, 各言語の FrontPage 等、約100ページ以上
- **ファイル**: `MoinMoin/action/AttachFile.py:601`
- **エラー**: `AttributeError: 'str' object has no attribute 'decode'`
- **原因**: Python 3 の `os.listdir()` は `str` を返すが、`.decode()` を呼んでいる
- **トレースバック**:
  ```
  theme/__init__.py:1755 send_title → AttachFile.send_link_rel()
  AttachFile.py:623 send_link_rel → _get_files()
  AttachFile.py:601 _get_files:
    files = [fn.decode(config.charset) for fn in os.listdir(attach_dir)]
  ```

---

## Error 2: PageEditor.sendEditor — `str.decode()` (影響: 大)

- **症状**: 全ページの `?action=edit&editor=text` が 500
- **影響範囲**: 全ページの編集操作
- **ファイル**: `MoinMoin/PageEditor.py:350`
- **エラー**: `AttributeError: 'str' object has no attribute 'decode'`
- **原因**: `"hidden".decode(...)` — Python 2 の bytes リテラルを前提としたコード
- **トレースバック**:
  ```
  action/edit.py:78 execute → pg.sendEditor()
  PageEditor.py:350:
    request.write(html.INPUT(type="hidden".decode(name="action", value="edit")))
  ```

---

## Error 3: action/info.py — SyntaxError (影響: 大)

- **症状**: 全ページの `?action=info` が 500
- **影響範囲**: 全ページの情報/履歴表示
- **ファイル**: `MoinMoin/action/info.py:37`
- **エラー**: `SyntaxError: invalid syntax`
- **原因**: 過去の移行で壊れた構文: `.encode('utf-8')` の挿入位置が誤り
- **コード**:
  ```python
  digest = hashlib.new('sha1', page.get_raw_body(.encode('utf-8')).encode(config.charset)).hexdigest().upper()
  ```
  正しくは `page.get_raw_body().encode(config.charset)` のはず。

---

## Error 4: fullsearch — `str.decode()` (影響: 大)

- **症状**: 全文検索が 500
- **影響範囲**: 検索機能全体
- **ファイル**: `MoinMoin/search/queryparser/__init__.py:157`
- **エラー**: `AttributeError: 'str' object has no attribute 'decode'`
- **原因**: Python 3 では query は既に `str` だが `.decode()` を呼んでいる
- **トレースバック**:
  ```
  action/fullsearch.py:189 → queryparser/__init__.py:157:
    query = query.decode(config.charset)
  ```

---

## Error 5: formatter/__init__.py — `import formatter, htmllib` (影響: 中)

- **症状**: テーブル属性エラー時のフォールバック表示で 500
- **影響範囲**: テーブル構文を含むページの特定条件下
- **ファイル**: `MoinMoin/formatter/__init__.py:373`
- **エラー**: `ModuleNotFoundError: No module named 'formatter'`
- **原因**: `formatter` と `htmllib` は Python 3.x で削除済み
- **トレースバック**:
  ```
  parser/text_moin_wiki.py:1537 format → _getTableAttrs()
  parser/text_moin_wiki.py:1143 → wikiutil.parseAttributes()
  wikiutil.py:2004 → table_extension() → formatter.rawHTML()
  formatter/__init__.py:373:
    import formatter, htmllib
  ```

---

## Error 6: SpellCheck — `sort()` with positional arg (影響: 低)

- **症状**: `?action=SpellCheck` が 500
- **影響範囲**: スペルチェック機能
- **ファイル**: `MoinMoin/action/SpellCheck.py:168`
- **エラー**: `TypeError: sort() takes no positional arguments`
- **原因**: Python 3 の `list.sort()` は比較関数を位置引数で受け取れない (`key=` を使う必要がある)
- **コード**:
  ```python
  badwords.sort(lambda x, y: cmp(x.lower(), y.lower()))
  ```

---

## Error 7: WantedPages / OrphanedPages — タイムアウト (影響: 低)

- **症状**: `/WantedPages`, `/OrphanedPages` がタイムアウト (10秒以上)
- **影響範囲**: 2ページのみ
- **原因**: 未調査。全ページスキャンが重すぎるか、内部で無限ループしている可能性

---

## 全量スキャン (pytest --run-slow) で追加発見されたエラー

### Error 8: Creole パーサー — `unichr` is not defined (影響: 中)

- **症状**: Creole 記法を使うページの表示が 500
- **影響範囲**: 32ページ (各言語のSyntaxReference等)
- **ファイル**: `MoinMoin/parser/_creole.py:147-148`
- **エラー**: `NameError: name 'unichr' is not defined`
- **原因**: Python 3 では `unichr` → `chr`
- **状態**: 未修正

### Error 9: RecentChanges — EditLogLine の比較 (影響: 低)

- **症状**: AbandonedPages 表示で 500
- **ファイル**: `MoinMoin/macro/RecentChanges.py:172`
- **エラー**: `TypeError: '<' not supported between instances of 'EditLogLine' and 'EditLogLine'`
- **原因**: Python 3 では `__lt__` 等の比較メソッドが必要
- **状態**: 未修正

---

## クロール統計

- 巡回ページ数: 300 (キュー残 1358)
- エラー合計: 107 (500: 82件, 404: 23件, タイムアウト: 2件)
- 404 は未インストールの言語パックのページのため正常

---

## 正常動作確認済み (200)

- `/` (トップ)
- `/LanguageSetup` (ページ表示)
- `?action=newaccount` (修正済み)
- `?action=login`
- `?action=diff`
- `?action=recall`
- `?action=subscribe`
- `?action=userprefs`
- `?action=raw`
- `?action=print`
- `?action=sitemap`
- `?action=chart`
- `?action=bookmark`
- `?action=LikePages`
- `?action=LocalSiteMap`
- `?action=MyPages`
- `?action=DesktopEdition`
- `?action=thread_monitor`
- `?action=Load`
- `?action=Save`
- `?action=AttachFile`
- `?action=Despam`
- `?action=PackagePages`
- `?action=SyncPages`
- `?action=CopyPage`
- `?action=titleindex`
- `/TitleIndex`, `/WordIndex`, `/FindPage`, `/RecentChanges`
- `/FrontPage` (添付なし)
- `/HelpOnFormatting`
- `/SystemInfo`
