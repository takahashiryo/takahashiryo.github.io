# CLAUDE.md — my_web（高橋亮 個人サイト）で作業する Claude 向けメモ

## これは何か
- 高橋亮（東京大学 特任助教）の個人研究者サイト。**日本語 / English / 中文**の3言語。
- Jekyll 4 製。**本番は Cloudflare Pages（独自ドメイン ryotakahashi.me）**。Cloudflare が GitHub 連携で main を直接ビルドする。
  GitHub Pages（takahashiryo.github.io）も `.github/workflows/deploy.yml` で並行稼働している。
- デザインは `../cronos_web`（yokota-cronos.com）に合わせている。明朝（`--serif`）＋青 `#4385f5`、
  セクション見出しは上下罫線つきの `.sechead`。

## 触る前に知っておくべきこと
1. **`_data/` の CSV には手元の作業ファイルから作った派生データが入る**。
   `data_local/` と `*.xlsx` は `.gitignore` 済み。ここに置いたものはコミットしない。
2. **3言語は「1ページ = 1言語 × 1ファイル」構成**。中身は `_includes/page_home.html` /
   `page_list.html` を `lang` 引数つきで include するだけ。文言は `_data/i18n.yml` に集約。
   → 文言を直すときは i18n.yml を直す。ページファイルは基本さわらない。
3. **`baseurl` は空**。独自ドメイン運用なので変更不要。
   サイト内リンクは必ず `relative_url` / `absolute_url` を通すこと（直書き禁止）。
4. **ローカルビルドは動く**（2026-09-02 に確立）。システム Ruby 2.6.10 のままでよいが、
   同梱の bundler 1.17 は解決器が古く arm64 を解せないので、user-install した bundler 2.4 を使う。

   ```bash
   export PATH="$HOME/.gem/ruby/2.6.0/bin:$PATH"   # bundler 2.4.22（gem install --user-install bundler -v 2.4.22）
   bundle install                                   # 初回のみ。gem は ~/.bundle/my_web に入る
   bundle exec jekyll build                         # 0.1 秒ほど
   bash scripts/verify_site.sh                      # CI と同じ検証をローカルで走らせる
   bundle exec jekyll serve                         # http://localhost:4000
   ```

   - **gem の展開先を Dropbox の外に逃がしてある**（`.bundle/config` の `BUNDLE_PATH`）。
     ここを消して Dropbox 配下に入れると数百ファイルの同期が走るので戻さないこと。
   - **`Gemfile.lock` はコミットしない**（gitignore 済み）。手元の lock は
     `PLATFORMS: arm64-darwin-25` に固定されるため、ubuntu で走る CI が解決できなくなる。
   - zsh の `eval "! a | b" >/dev/null` はパイプ否定の終了ステータスを取り違える。
     検証スクリプトで `!` を使わず `test -z "$(...)"` にしているのはこのため。
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

**並び順**は `sortkey`（`YYYYMMDD`）の降順。`day` が空のものは `00` になるので、
同じ月の中では日の分かっているものより後ろに来る。同じ日（または両方とも日が不明）の
ときは 種別 → 掲載先 → タイトル の昇順（`scripts/build_cv.py` の `pub_sort_key`）。
スプレッドシート同期に切り替えるときは、Publications シートに **`day` 列**を
足すこと（無いと日が全部空になり、月単位の並びに戻る）。
一覧ページのフィルタタブはこの値から自動生成される。

将来スプレッドシート同期に切り替える場合は、リポジトリ Variables に `SHEET_ID` を入れるだけで
`.github/workflows/update-data.yml` が動く（先頭行が `year` かを検証してから保存する）。

## 作業の作法
- ユーザーは日本語。返答も日本語。
- commit メッセージ末尾に `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- push 前に `git fetch && git rebase --autostash origin/main`。
