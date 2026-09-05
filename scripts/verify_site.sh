#!/usr/bin/env bash
# _site を CI（.github/workflows/deploy.yml）と同じ基準で検証する。
#   bundle exec jekyll build && bash scripts/verify_site.sh
#
# CI との違いは2点だけ:
#   - 非公開ファイルの検査は git の追跡対象を見る（手元の data_local/ は gitignore 済みで CI には無い）
#   - zsh でも動くよう、パイプ否定ではなく出力が空かどうかで判定する
set -u
fail=0
chk() {  # chk "名前" "コマンド"
  if eval "$2" >/dev/null 2>&1; then printf '  OK   %s\n' "$1"
  else printf '  FAIL %s\n' "$1"; fail=1; fi
}

cd "$(dirname "$0")/.."
test -d _site || { echo "_site が無い。先に bundle exec jekyll build を実行すること"; exit 1; }

echo "--- 6ページ＋補助ファイルが生成されているか ---"
for p in index.html cv/index.html \
         en/index.html en/cv/index.html \
         zh/index.html zh/cv/index.html \
         sitemap.xml robots.txt 404.html; do
  chk "$p" "test -s '_site/$p'"
done

echo "--- 研究テーマの詳細ページ（4テーマ×3言語）---"
for t in e-textile low-power-wearable robot-skin digital-fabrication; do
  for pre in "" "en/" "zh/"; do
    chk "${pre}research/$t/" "test -s '_site/${pre}research/$t/index.html'"
  done
done
chk 'トップのカードが詳細へリンク' 'grep -q "href=\"/research/e-textile/\"" _site/index.html'
chk '詳細ページの件数がカードと一致' '[ "$(grep -o "class=\"entry entry--pub\"" _site/research/e-textile/index.html | wc -l | tr -d " ")" = "$(grep -o "theme-pubs-head\">関連論文 [0-9]* 件" _site/index.html | head -1 | grep -o "[0-9]*")" ]'

echo "--- ナビは Publications と CV の2つ ---"
chk '論文 リンクあり'   'grep -q ">論文</a>" _site/index.html'
chk 'CV リンク(ja)'   'grep -q ">履歴書</a>" _site/index.html'
chk 'CV リンク(en)'   'grep -q ">CV</a>" _site/en/index.html'
chk '概要 リンクなし'   'test -z "$(grep -o ">概要</a>" _site/index.html)"'

echo "--- 言語ごとに自分の文言が出ているか ---"
chk 'ja lead'  'grep -q "電池も配線もいらない" _site/index.html'
chk 'en lead'  'grep -q "no battery and no wire" _site/en/index.html'
chk 'zh lead'  'grep -q "无需电池与布线" _site/zh/index.html'
chk 'ja role'  'grep -q "特任助教" _site/index.html'
chk 'en role'  'grep -q "Project Assistant Professor" _site/en/index.html'

echo "--- hreflang / canonical ---"
for l in ja en zh; do chk "hreflang=$l" "grep -q 'hreflang=\"$l\"' _site/index.html"; done
chk 'canonical' 'grep -q "rel=\"canonical\"" _site/index.html'

echo "--- 論文一覧（論文62 + メディア24 = 86件）---"
chk 'Meander Coil++' 'grep -q "Meander Coil++" _site/cv/index.html'
chk 'picoRing'       'grep -q "picoRing" _site/cv/index.html'
n=$(grep -oE 'class="entry[" ]' _site/cv/index.html | wc -l | tr -d ' ')
chk "entry >= 86（実測 $n）" "test $n -ge 86"
for k in journal conference media; do
  chk "フィルタ $k" "grep -q 'data-filter=\"$k\"' _site/cv/index.html"
done
g=$(grep -o 'class="group-head"' _site/cv/index.html | wc -l | tr -d ' ')
chk "種別見出し 7つ（実測 $g）" "test $g -eq 7"
chk '著者強調'  "grep -q \"class='me'\" _site/cv/index.html"

echo "--- CV（学歴3+職歴8+研究費7+受賞19+論文86+講演10 = 133）---"
c=$(grep -oE 'class="entry[" ]' _site/cv/index.html | wc -l | tr -d ' ')
chk "entry >= 133（実測 $c）" "test $c -ge 133"
chk 'pub-groups'  'grep -q "id=\"pub-groups\"" _site/cv/index.html'
chk 'media タブ'  'grep -q "data-filter=\"media\"" _site/cv/index.html'
chk '受賞(en)'    'grep -q "Best Paper Award" _site/en/cv/index.html'
chk '研究費 金額' 'grep -q "18,330,000" _site/cv/index.html'
chk '職歴'        'grep -q "Meta Inc" _site/cv/index.html'
chk '役割(ja)'     'grep -q "研究代表者" _site/cv/index.html'
chk '役割(en)'     'grep -q "Principal Investigator" _site/en/cv/index.html'

echo "--- トップは各タブ10件 + 受賞6件 ---"
chk "$(python3 scripts/check_home.py 2>&1 | tail -1)" 'python3 scripts/check_home.py >/dev/null'
chk 'CV への導線' 'grep -q "href=\"/cv/\"" _site/index.html'

echo "--- 未展開の Liquid が残っていないか ---"
chk 'Liquid なし' 'test -z "$(grep -rlE "\{\{|\{%" _site --include="*.html" | grep -v 404)"'

echo "--- 非公開ファイルがコミットされていないか ---"
chk 'xlsx 未追跡'       'test -z "$(git ls-files | grep -E "\.xlsx$")"'
chk 'data_local 未追跡' 'test -z "$(git ls-files | grep -E "^data_local/")"'

echo
if [ $fail = 0 ]; then echo "==> 全部通った"; else echo "==> 失敗あり"; fi
exit $fail
