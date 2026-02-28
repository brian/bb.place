# bb.place static site (Hugo)

This repository is a Hugo migration of `bb.place` from Ghost.

## Local development

1. Install Hugo extended.
2. Run:

```bash
python3 scripts/import_ghost.py
hugo server -D
```

## Build

```bash
python3 scripts/import_ghost.py
hugo --minify
```

## Content model

- Posts are generated under `content/posts/<slug>/index.md`.
- Pages are generated under `content/<slug>/index.md`.
- Front matter fields include:
  - `title`, `slug`, `date`, `draft`, `type`
  - `tags`, `primary_tag`, `internal_topics`, `include_in_feed`
  - `layout` for special page templates

## Publishing workflow

- Write/edit Markdown in `content/`.
- Commit to `main`.
- GitHub Actions builds and deploys to GitHub Pages.

## Notes

- Membership/sign-in portal behavior from Ghost is removed.
- Kaleidoscope remains as content pages.
- RSS is emitted from `/rss/index.xml`.
