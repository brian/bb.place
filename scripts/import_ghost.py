#!/usr/bin/env python3
import argparse
import json
import pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_EXPORT = ROOT / "bb-place.ghost.2026-02-28-01-37-09.json"


def load_export(path: pathlib.Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw["db"][0]["data"]


def yaml_escape(value: str) -> str:
    return value.replace('"', '\\"')


def clean_html(html: str) -> str:
    out = html or ""
    out = out.replace("__GHOST_URL__", "https://bb.place")
    out = out.replace("#/portal/signup", "")
    out = out.replace('href=""', 'href="/kaleidoscope/"')
    return out


def write_content(path: pathlib.Path, frontmatter: str, html: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter + "\n" + html + "\n", encoding="utf-8")


def build(export_path: pathlib.Path):
    data = load_export(export_path)

    tags = {t["id"]: t for t in data["tags"]}
    users = {u["id"]: u for u in data["users"]}

    post_tags = {}
    for rel in data["posts_tags"]:
        post_tags.setdefault(rel["post_id"], []).append(rel)
    for pid in post_tags:
        post_tags[pid] = sorted(post_tags[pid], key=lambda x: x.get("sort_order", 0))

    post_authors = {}
    for rel in data["posts_authors"]:
        post_authors.setdefault(rel["post_id"], []).append(rel)
    for pid in post_authors:
        post_authors[pid] = sorted(post_authors[pid], key=lambda x: x.get("sort_order", 0))

    for post in data["posts"]:
        if post.get("status") != "published":
            continue

        pid = post["id"]
        rel_tags = post_tags.get(pid, [])
        tag_objs = [tags[r["tag_id"]] for r in rel_tags if r["tag_id"] in tags]

        public_tags = [t["slug"] for t in tag_objs if t.get("visibility") == "public"]
        internal_tags = [t["slug"] for t in tag_objs if t.get("visibility") == "internal"]

        primary_tag = public_tags[0] if public_tags else ""
        include_in_feed = "false" if ("hash-nofeed" in internal_tags or primary_tag == "dispatch") else "true"

        rel_authors = post_authors.get(pid, [])
        author_name = "Brian Bailey"
        if rel_authors:
            author = users.get(rel_authors[0]["author_id"])
            if author and author.get("name"):
                author_name = author["name"]

        title = post.get("title", "Untitled")
        slug = post["slug"]
        published_at = post.get("published_at") or post.get("created_at")
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

        html = clean_html(post.get("html") or "")

        type_name = post.get("type")
        layout = ""
        if type_name == "page":
            if slug == "about":
                layout = "about"
            elif slug == "archive":
                layout = "archive"
            elif slug == "dispatch":
                layout = "dispatch"
            elif slug in {"uncommon", "story", "community", "site", "art", "end", "credits", "love", "unfinished"}:
                layout = "uncommon"
            else:
                layout = "single"

        fm_lines = [
            "---",
            f"title: \"{yaml_escape(title)}\"",
            f"slug: \"{slug}\"",
            f"date: {dt.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "draft: false",
            f"type: \"{'post' if type_name == 'post' else 'page'}\"",
        ]

        if type_name == "post":
            fm_lines.append("tags:")
            for t in public_tags:
                fm_lines.append(f"  - \"{t}\"")
            fm_lines.append("internal_topics:")
            for t in internal_tags:
                fm_lines.append(f"  - \"{t}\"")
            fm_lines.append(f"primary_tag: \"{primary_tag}\"")
            fm_lines.append(f"include_in_feed: {include_in_feed}")
            fm_lines.append(f"author_name: \"{yaml_escape(author_name)}\"")
            if post.get("feature_image"):
                fm_lines.append(f"feature_image: \"{post['feature_image'].replace('__GHOST_URL__', 'https://bb.place')}\"")
        else:
            fm_lines.append(f"layout: \"{layout}\"")

        fm_lines.extend(["---", ""])
        frontmatter = "\n".join(fm_lines)

        if type_name == "post":
            dest = ROOT / "content" / "posts" / slug / "index.md"
        else:
            dest = ROOT / "content" / slug / "index.md"

        write_content(dest, frontmatter, html)

    # Ensure /rss/ is generated as a section endpoint with XML output
    rss_index = ROOT / "content" / "rss" / "_index.md"
    if not rss_index.exists():
        rss_index.parent.mkdir(parents=True, exist_ok=True)
        rss_index.write_text("---\ntitle: RSS\nlayout: rss\nbuild:\n  render: always\noutputs:\n  - RSS\n---\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Ghost JSON export into Hugo content")
    parser.add_argument(
        "--export",
        type=pathlib.Path,
        default=DEFAULT_EXPORT,
        help="Path to Ghost export JSON",
    )
    args = parser.parse_args()
    build(args.export)
