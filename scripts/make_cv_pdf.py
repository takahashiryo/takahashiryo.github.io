#!/usr/bin/env python3
"""印刷用の CV ページ（/cv-print/）を PDF にする。

    python3 scripts/make_cv_pdf.py

jekyll build のあとに走らせる前提。GitHub Actions の deploy.yml から呼んでいる。
weasyprint と日本語フォント（fonts-noto-cjk）が要るので、手元の macOS では動かない。
体裁の確認は _site/cv-print/index.html をブラウザで開いて行う。
"""
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "_site"
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
    dst = SITE / out
    HTML(filename=str(s), base_url=str(s.parent)).write_pdf(str(dst))
    print(f"{out}: {dst.stat().st_size // 1024} KB")
