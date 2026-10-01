# Writing

A static blog — plain markdown, one Python build script, zero JavaScript.
Modeled on [ryanrusnak.com](https://ryanrusnak.com/).

## Structure

    content/     markdown posts — the only thing you edit
    build.py     static site generator (uv run build.py)
    style.css    the entire design
    public/      generated output — deploy this folder

## Write a post

Create `content/<my-slug>.md`:

    ---
    title: My Post Title
    date: 2026-10-01
    category: essay        # essay | notes | talk
    tags: [linux, ai]
    description: One-line summary shown on the home page.
    ---

    Body in markdown...

Then build and preview:

    uv run build.py
    python -m http.server 8000 -d public

Open http://localhost:8000.

## Deploy (GitHub Pages)

    git init && git add -A && git commit -m "init"
    # create a repo named <you>.github.com on GitHub, then:
    git remote add origin git@github.com:<you>/<you>.github.com.git
    git push -u origin main

Settings → Pages → deploy from branch. For a rebuild-on-push workflow, add a
GitHub Action running `uv run build.py` and publishing `public/` (or use
Netlify/Cloudflare Pages: build command `uv run build.py`, output `public`).

## Design notes

- Fonts: system serif stack + monospace for metadata
- Colors: `--fg` / `--bg` / `--muted` / `--accent` in `:root` of style.css
- Dark mode: automatic via `prefers-color-scheme`
- Reading time: word count / 200 wpm, computed in build.py
