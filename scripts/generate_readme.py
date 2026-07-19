#!/usr/bin/env python3
"""Generate README.md from data/conferences.yml."""

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "conferences.yml"
README_FILE = ROOT / "README.md"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def paper_links(y):
    """Normalize a year's paper_list into a list of {label, url} dicts.

    Accepts either a single URL string (label defaults to "link") or a list
    of {label, url} entries, so a year can expose several known lists at once
    (e.g. USENIX "Cycle 1" and "Session")."""
    pl = y.get("paper_list")
    if not pl:
        return []
    if isinstance(pl, str):
        return [{"label": "link", "url": pl}]
    return pl


def primary_paper_url(y):
    """URL used for the single Quick Links icon: the last (most complete) list."""
    links = paper_links(y)
    return links[-1]["url"] if links else None


def build_quick_links(conferences):
    all_years = sorted(
        {y["year"] for c in conferences for y in c["years"]}, reverse=True
    )
    cols = all_years[:6]

    lines = []
    header = "| Conference | " + " | ".join(str(y) for y in cols) + " |"
    sep = "| ---------- | " + " | ".join("----" for _ in cols) + " |"
    lines.append(header)
    lines.append(sep)

    for conf in conferences:
        paper_map = {}
        for y in conf["years"]:
            url = primary_paper_url(y)
            if url:
                paper_map[y["year"]] = url

        cells = []
        for yr in cols:
            if yr in paper_map:
                cells.append(f"[🔗]({paper_map[yr]})")
            else:
                cells.append("")
        row = f"| [{conf['name']}](#{conf['anchor']}) | " + " | ".join(cells) + " |"
        lines.append(row)

    return "\n".join(lines)


def _cycle_dates(cycles, key):
    """Join a year's cycle values for one field (deadline/notification) into a
    single cell, one line per cycle, prefixed with the cycle name. Cycles with
    an empty value are skipped."""
    parts = []
    for c in cycles:
        val = c.get(key, "")
        if not val:
            continue
        name = c.get("name", "")
        parts.append(f"{name}: {val}" if name else f"{val}")
    return "<br>".join(parts)


def build_conference_table(conf):
    # One row per year. Submission cycles differ only in their schedule, so the
    # per-cycle deadlines/notifications are stacked inside the Deadline and
    # Notification cells instead of spawning a separate row per cycle.
    lines = []

    # Header
    lines.append(f"## {conf['name']}")
    if "collection_url" in conf:
        lines.append(f"[Official Collection]({conf['collection_url']})")

    lines.append(
        "| Year | Official Website | Paper List "
        "| Deadline | Notification | Conference | Location |"
    )
    lines.append(
        "| ---- | ---------------- | ---------- "
        "| -------- | ------------ | ---------- | -------- |"
    )

    for y in conf["years"]:
        website = f"[🏠 website]({y['website']})" if "website" in y else ""
        paper_list = "<br>".join(
            f"[🔗 {link['label']}]({link['url']})" for link in paper_links(y)
        )
        cycles = y.get("cycles", []) or [{}]
        deadline = _cycle_dates(cycles, "deadline")
        notification = _cycle_dates(cycles, "notification")
        conf_date = y.get("conference_date", "")
        location = y.get("location", "")

        lines.append(
            f"| {y['year']}| {website}| {paper_list}"
            f"| {deadline}| {notification}| {conf_date}| {location}|"
        )

    return "\n".join(lines)


def generate_readme(data):
    conferences = data["conferences"]

    catalogue_links = " :sparkles: ".join(
        f"[{c['name']}](#{c['anchor']})" for c in conferences
    )

    sections = []

    # Title
    sections.append("# Security-Conference-Accepted-Paper-List\n")
    sections.append(
        "Accepted paper lists for top-4 security conferences "
        "(S&P, USENIX Security, CCS, NDSS).\n"
    )
    sections.append(
        "> **CATALOGUE**\n>\n"
        f"> [Quick Links](#quick-links) :sparkles: {catalogue_links}\n"
    )

    # Quick Links
    sections.append("## Quick Links")
    sections.append(build_quick_links(conferences))
    sections.append("")

    # Each conference
    for conf in conferences:
        sections.append("")
        sections.append(build_conference_table(conf))
        sections.append("")

    # Acknowledge
    sections.append("")
    sections.append("## Acknowledge")
    sections.append(
        "This project is built upon the excellent work of "
        "[Conference-Accepted-Paper-List](https://github.com/Lionelsy/Conference-Accepted-Paper-List)."
    )

    readme = "\n".join(sections).rstrip() + "\n"

    # Collapse multiple blank lines
    while "\n\n\n" in readme:
        readme = readme.replace("\n\n\n", "\n\n")

    return readme


def main():
    data = load_data()
    readme = generate_readme(data)
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"Generated {README_FILE}")


if __name__ == "__main__":
    main()
