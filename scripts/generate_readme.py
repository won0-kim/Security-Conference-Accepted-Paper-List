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
            if "paper_list" in y:
                paper_map[y["year"]] = y["paper_list"]

        cells = []
        for yr in cols:
            if yr in paper_map:
                cells.append(f"[🔗]({paper_map[yr]})")
            else:
                cells.append("")
        row = f"| [{conf['name']}](#{conf['anchor']}) | " + " | ".join(cells) + " |"
        lines.append(row)

    return "\n".join(lines)


def build_conference_table(conf):
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
        cycles = y.get("cycles", [])
        for i, cycle in enumerate(cycles):
            is_first = i == 0
            cycle_name = cycle.get("name", "")
            if cycle_name:
                year_label = f"{y['year']} ({cycle_name})"
            else:
                year_label = str(y["year"])

            if is_first:
                website = f"[🏠 website]({y['website']})" if "website" in y else ""
                paper_list = (
                    f"[🔗 link]({y['paper_list']})" if "paper_list" in y else ""
                )
                conf_date = y.get("conference_date", "")
                location = y.get("location", "")
            else:
                website = ""
                paper_list = ""
                conf_date = ""
                location = ""

            deadline = cycle.get("deadline", "")
            notification = cycle.get("notification", "")

            lines.append(
                f"| {year_label}| {website}| {paper_list}"
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
