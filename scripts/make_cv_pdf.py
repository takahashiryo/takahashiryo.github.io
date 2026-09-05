#!/usr/bin/env python3
"""印刷用の CV ページ（/cv-print/）を PDF にしてリポジトリ直下に置く。

    bundle exec jekyll build && python3 scripts/make_cv_pdf.py

出力は cv.pdf（英語）と cv-ja.pdf（日本語）。リポジトリ直下に置くのは、
Jekyll が直下のファイルを _site にそのまま写すため。これをコミットしておけば
GitHub Pages でも Cloudflare Pages でも同じものが配信される
（Cloudflare は Actions ではなく自前で jekyll build するので、
  Actions の中だけで作った PDF はあちらに乗らない）。

weasyprint と日本語フォント（fonts-noto-cjk）が要るので手元の macOS では動かない。
生成は .github/workflows/cv-pdf.yml が行う。体裁の確認は
_site/cv-print/index.html をブラウザで開いて行う。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
JOBS = [
    ("en/cv-print/index.html", "cv.pdf"),      # 既定は英語
    ("cv-print/index.html", "cv-ja.pdf"),
]

try:
    from weasyprint import HTML
except ImportError:
    sys.exit("weasyprint が入っていない。pip install weasyprint")

for src, out in JOBS:
    s = SITE / src
    if not s.exists():
        sys.exit(f"{s} が無い。先に jekyll build を実行すること")
    dst = ROOT / out
    HTML(filename=str(s), base_url=str(s.parent)).write_pdf(str(dst))
    print(f"{out}: {dst.stat().st_size // 1024} KB")
