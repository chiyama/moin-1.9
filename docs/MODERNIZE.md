# MoinMoin 近代化作業ガイド

本ドキュメントは、Python 3 移行後の MoinMoin を「実用レベル」に引き上げるための
セッション単位の作業計画である。各セッションは独立して実行でき、前のセッションの
成果に依存する場合は明記している。

進捗は各項目の Status を更新して管理する。

## Status 凡例

- `[ ]` 未着手
- `[~]` 作業中・部分完了
- `[x]` 完了・検証済み

---

## Session 1: ページ編集 (PageEditor)

**対象モジュール**: `PageEditor.py`, `action/edit.py`, `action/Save.py`, `caching.py`

**ゴール**: Wiki ページの作成・編集・保存が動作する

**背景**: 現在ページの閲覧 (Page.py) は動作するが、編集・保存のパスは未検証。
str/bytes 境界の問題が高確率で存在する。

### 作業項目

- [ ] `action/edit.py` — 編集画面の表示を検証
- [ ] `PageEditor.py` — `saveText()` のファイル書き込みパスを修正
  - `codecs.open()` → `open(encoding='utf-8')`
  - ファイルロック周りの動作確認
- [ ] `caching.py` — キャッシュの読み書きを修正
  - pickle の read/write が bytes で動作するか確認
  - `open()` のモード (binary vs text) を監査
- [ ] `action/Save.py` — 保存アクションの動作確認

### 検証手順

```bash
# 1. サーバー起動
python wikiserver.py

# 2. ブラウザで以下を実行
# - http://localhost:8080/TestPage?action=edit にアクセス
# - テキストを入力して保存
# - 保存したページが表示されることを確認

# 3. プログラム的な検証
python -c "
from MoinMoin.web.request import Client
from MoinMoin.wsgiapp import Application
client = Client(Application())
# 編集画面の取得
resp = client.get('/TestPage?action=edit')
print('Edit form:', resp[1])
"
```

### 完了条件

- 新規ページの作成ができる
- 既存ページの編集・保存ができる
- 保存後にページが正しく表示される

---

## Session 2: ユーザー管理 (user, auth)

**対象モジュール**: `user.py`, `auth/__init__.py`, `action/login.py`, `action/newaccount.py`, `action/recoverpass.py`

**ゴール**: ユーザー登録・ログイン・ログアウトが動作する

**背景**: `user.py` は `codecs.open()` でプロファイルを読み書きし、パスワードは
passlib (bundled) でハッシュする。`hashlib` のエンコーディング問題は修正済みだが、
プロファイルの読み書きパスは未検証。

### 作業項目

- [ ] `user.py` — ユーザープロファイルの読み書き
  - `codecs.open()` → `open(encoding='utf-8')`
  - `save()` と `load()` の str/bytes 確認
- [ ] `auth/__init__.py` — MoinAuth (内蔵認証) のフロー確認
- [ ] `action/newaccount.py` — アカウント作成
- [ ] `action/login.py` — ログインフォーム
- [ ] `action/recoverpass.py` — パスワードリセット
- [ ] パスワードハッシュの検証 (passlib 連携)

### 検証手順

```bash
# ブラウザで以下を実行
# 1. http://localhost:8080/?action=newaccount でアカウント作成
# 2. ログアウト後、再度ログイン
# 3. ユーザー設定画面にアクセス
```

### 完了条件

- 新規ユーザーが作成できる
- ログイン・ログアウトが動作する
- ユーザープロファイルが永続化される

---

## Session 3: 添付ファイル (AttachFile)

**対象モジュール**: `action/AttachFile.py`, `action/Load.py`

**ゴール**: ファイルのアップロード・ダウンロード・一覧表示が動作する

**背景**: 添付ファイルはバイナリデータなので `open('rb')`/`open('wb')` で正しく
扱われている可能性が高いが、ファイル名のエンコーディングやフォーム処理に問題がありうる。

### 作業項目

- [ ] `action/AttachFile.py` — アップロード処理 (`_do_upload`)
  - multipart フォームデータの処理
  - ファイル名の str/bytes
