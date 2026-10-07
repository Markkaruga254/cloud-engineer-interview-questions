#!/usr/bin/env python3
"""Build the interview-question tracker site from README.md.

README.md stays exactly as upstream publishes it. This script reads it,
splits it into tracks and questions, and writes _site/index.html.

    pip install markdown
    python scripts/build.py
"""
import json
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
TEMPLATE = ROOT / "site" / "template.html"
OUT = ROOT / "_site"

# Each track maps to one "## " section of the README.
TRACKS = [
    {
        "id": "fundamentals",
        "heading": "## Cloud Computing Interview Questions",
        "name": "Cloud fundamentals",
        "blurb": "Core concepts, architecture, security and operations.",
        "mode": "h3",
        "color": ["#2f4b9b", "#8da6ff"],
    },
    {
        "id": "aws",
        "heading": "## Amazon Web Services (AWS) Interview Questions",
        "name": "AWS",
        "blurb": "Service-specific questions, each with an answer.",
        "mode": "h3",
        "color": ["#b8650b", "#f0a24a"],
    },
    {
        "id": "azure",
        "heading": "## Microsoft Azure Interview Questions",
        "name": "Azure",
        "blurb": "Mostly questions without answers. Use the notes box to write your own.",
        "mode": "numbered",
        "color": ["#0a6cbf", "#5fb0f5"],
    },
    {
        "id": "gcp",
        "heading": "## Google Cloud Platform (GCP) Interview Questions",
        "name": "GCP",
        "blurb": "Questions only. Use the notes box to write your own answers.",
        "mode": "numbered",
        "color": ["#1e8e5a", "#58d19b"],
    },
    {
        "id": "aws-services",
        "heading": "## List of AWS services with brief description",
        "name": "AWS services",
        "blurb": "Reference list. Check a service once you can say what it does and when to use it.",
        "mode": "services",
        "color": ["#7a4bb0", "#be9af0"],
    },
]

MD_EXT = ["tables", "fenced_code", "sane_lists"]
TOC_LINE = re.compile(r"^\s*\d+\.\s+\[.*\]\(#.*\)\s*$")


def split_sections(lines):
    """Map each '## ' heading line to its body lines."""
    sections, current = {}, None
    for line in lines:
        if line.startswith("## "):
            current = line.strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def render(body_lines):
    text = "\n".join(body_lines).strip()
    return markdown.markdown(text, extensions=MD_EXT) if text else ""


def parse_h3(body):
    """Each '### ' heading is a question. Headings ending in ':' are
    sub-parts of the previous answer, so they stay inside it."""
    items, cur = [], None
    for line in body:
        if TOC_LINE.match(line):
            continue
        if line.startswith("### "):
            title = line[4:].strip()
            if title.endswith(":") and cur is not None:
                cur["body"].append(f"#### {title}")
                continue
            cur = {"title": title, "body": []}
            items.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    return items


def parse_numbered(body):
    """Azure/GCP: '### 1. Question' (with answer) or '4. Question' (bare)."""
    items, cur = [], None
    heading = re.compile(r"^###\s+\d+\.\s+(.*)$")
    plain = re.compile(r"^\d+\.\s+(.*)$")
    for line in body:
        m = heading.match(line) or plain.match(line)
        if m:
            cur = {"title": m.group(1).strip(), "body": []}
            items.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    return items


def parse_services(body):
    """'### Category' followed by '- **Service:** description' bullets."""
    items, group = [], ""
    bullet = re.compile(r"^[-*]\s+\*\*(.+?)\*\*:?\s*(.*)$")
    for line in body:
        if line.startswith("### "):
            group = line[4:].strip()
            continue
        m = bullet.match(line)
        if m:
            name = m.group(1).strip().rstrip(":").strip()
            items.append({"title": name, "body": [m.group(2).strip()], "group": group})
    return items


PARSERS = {"h3": parse_h3, "numbered": parse_numbered, "services": parse_services}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:70]


def build_data():
    sections = split_sections(README.read_text(encoding="utf-8").splitlines())
    tracks = []
    for t in TRACKS:
        if t["heading"] not in sections:
            sys.exit(f"Section not found in README.md: {t['heading']}")
        raw = PARSERS[t["mode"]](sections[t["heading"]])
        seen, items = {}, []
        for it in raw:
            # IDs come from the question text, so progress survives upstream reordering.
            base = f"{t['id']}-{slugify(it['title'])}"
            seen[base] = seen.get(base, 0) + 1
            qid = base if seen[base] == 1 else f"{base}-{seen[base]}"
            md_title = markdown.markdown(it["title"], extensions=MD_EXT)
            title_html = re.sub(r"^<p>|</p>$", "", md_title.strip())
            items.append({
                "id": qid,
                "title": title_html,
                "html": render(it["body"]),
                **({"group": it["group"]} if it.get("group") else {}),
            })
        tracks.append({
            "id": t["id"], "name": t["name"], "blurb": t["blurb"],
            "color": t["color"], "items": items,
        })
    return {"tracks": tracks}


def main():
    data = build_data()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*__DATA__*/null", payload)
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    for t in data["tracks"]:
        print(f"{t['name']:<20} {len(t['items']):>4} items")
    print(f"Wrote {OUT / 'index.html'} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
