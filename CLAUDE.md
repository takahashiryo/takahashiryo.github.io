# CLAUDE.md — my_web（高橋亮 個人サイト）で作業する Claude 向けメモ

## これは何か
- 高橋亮（東京大学 特任助教）の個人研究者サイト。**日本語 / English / 中文**の3言語。
- Jekyll 4 製。GitHub Actions で **GitHub Pages** に配信（`.github/workflows/deploy.yml`）。
- デザインは `../cronos_web`（yokota-cronos.com）に合わせている。明朝（`--serif`）＋青 `#4385f5`、
  セクション見出しは上下罫線つきの `.sechead`。

## 触る前に知っておくべきこと
1. **`_data/` の CSV には手元の作業ファイルから作った派生データが入る**。
   `data_local/` と `*.xlsx` は `.gitignore` 済み。ここに置いたものはコミットしない。
2. **3言語は「1ページ = 1言語 × 1ファイル」構成**。中身は `_includes/page_home.html` /
   `page_list.html` を `lang` 引数つきで include するだけ。文言は `_data/i18n.yml` に集約。
   → 文言を直すときは i18n.yml を直す。ページファイルは基本さわらない。
3. **`baseurl` に注意**。いまはプロジェクトページ用に `/ryotakahashi.github.io`。
   独自ドメインを付けたら `url` を変えて `baseurl: ""` にする。
   サイト内リンクは必ず `relative_url` / `absolute_url` を通すこと（直書き禁止）。
4. **ローカルビルド不可**（システム Ruby 2.6）。検証は push 後の Actions に任せる。
   Liquid のロジックは Python で等価シミュレーションして確認すると安全。
5. **アンカーの着地位置**はヘッダーが sticky なので JS が `scroll-padding-top` を実測して入れている
   （`_layouts/default.html` 末尾）。ヘッダーの高さを変えたらここも確認する。

## データ
| ファイル | 内容 | 由来 |
| --- | --- | --- |
| `_data/publications.csv` | 論文62件 | 手元データから生成 |
| `_data/awards.csv` | 受賞19件 | researchmap API |
| `_data/talks.csv` | 講演10件 | 手元データから生成 |
| `_data/i18n.yml` | 3言語の文言 | 手書き |
| `_data/profile.yml` | リンク・研究テーマ | 手書き＋researchmap |

`type` の値: `journal` / `conference` / `workshop` / `demo` / `poster` / `domestic` / `article`。
一覧ページのフィルタタブはこの値から自動生成される。

将来スプレッドシート同期に切り替える場合は、リポジトリ Variables に `SHEET_ID` を入れるだけで
`.github/workflows/update-data.yml` が動く（先頭行が `year` かを検証してから保存する）。

## 作業の作法
- ユーザーは日本語。返答も日本語。
- commit メッセージ末尾に `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- push 前に `git fetch && git rebase --autostash origin/main`。
