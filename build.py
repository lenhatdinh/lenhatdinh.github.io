#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown"]
# ///
"""Static blog generator.

Reads markdown files from content/, writes HTML to public/.
Run:  uv run build.py        (or: python3 build.py if markdown is installed)
"""

import itertools
import re
import shutil
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"

# ---------------------------------------------------------------------------
# Frontmatter: the key: value block between --- lines at the top of a post
# ---------------------------------------------------------------------------
def parse_post(path: Path) -> dict:
    text = path.read_text()
    meta, body = {}, text

    if text.startswith("---"):
        front, _, body = text[3:].partition("---")
        for line in front.strip().splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()

    html = markdown.markdown(body, extensions=["extra", "codehilite", "toc"])

    words = len(re.sub(r"<[^>]+>", " ", html).split())
    minutes = max(1, round(words / 200))  # avg reading speed ~200 wpm

    return {
        "slug": path.stem,  # filename without .md
        "title": meta.get("title", path.stem),
        "date": date.fromisoformat(meta["date"]),
        "category": meta.get("category", "notes"),
        "tags": [t.strip() for t in meta.get("tags", "[]").strip("[]").split(",") if t.strip()],
        "description": meta.get("description", ""),
        "minutes": minutes,
        "html": html,
    }


# ---------------------------------------------------------------------------
# Templates — plain f-strings. Tweak these to change the design.
# ---------------------------------------------------------------------------
def layout(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<main>{body}</main>
</body>
</html>"""


def post_page(post: dict, prev_post: dict | None, next_post: dict | None) -> str:
    prev = ""
    if prev_post:
        prev = f'<a class="nav" href="/{prev_post["slug"]}/">← previous&nbsp;&nbsp;{prev_post["title"]}</a>'
    nxt = ""
    if next_post:
        nxt = f'<a class="nav next" href="/{next_post["slug"]}/">{next_post["title"]}&nbsp;&nbsp;next →</a>'
    tags = " ".join(f'<span class="tag">#{t}</span>' for t in post["tags"])
    body = f"""<div class="post">
<p class="crumbs"><a href="/">[~/writing](/)</a>/{post["date"].year}/ {post["slug"]}.md</p>
<p class="meta">{post["date"].isoformat()} {post["category"]} {post["minutes"]} min {tags}</p>
<h1>{post["title"]}</h1>
{post["html"]}
</div>
<div class="postnav">{prev}{nxt}</div>"""
    return layout(post["title"], body)


def home_page(posts: list[dict]) -> str:
    sections = []
    for year, group in group_by_year(posts):
        items = "\n".join(
            f"""<article>
<p class="meta">{p["date"].isoformat()} {p["category"]} {p["minutes"]} min</p>
<h2><a href="/{p["slug"]}/">{p["title"]}</a></h2>
<p class="desc">{p["description"]}</p>
</article>"""
            for p in group
        )
        n = len(group)
        sections.append(f'<section><h1 class="year">{year} {n} {"post" if n == 1 else "posts"}</h1>{items}</section>')
    return layout("Writing", "\n".join(sections))


def group_by_year(posts: list[dict]):
    """Yield (year, posts) newest-first. Posts must already be date-sorted."""
    for year, group in itertools.groupby(posts, key=lambda p: p["date"].year):
        yield year, list(group)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir()
    shutil.copy(ROOT / "style.css", PUBLIC / "style.css")

    posts = sorted((parse_post(p) for p in CONTENT.glob("*.md")),
                   key=lambda p: p["date"], reverse=True)

    for i, post in enumerate(posts):
        prev = posts[i + 1] if i + 1 < len(posts) else None  # older
        nxt = posts[i - 1] if i > 0 else None                # newer
        page = post_page(post, prev, nxt)
        out = PUBLIC / post["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page)

    (PUBLIC / "index.html").write_text(home_page(posts))

    print(f"Built {len(posts)} posts → {PUBLIC}/")


if __name__ == "__main__":
    build()