- [ ] `action/AttachFile.py` — ダウンロード処理 (`_do_get`)
  - Content-Type, Content-Disposition ヘッダ
- [ ] `action/AttachFile.py` — 一覧表示
- [ ] `action/Load.py` — ページコンテンツのアップロード

### 検証手順

```bash
# 1. テストページを作成 (Session 1 完了が前提)
# 2. 添付ファイルのアップロード
# 3. 添付ファイルの一覧表示
# 4. 添付ファイルのダウンロード
# 5. 日本語ファイル名でのテスト
```

### 完了条件

- テキストファイルとバイナリファイルの両方がアップロードできる
- アップロードしたファイルがダウンロードできる
- 添付ファイル一覧が正しく表示される

---

## Session 4: ログファイルと履歴 (logfile, diff, info)

**対象モジュール**: `logfile/__init__.py`, `logfile/editlog.py`, `action/diff.py`, `action/info.py`

**ゴール**: ページの編集履歴表示と差分表示が動作する

**背景**: ログファイルはバイナリモード (`rb`/`ab`) で開かれ、行ごとにデコードする。
基本的な read パスは修正済みだが、edit log の解析や diff 表示は未検証。

### 作業項目

- [ ] `logfile/editlog.py` — EditLog エントリの解析
  - タブ区切り行のパース
  - タイムスタンプ、ユーザー名、ページ名のデコード
- [ ] `action/info.py` — ページ情報・履歴画面
- [ ] `action/diff.py` — リビジョン間の差分表示
- [ ] `util/diff_html.py` — HTML 差分レンダリング

### 検証手順

```bash
# 1. ページを2回以上編集 (Session 1 完了が前提)
# 2. http://localhost:8080/TestPage?action=info で履歴表示
# 3. 2つのリビジョン間の diff を表示
```

### 完了条件

- ページの編集履歴が正しく表示される
- リビジョン間の差分が表示される

---

## Session 5: 検索 (search)

**対象モジュール**: `search/__init__.py`, `search/builtin.py`, `search/queryparser/`, `action/fullsearch.py`

**ゴール**: ビルトイン検索 (Xapian 不要) が動作する

### 作業項目

- [ ] `search/builtin.py` — MoinSearch の動作確認
- [ ] `search/queryparser/` — クエリパーサーの str 処理
- [ ] `action/fullsearch.py` — 検索結果ページの表示

### 検証手順

```bash
# 1. http://localhost:8080/?action=fullsearch&value=MoinMoin で検索
# 2. 日本語キーワードでの検索
```

### 完了条件

- ページタイトル検索が動作する
- ページ全文検索が動作する
- 検索結果が正しくリンクされる

---

## Session 6: セキュリティ (security, ACL)

**対象モジュール**: `security/__init__.py`, `security/textcha.py`, `security/antispam.py`

**ゴール**: ACL (アクセス制御リスト) が正しく動作する

### 作業項目

- [ ] `security/__init__.py` — ACL パース・評価
- [ ] ACL による読み取り/書き込み制限の検証
- [ ] `security/textcha.py` — テキスト CAPTCHA
- [ ] `security/antispam.py` — スパム対策

### 検証手順

```bash
# 1. wikiconfig.py で ACL を設定
# 2. 匿名ユーザーとログインユーザーで権限の違いを確認
# 3. テスト: python -m pytest MoinMoin/security/_tests/test_security.py -v
```

### 完了条件

- ACL 設定に基づいたアクセス制御が機能する
- テストスイートが通過する

---

## Session 7: メール通知 (mail, events)

**対象モジュール**: `mail/sendmail.py`, `events/__init__.py`, `events/emailnotify.py`

**ゴール**: ページ変更時のメール通知が動作する

### 作業項目

- [ ] `mail/sendmail.py` — SMTP 送信
  - メールヘッダの str/bytes
  - MIME エンコーディング
- [ ] `events/__init__.py` — イベントディスパッチ
- [ ] `events/emailnotify.py` — メール通知ハンドラ

### 検証手順

```bash
# 1. wikiconfig.py で mail_from, mail_smarthost を設定
# 2. ページを購読し、別ユーザーで編集
# 3. メールが送信されることを確認
```

