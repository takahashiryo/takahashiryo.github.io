#!/usr/bin/env python3
"""publications.csv から _data/bibtex.yml（タイトル→BibTeX）を作る。

- doi 列（無ければ url の doi.org / dl.acm.org/doi/ 部分、無ければ _data/doi.yml）があれば
  Crossref（doi.org のコンテンツネゴシエーション）から BibTeX を取得する。
- 取れない行は CSV の著者・題名・掲載先・年月から生成する。
- 既に bibtex.yml にある題名は再取得しない（--refresh で全件取り直し）。
"""
import csv, re, sys, time, urllib.request, urllib.error
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "_data/publications.csv"
OUT = ROOT / "_data/bibtex.yml"
DOI_YML = ROOT / "_data/doi.yml"
REFRESH = "--refresh" in sys.argv

TYPE_MAP = {"journal": "article", "conference": "inproceedings", "workshop": "inproceedings",
            "demo": "inproceedings", "poster": "inproceedings", "domestic": "inproceedings", "article": "article"}
MONTHS = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]

def find_doi(r, doi_map):
    d = (r.get("doi") or "").strip()
    if d: return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    u = r.get("url") or ""
    m = re.search(r"doi\.org/(10\.[^\s\"]+)", u) or re.search(r"dl\.acm\.org/doi/(?:abs/)?(10\.[^\s\"?]+)", u)
    if m: return m.group(1)
    return (doi_map.get(r["title"]) or "").strip() or None

def fetch_bibtex(doi):
    req = urllib.request.Request(f"https://doi.org/{doi}", headers={"Accept": "application/x-bibtex", "User-Agent": "my_web build_bibtex (mailto:takahashi@akg.t.u-tokyo.ac.jp)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception as e:
        print(f"  ! {doi}: {e}", file=sys.stderr); return None

def pretty(bib):
    """Crossref の 1 行 BibTeX を 1 フィールド 1 行に整形する。"""
    bib = bib.strip()
    m = re.match(r"(@\w+\{[^,]+,)\s*(.*)\}\s*$", bib, re.S)
    if not m: return bib
    head, body = m.group(1), m.group(2).strip().rstrip(",")
    fields = re.split(r",\s+(?=[A-Za-z_]+=)", body)
    return head + "\n" + ",\n".join("  " + f.strip() for f in fields) + "\n}"

def clean_authors(a):
    a = re.sub(r"[*†]", "", a)
    if "," in a and " " not in a.split(",")[0].strip():   # 日本語著者（カンマ区切り、空白なし）
        parts = [p.strip() for p in a.split(",") if p.strip()]
    else:
        a = re.sub(r",?\s+and\s+", ", ", a)
        parts = [p.strip() for p in a.split(",") if p.strip()]
    return " and ".join(parts)

def surname(a):
    first = re.sub(r"[*†]", "", a).split(",")[0].strip()
    first = re.sub(r"\s+and\s+.*", "", first)
    if re.search(r"[぀-ヿ㐀-鿿]", first): return re.sub(r"\W", "", first)[:2] or "anon"
    return re.sub(r"[^A-Za-z]", "", first.split()[-1]).lower() or "anon"

def compose(r):
    kind = TYPE_MAP.get(r["type"], "misc")
    key = f"{surname(r['authors'])}{r['year']}{re.sub(r'[^a-z]', '', r['title'].lower().split()[0]) or 'x'}"
    fields = [("title", r["title"]), ("author", clean_authors(r["authors"]))]
    venue = r["venue"]
    if kind == "article": fields.append(("journal", venue))
    else: fields.append(("booktitle", venue))
    if r.get("detail"): fields.append(("note" if kind == "article" and not re.search(r"vol|pp|no\.", r["detail"], re.I) else ("pages" if re.match(r"^\s*pp?\.", r["detail"]) else "note"), r["detail"]))
    if r.get("place"): fields.append(("address", r["place"]))
    fields.append(("year", r["year"]))
    m = r.get("month") or ""
    if m.isdigit() and 1 <= int(m) <= 12: fields.append(("month", MONTHS[int(m)-1]))
    body = ",\n".join(f"  {k} = {{{v}}}" if k != "month" else f"  {k} = {v}" for k, v in fields)
    return f"@{kind}{{{key},\n{body}\n}}"

def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    doi_map = yaml.safe_load(open(DOI_YML, encoding="utf-8")) or {} if DOI_YML.exists() else {}
    out = {} if REFRESH or not OUT.exists() else (yaml.safe_load(open(OUT, encoding="utf-8")) or {})
    n_fetch = n_comp = 0
    for r in rows:
        t = r["title"]
        if t in out and not REFRESH: continue
        doi = find_doi(r, doi_map)
        bib = fetch_bibtex(doi) if doi else None
        if bib and bib.startswith("@"):
            bib = pretty(bib); n_fetch += 1; time.sleep(0.3)
        else:
            bib = compose(r); n_comp += 1
        out[t] = bib
    order = [r["title"] for r in rows]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# 論文タイトル → BibTeX。scripts/build_bibtex.py が publications.csv から作る（手で直してよい。再実行時は既存の題名を上書きしない）。\n")
        yaml.safe_dump({t: out[t] for t in order if t in out}, f, allow_unicode=True, sort_keys=False, default_style="|", width=1000)
    print(f"fetched {n_fetch}, composed {n_comp}, total {len(out)}")

if __name__ == "__main__":
    main()
