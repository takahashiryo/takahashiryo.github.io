# 高橋 亮 個人サイト（日本語 / English / 中文）

**リポジトリ**: `takahashiryo/takahashiryo.github.io`

Jekyll 製の研究者個人サイト。デザインは [JST CRONOS 横田グループのサイト](https://yokota-cronos.com)（明朝＋青の editorial 系）に揃えている。

## 3言語のしくみ

| 言語 | URL | ページファイル |
| --- | --- | --- |
| 日本語 | `/` ・ `/publications/` ・ `/cv/` | `_pages/ja*.html` |
| English | `/en/` ・ `/en/publications/` ・ `/en/cv/` | `_pages/en*.html` |
| 中文 | `/zh/` ・ `/zh/publications/` ・ `/zh/cv/` | `_pages/zh*.html` |

- 文言はすべて **[`_data/i18n.yml`](_data/i18n.yml)** に3言語分まとめてある。ページ側は `lang` を渡すだけ。
- 研究テーマの本文は [`_data/profile.yml`](_data/profile.yml) の `research:` に3言語分ある。
- 論文タイトルなどの書誌情報は**原語のまま**（翻訳しない）。
- 各ページには `hreflang` を入れてあるので、検索エンジンには「同じページの言語違い」と伝わる。

ヘッダーのナビは **Publications と CV の2つ**。論文一覧にはメディア掲載も混ぜてあり、
`Media` タブで絞り込める。CV は 学歴 / 職歴 / 研究費 / 受賞 / 講演 をまとめたページ。

言語を1つ増やすときは、`_data/i18n.yml` にブロックを足し、`_pages/` の3ファイルをコピーして `lang` と `permalink` を変え、`_layouts/default.html` の言語切替に1行足す。

## データの更新

現在の中身は `_data/` の CSV。

| ファイル | 内容 | 件数 |
| --- | --- | --- |
| `_data/publications.csv` | 論文（journal / conference / workshop / demo / poster / domestic / article） | 62 |
| `_data/media.csv` | メディア掲載（論文一覧に混ぜて表示） | 24 |
| `_data/awards.csv` | 受賞 | 19 |
| `_data/talks.csv` | 招待講演など | 10 |
| `_data/grants.csv` | 研究費 | 7 |
| `_data/education.csv` | 学歴 | 3 |
| `_data/experience.csv` | 職歴 | 8 |

受賞・研究費・学歴・職歴・メディア掲載は **researchmap から取り込める**:

```bash
python3 scripts/build_cv.py     # researchmap の公開APIから _data/ を作り直す
```

### スプレッドシート同期に切り替える（推奨）

1. `data_local/` の xlsx を Google スプレッドシートにアップロードする
   （シート名 `Publications` / `Awards` / `Talks` のまま）。
2. 共有設定を **「編集: 自分のみ」＋「リンクを知っている全員: 閲覧者」** にする。
   ⚠️ 閲覧まで止めると取り込みが Google のエラーページを CSV として保存してしまう。
3. GitHub の **Settings → Secrets and variables → Actions → Variables** に
   `SHEET_ID`（スプレッドシートURLの `/d/` と `/edit` の間）を登録する。
4. 以降は毎日 06:00 JST に自動で取り込まれる（`.github/workflows/update-data.yml`）。
   手動なら Actions から «Update data from spreadsheet» を実行。

取り込みは**先頭行が `year` で始まるかを検証**し、CSV でなければ既存ファイルを残したまま失敗する。

## 公開設定

`.github/workflows/deploy.yml` が push のたびに Jekyll をビルドして GitHub Pages へ配信する。
最初に一度だけ **Settings → Pages → Build and deployment → Source を «GitHub Actions»** にする必要がある。

### URL について

リポジトリ名が `ryotakahashi.github.io` なのに対しアカウント名が `takahashiryo` なので、
このままだと **プロジェクトページ** 扱いになり URL は
`https://takahashiryo.github.io/ryotakahashi.github.io/` という冗長なものになる。整えるなら次のどちらか。

| やりたいこと | 手順 | `_config.yml` |
| --- | --- | --- |
| `https://takahashiryo.github.io/` にする | リポジトリ名を `takahashiryo.github.io` に変更 | `url: "https://takahashiryo.github.io"` / `baseurl: ""` |
| 独自ドメイン（ryotakahashi.me）にする | Settings → Pages → Custom domain に設定し、DNS を向ける | `url: "https://ryotakahashi.me"` / `baseurl: ""` |

現在の `_config.yml` はプロジェクトページ（`https://takahashiryo.github.io/ryotakahashi.github.io/`）向けの設定。
**独自ドメイン（例 ryotakahashi.me）を割り当てたら 2行変える**:

```yaml
url     : "https://ryotakahashi.me"
baseurl : ""
```

（サイト内リンクはすべて `relative_url` を通してあるので、この2行だけで切り替わる。）

## 独自ドメイン（ryotakahashi.me）へ移す

**本番は Cloudflare Pages で `https://ryotakahashi.me` に公開されている**（GitHub Pages `https://takahashiryo.github.io/` も同じ内容で並行稼働）。
`ryotakahashi.me` は現在 **Google Sites** が動いていて、DNS も Google のネームサーバーのまま。
Cloudflare に移すと、この Google Sites のページは表に出なくなる（差し替えになる）ので注意。

### 手順

1. **Cloudflare にドメインを追加**
   Cloudflare（無料プラン）で «Add a site» → `ryotakahashi.me`。
   既存の DNS レコードが自動で読み込まれるので、内容を確認してから進む。
   最後に Cloudflare 側のネームサーバー2つが表示される。
2. **レジストラでネームサーバーを変更**
   ドメインは Google Domains 由来なので、現在の管理先（Squarespace Domains）で
   ネームサーバーを 1. の2つに差し替える。反映まで数時間〜1日。
3. **Cloudflare Pages のプロジェクトを作る**（どちらか）
   - **推奨: «Connect to Git»** … このリポジトリを選び、
     Build command `bundle exec jekyll build` / Output directory `_site` を指定。
     トークンもワークフローも不要。
   - **wrangler で送る** … CRONOS サイトと同じ方式。リポジトリに
     Secrets `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` と
     Variables `CLOUDFLARE_PROJECT`（プロジェクト名）を登録すると
     `.github/workflows/deploy-cloudflare.yml` が動き出す。
4. **カスタムドメインを割り当てる**
   Pages プロジェクトの «Custom domains» に `ryotakahashi.me` を追加。
   `www.ryotakahashi.me` は Cloudflare の Redirect Rules で apex に 301 させるときれい。
5. **`_config.yml` を1行変える**

   ```yaml
   url : "https://ryotakahashi.me"
   ```

   （`baseurl` は `""` のままでよい。サイト内リンクは `relative_url` を通してあるので他は触らなくてよい。）

GitHub Pages 側（`takahashiryo.github.io`）はそのまま残しても問題ない。
残す場合は 5. のあと canonical が `ryotakahashi.me` を指すので、検索結果は独自ドメインに寄る。

## ファイル早見表

| やりたいこと | 触る場所 |
| --- | --- |
| 文言・肩書き・自己紹介 | `_data/i18n.yml` |
| リンク（Scholar 等）・研究テーマ | `_data/profile.yml` |
| 論文・受賞・講演 | `_data/*.csv`（スプレッドシート同期に切り替え可） |
| 見た目 | `_includes/style.html` |
| ページ構成 | `_includes/page_home.html` / `page_list.html` |
| ヘッダー・言語切替・meta | `_layouts/default.html` |
