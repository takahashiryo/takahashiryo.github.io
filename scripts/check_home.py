"""トップページの Publications と Awards の件数を確かめる。

トップは種別ごとに「新しい順 limit 件」の組を並べておき、タブで組を入れ替える
作りになっている（_includes/pub_list.html の limit > 0 の側）。組の数と、
初期表示になる All の件数、それに受賞の件数を見る。

CI（.github/workflows/deploy.yml）と scripts/verify_site.sh の両方から呼ぶ。
"""
import pathlib
import re
import sys

LIMIT = 10        # _config.yml の home_pub_limit
AWARDS = 6        # 同 home_award_limit
SETS = 7          # All + 種別6つ

ENTRY = r'class="entry[ "]'


def main(path="_site/index.html"):
    h = pathlib.Path(path).read_text()

    # data-set ごとの組に割って、次の <section> が来るまでを1組として数える
    parts = re.split(r'<div class="pub-list[^"]*" data-set="([^"]+)"', h)[1:]
    sets = [(name, len(re.findall(ENTRY, body.split("<section", 1)[0])))
            for name, body in zip(parts[0::2], parts[1::2])]

    awards_html = h.split('id="awards"', 1)[1].split("</section>", 1)[0]
    awards = len(re.findall(ENTRY, awards_html))

    print(f"home sets: {sets}  awards: {awards}")

    bad = []
    if len(sets) != SETS:
        bad.append(f"タブの組が {SETS} つでない: {len(sets)}")
    if not sets or sets[0] != ("all", LIMIT):
        bad.append(f"All が {LIMIT} 件でない: {sets[:1]}")
    if any(n < 1 or n > LIMIT for _, n in sets):
        bad.append(f"組の件数が 1..{LIMIT} の外: {sets}")
    if awards != AWARDS:
        bad.append(f"受賞が {AWARDS} 件でない: {awards}")
    if bad:
        sys.exit("\n".join(bad))


if __name__ == "__main__":
    main(*sys.argv[1:])
