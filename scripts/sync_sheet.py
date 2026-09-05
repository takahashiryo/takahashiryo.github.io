#!/usr/bin/env python3
"""Google スプレッドシートから publications / awards / talks の CSV を取り込む。

使い方:
    SHEET_ID=<スプレッドシートのID> python3 scripts/sync_sheet.py

前提:
  * スプレッドシートの共有設定は「編集: 自分のみ」＋「リンクを知っている全員: 閲覧者」。
    閲覧まで止めると gviz が HTML のエラーページを返し、CSV が壊れる（CRONOS で実際に事故あり）。
  * シート名は Publications / Awards / Talks。列は data_local の xlsx と同じ。
取得したデータが CSV でなければ、既存ファイルを残したまま異常終了する。
"""
import os, sys, urllib.request, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # build_cv を読むため

SHEET_ID = os.environ.get("SHEET_ID", "").strip()
OUT = Path(__file__).resolve().parent.parent / "_data"
SHEETS = {"Publications": "publications.csv",
          "Awards": "awards.csv",
          "Talks": "talks.csv"}
EXPECTED_HEAD = {"publications.csv": "year", "awards.csv": "year", "talks.csv": "year"}


def fetch(sheet: str) -> str:
    url = ("https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:csv&sheet=%s"
           % (SHEET_ID, urllib.parse.quote(sheet)))
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    if not SHEET_ID:
        print("ERROR: 環境変数 SHEET_ID が未設定", file=sys.stderr)
        return 2
    for sheet, fname in SHEETS.items():
        try:
            text = fetch(sheet).replace("\r\n", "\n")
        except Exception as e:                      # noqa: BLE001
            print(f"ERROR: {sheet} の取得に失敗: {e}", file=sys.stderr)
            return 1
        head = text.split("\n", 1)[0].lstrip('"').lower()
        if not head.startswith(EXPECTED_HEAD[fname]):
            print(f"ERROR: {sheet} が CSV ではない（共有設定を確認）。先頭: {head[:60]!r}",
                  file=sys.stderr)
            return 1
        (OUT / fname).write_text(text, encoding="utf-8")
        print(f"{fname}: {len(text.splitlines()) - 1} 件")

    # シートは sortkey 列を持たない（持たせると手で保守することになる）。
    # 取り込んだあとに YYYYMMDD で計算し直し、並べ替えまでやる。
    # これをしないと publications.csv から sortkey が消え、
    # サイト側の sort: "sortkey" が効かなくなる。
    from build_cv import add_sortkey
    for fname in ("publications.csv", "talks.csv"):
        add_sortkey(fname)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