---

## Session 8: XMLRPC API

**対象モジュール**: `xmlrpc/__init__.py`, `xmlrpc/*.py`

**ゴール**: XMLRPC 経由でのページ取得・更新が動作する

### 作業項目

- [ ] `xmlrpc/__init__.py` — XmlRpcBase の動作確認
- [ ] `xmlrpc.client` の bytes/str 処理
- [ ] 基本 API: getPage, putPage, listPages

### 検証手順

```python
import xmlrpc.client
s = xmlrpc.client.ServerProxy('http://localhost:8080/?action=xmlrpc2')
print(s.getAllPages())
```

---

## Session 9: パーサーとフォーマッター

**対象モジュール**: `parser/`, `formatter/`

**ゴール**: 各種マークアップの解析と出力が正しく動作する

### 作業項目

- [ ] `parser/text_moin_wiki.py` — メインパーサーの全機能テスト
- [ ] `parser/highlight.py` — Pygments 連携 (コードブロック)
- [ ] `parser/text_csv.py` — CSV テーブル
- [ ] `parser/text_rst.py` — reStructuredText (docutils 必要)
- [ ] `formatter/text_html.py` — HTML 出力の検証
- [ ] `formatter/text_plain.py` — プレーンテキスト出力

### 検証手順

```bash
# 各種マークアップを含むテストページを作成して表示確認
# - 見出し、リスト、テーブル、リンク、画像
# - コードブロック ({{{#!python ... }}})
# - マクロ (<<TableOfContents>>, <<Include(...)>>)
```

---

## Session 10: テストスイートの近代化

**対象モジュール**: `_tests/`, 各パッケージの `_tests/`

**ゴール**: テストスイートの通過率を大幅に向上させる

### 作業項目

- [ ] `_tests/test_wikiutil.py` — yield-based テストを `@pytest.mark.parametrize` に書き換え
- [ ] `_tests/test_wsgiapp.py` — 同上
- [ ] 各パッケージの `_tests/` でのテスト通過状況を確認
- [ ] `conftest.py` の改善 (必要に応じて)
- [ ] `imp` → `importlib` の移行 (`config/multiconfig.py`)

### 検証手順

```bash
# 全テスト実行
python -m pytest MoinMoin/ -v --ignore=MoinMoin/support/ -k "not xapian and not ldap and not openid" --tb=short 2>&1 | tail -20
```

### 完了条件

- テスト通過率 80% 以上
- yield-based テストが全て parametrize に変換されている

---

## Session 11: codecs.open 一掃と残存 Python 2 コード除去

**対象**: 全モジュール横断

**ゴール**: 残存する Python 2 パターンを全て除去する

### 作業項目

- [ ] `codecs.open()` → `open(encoding=)` (17ファイル)
- [ ] `imp` モジュール → `importlib` (multiconfig.py)
- [ ] 残存する `unicode` 型参照の除去 (docstring 含む)
- [ ] `# -*- coding: iso-8859-1 -*-` ヘッダの除去
- [ ] `has_key()` の残存箇所を `in` に変更

### 検証手順

```bash
# 残存パターンの検索
grep -rn "codecs.open" MoinMoin/ --include="*.py" | grep -v /support/
grep -rn "import imp" MoinMoin/ --include="*.py" | grep -v /support/
grep -rn "has_key" MoinMoin/ --include="*.py" | grep -v /support/
```

---

## 全体の依存関係

```
Session 1 (PageEditor)  ← 基盤。他の多くのセッションの前提
    ↓
Session 2 (user/auth)   ← Session 3,6,7 の前提
    ↓
Session 3 (AttachFile)
Session 4 (logfile/diff) ← Session 1 の後ならいつでも
Session 5 (search)       ← 独立して実行可能
Session 6 (security)     ← Session 2 の後
Session 7 (mail)         ← Session 2 の後
Session 8 (XMLRPC)       ← 独立して実行可能
Session 9 (parser)       ← 独立して実行可能
Session 10 (tests)       ← 全セッション後が理想だが途中でも可
Session 11 (cleanup)     ← 最後に実行
```
