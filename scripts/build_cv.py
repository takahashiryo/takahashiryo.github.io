#!/usr/bin/env python3
"""researchmap の公開 API から CV 用データ（学歴・職歴・研究費・メディア掲載）を作る。

    python3 scripts/build_cv.py [researchmap-json-dir]

引数を省略すると API から直接取得する。出力は _data/ 以下の CSV。
メディア掲載は publications.csv と同じ列にそろえてあるので、論文一覧にそのまま混ぜられる。
"""
import csv, json, re, sys, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "_data"
PERMALINK = "takahashi_ryo"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def load(endpoint: str) -> list:
    if SRC and (SRC / f"rm_{endpoint}.json").exists():
        data = json.loads((SRC / f"rm_{endpoint}.json").read_text())
    else:
        url = f"https://api.researchmap.jp/{PERMALINK}/{endpoint}"
        with urllib.request.urlopen(url, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
    return data.get("items", [])


def pick(d, lang, other=None):
    """{'ja': ..., 'en': ...} から言語を選ぶ。無ければもう一方で埋める。"""
    if not isinstance(d, dict):
        return str(d or "")
    v = d.get(lang) or (d.get(other) if other else "") or ""
    return str(v).strip()


def ym(s):
    s = (s or "")[:7]
    m = re.match(r"(\d{4})-(\d{2})", s)
    return (m.group(1), m.group(2)) if m else ((s[:4] if s[:4].isdigit() else ""), "")


def write(name, cols, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} 件")


def build_education():
    rows = []
    for e in load("education"):
        fy, fm = ym(e.get("from_date")); ty, tm = ym(e.get("to_date"))
        rows.append({
            "from": f"{fy}.{fm}" if fm else fy, "to": f"{ty}.{tm}" if tm else ty,
            "sortkey": f"{fy}{fm}",
            "affiliation_ja": pick(e.get("affiliation"), "ja", "en"),
            "affiliation_en": pick(e.get("affiliation"), "en", "ja"),
            "department_ja": pick(e.get("department"), "ja", "en"),
            "department_en": pick(e.get("department"), "en", "ja"),
            "course_ja": pick(e.get("course"), "ja", "en"),
            "course_en": pick(e.get("course"), "en", "ja"),
        })
    rows.sort(key=lambda r: r["sortkey"], reverse=True)
    write("education.csv", list(rows[0].keys()), rows)


def build_experience():
    rows = []
    for e in load("research_experience"):
        fy, fm = ym(e.get("from_date")); ty, tm = ym(e.get("to_date"))
        rows.append({
            "from": f"{fy}.{fm}" if fm else fy, "to": f"{ty}.{tm}" if tm else ty,
            "sortkey": f"{fy}{fm}",
            "affiliation_ja": pick(e.get("affiliation"), "ja", "en"),
            "affiliation_en": pick(e.get("affiliation"), "en", "ja"),
            "job_ja": pick(e.get("job"), "ja", "en"),
            "job_en": pick(e.get("job"), "en", "ja"),
        })
    rows.sort(key=lambda r: r["sortkey"], reverse=True)
    write("experience.csv", list(rows[0].keys()), rows)


ROLE = {"principal_investigator": ("研究代表者", "Principal Investigator"),
        "coinvestigator": ("研究分担者", "Co-Investigator")}


def build_grants():
    rows = []
    for g in load("research_projects"):
        fy, fm = ym(g.get("from_date")); ty, tm = ym(g.get("to_date"))
        amt = (g.get("overall_grant_amount") or {}).get("total_cost") or ""
        amt_disp_ja = amt_disp_en = ""
        if amt.isdigit():
            amt_disp_ja = f"{int(amt):,} 円"
            amt_disp_en = f"JPY {int(amt):,}"
        role = g.get("research_project_owner_role") or ""
        if not role:
            # 役割が未入力でも、研究者が本人ひとりなら代表者とみなす
            inv = (g.get("investigators") or {}).get("ja") or []
            role = "principal_investigator" if len(inv) == 1 else ""
        url = ""
        for s in (g.get("see_also") or []):
            if "researchmap.jp" not in s.get("@id", ""):
                url = s["@id"]; break
        rows.append({
            "from": f"{fy}.{fm}" if fm else fy, "to": f"{ty}.{tm}" if tm else ty,
            "sortkey": f"{fy}{fm}",
            "title_ja": pick(g.get("research_project_title"), "ja", "en"),
            "title_en": pick(g.get("research_project_title"), "en", "ja"),
            "funder_ja": pick(g.get("offer_organization"), "ja", "en"),
            "funder_en": pick(g.get("offer_organization"), "en", "ja"),
            "system": " ".join(x for x in [pick(g.get("system_name"), "ja", "en"),
                                           pick(g.get("category"), "ja", "en")] if x),
            "role_ja": ROLE.get(role, ("", ""))[0],
            "role_en": ROLE.get(role, ("", ""))[1],
            "amount_ja": amt_disp_ja, "amount_en": amt_disp_en,
            "number": ", ".join((g.get("identifiers") or {}).get("grant_number") or []),
            "url": url,
        })
    rows.sort(key=lambda r: r["sortkey"], reverse=True)
    write("grants.csv", list(rows[0].keys()), rows)


PUB_COLS = ["year", "month", "type", "authors", "title", "venue", "detail",
            "place", "award", "url", "doi", "note", "reviewed", "sortkey"]


def build_media():
    rows = []
    for m in load("media_coverage"):
        y, mo = ym(m.get("publication_date"))
        outlet = (pick(m.get("publisher"), "ja", "en") or pick(m.get("event"), "ja", "en")
                  or pick(m.get("location"), "ja", "en"))
        loc = pick(m.get("location"), "ja", "en")
        url = loc if loc.startswith("http") else ""
        if outlet.startswith("http"):
            outlet = ""
        rows.append({
            "year": y, "month": mo, "type": "media", "authors": "",
            "title": pick(m.get("media_coverage_title"), "ja", "en"),
            "venue": outlet, "detail": "", "place": "", "award": "",
            "url": url, "doi": "", "note": "", "reviewed": "no",
            "sortkey": f"{y}{mo}",
        })
    rows.sort(key=lambda r: (r["sortkey"], r["title"]), reverse=True)
    write("media.csv", PUB_COLS, rows)


def add_sortkey(name):
    """既存の publications.csv / talks.csv に sortkey 列を足して並べ替える。"""
    path = OUT / name
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        r["sortkey"] = f"{r['year']}{r['month']}"
    rows.sort(key=lambda r: (r["sortkey"], r["title"]), reverse=True)
    write(name, PUB_COLS, rows)


if __name__ == "__main__":
    build_education()
    build_experience()
    build_grants()
    build_media()
    add_sortkey("publications.csv")
    add_sortkey("talks.csv")
