#!/usr/bin/env python3
"""Assemble the Kineton Academy wiki from authored articles + the MIL* trees.

Sources:
  wiki/articles/<mod>/<topic>/index.md   hand-authored articles (the real content)
  MIL1..MIL4/                            source files (PDFs, dbc/cdd, transcripts)
  Files/cards_export.json                glossary cards
  Files/VideoLinks.txt, MIL2_Links.txt   external links

For every directory in MIL1..MIL4 the script:
  - copies the matching article (if one exists) to wiki/docs/, along with any
    image assets stored next to the article
  - appends auto-generated "Source material" (PDF links) and "Downloads"
    sections, so every article stays linked to its original files
  - generates a fallback page (references only) for directories without an
    article yet

It also generates module curriculum pages, the home page, glossary, resources
page, asset symlinks (docs/assets/mil<N> -> MIL<N>) and wiki/mkdocs.yml.

Run from the project root:
  wiki-venv/bin/python wiki/build_wiki.py             # build everything
  wiki-venv/bin/python wiki/build_wiki.py --manifest  # only write the source
                                                      # manifest used by authors
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
DOCS = WIKI / "docs"
ARTICLES = WIKI / "articles"
MODULES = ["MIL1", "MIL2", "MIL3", "MIL4"]

TRANSCRIPT_EXTS = {".txt"}
ATTACH_EXTS = {
    ".dbc", ".cdd", ".zip", ".png", ".doc", ".html", ".json",
    ".srt", ".vtt", ".tsv", ".ps1",
}
SKIP_FILES = {"cards_export.json"}
SKIP_EXTS = {".mp3", ".docx"}

MODULE_TITLES = {
    "MIL1": "Vehicle Fundamentals",
    "MIL2": "Tools & Testing Basics",
    "MIL3": "Requirements, HIL & Calibration",
    "MIL4": "Verification & Validation",
}
MODULE_BLURBS = {
    "MIL1": "Core vehicle knowledge every E/E engineer needs: in-vehicle networks "
            "(CAN, LIN, Ethernet), EE architecture, electric machines, HEV/BEV "
            "architectures, combustion engines, sensors, the V-model and the main "
            "vehicle subsystems.",
    "MIL2": "Hands-on tooling: analyzing bus traffic with CANalyzer, scripting in "
            "CAPL, system-level simulation in CANoe, UDS diagnostics, RDI testing, "
            "the diagnostic tool landscape, and test automation.",
    "MIL3": "The engineering process: writing and managing requirements, functional "
            "(VF) specifications, test case design, using HIL rigs, and "
            "measurement/calibration with INCA & MDA.",
    "MIL4": "Closing the V-model: verification and validation in practice, the "
            "diagnosis process, structured troubleshooting and first-level analysis.",
}


def pretty(name: str) -> str:
    s = Path(name).stem if "." in name else name
    s = s.replace("___", " - ").replace("__", " ").replace("_", " ")
    s = re.sub(r"^\d+\s*", "", s)
    s = re.sub(r"\s+", " ", s).strip(" -")
    return s or name


def slugify(name: str, used: set) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", pretty(name).lower()).strip("-") or "page"
    cand, i = base, 2
    while cand in used:
        cand = f"{base}-{i}"
        i += 1
    used.add(cand)
    return cand


def fmt_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


def classify(files):
    """Split a directory's files into (pdfs, transcripts, attachments)."""
    pdfs, transcripts, attachments = [], [], []
    for f in sorted(files):
        ext = f.suffix.lower()
        if f.name in SKIP_FILES or ext in SKIP_EXTS:
            continue
        if ext == ".pdf":
            pdfs.append(f)
        elif ext in TRANSCRIPT_EXTS and f.name not in {"VideoLinks.txt", "MIL2_Links.txt"}:
            transcripts.append(f)
        elif ext in ATTACH_EXTS:
            attachments.append(f)
    return pdfs, transcripts, attachments


# ------------------------------------------------------------- auto sections

def references_md(pdfs, transcripts, attachments, rel_to_root, mod_slug, mod) -> str:
    """Auto-generated source/download links for one directory."""
    asset = lambda p: f"{rel_to_root}/assets/{mod_slug}/{p.relative_to(ROOT / mod).as_posix()}"
    lines = []
    if pdfs:
        lines += ["---", "", "## Source material", "",
                  "This article was distilled from the academy lesson materials:"]
        lines.append("")
        for p in pdfs:
            lines.append(f"- :material-file-pdf-box: [{pretty(p.name)}]({asset(p)})"
                         f" — PDF, {fmt_size(p.stat().st_size)}")
        lines.append("")
    downloads = [(a, pretty(a.name)) for a in attachments] + [
        (t, f"{pretty(t.name)} (lecture transcript)") for t in transcripts
    ]
    if downloads:
        lines += ["## Downloads", ""]
        for f, label in downloads:
            lines.append(f"- :material-file: [{label}]({asset(f)}) — {fmt_size(f.stat().st_size)}")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------ tree walk

def walk_module(mod):
    """Yield (dir_path, slug_rel_path) for the module root and every subdir.

    slug_rel_path is relative to docs/<modslug>/, with each level slugified
    (unique per parent) — the same path the article must live at.
    """
    mod_dir = ROOT / mod
    mod_slug = slugify(mod, set())
    yield mod_dir, mod_slug, Path()

    def recurse(dir_path, slug_rel):
        used: set = set()
        for sub in sorted(p for p in dir_path.iterdir() if p.is_dir()):
            s = slugify(sub.name, used)
            yield sub, mod_slug, slug_rel / s
            yield from recurse(sub, slug_rel / s)

    yield from recurse(mod_dir, Path())


def build_tree():
    """Copy articles into docs/, append references, build nav. Returns
    (nav_modules, stats)."""
    nav_modules = []
    stats = {"articles": 0, "topics": 0, "pdfs": 0}
    for mod in MODULES:
        mod_slug = slugify(mod, set())
        (DOCS / mod_slug).mkdir(parents=True, exist_ok=True)

        # asset symlink: docs/assets/<mod_slug> -> <mod_dir>
        assets_dir = DOCS / "assets"
        assets_dir.mkdir(exist_ok=True)
        link = assets_dir / mod_slug
        target = os.path.relpath(ROOT / mod, assets_dir)
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(target)

        # child nav entries keyed by parent slug path
        children_nav: dict[str, list] = {}
        topic_rows = []

        dirs = list(walk_module(mod))
        for dir_path, mslug, slug_rel in dirs:
            if not slug_rel.parts:
                continue  # module root handled separately
            title = pretty(dir_path.name)
            files = [p for p in dir_path.iterdir() if p.is_file()]
            pdfs, transcripts, attachments = classify(files)
            stats["pdfs"] += len(pdfs)

            out_dir = DOCS / mslug / slug_rel
            out_dir.mkdir(parents=True, exist_ok=True)
            rel_to_root = "/".join([".."] * len(out_dir.relative_to(DOCS).parts))

            article_dir = ARTICLES / mslug / slug_rel
            article = article_dir / "index.md"
            sub_articles = []
            if article.exists():
                body = article.read_text(encoding="utf-8").rstrip()
                stats["articles"] += 1
                # copy article assets (img/ etc.)
                for extra in article_dir.iterdir():
                    if extra.name == "index.md":
                        continue
                    dest = out_dir / extra.name
                    if extra.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(extra, dest)
                    else:
                        shutil.copy2(extra, dest)
                # sub-articles: any other .md files become child pages
                for sub_md in sorted(article_dir.glob("*.md")):
                    if sub_md.name == "index.md":
                        continue
                    sub_slug = sub_md.stem
                    sub_out = out_dir / sub_slug
                    sub_out.mkdir(exist_ok=True)
                    shutil.copy2(sub_md, sub_out / "index.md")
                    sub_title = pretty(sub_md.stem)
                    sub_articles.append(
                        {sub_title: f"{(sub_out / 'index.md').relative_to(DOCS).as_posix()}"}
                    )
            else:
                body = (f"# {title}\n\n"
                        f"_Article not written yet — source material below._")

            # children pages of this dir (already processed dirs are deeper;
            # collect links from slug_rel mapping)
            child_links = []
            for cdir, cmslug, cslug_rel in dirs:
                if cmslug == mslug and cslug_rel.parent == slug_rel and cslug_rel.parts:
                    child_links.append((pretty(cdir.name), cslug_rel.name))

            md = body + "\n\n"
            if child_links:
                md += "## Sub-sections\n\n"
                md += "\n".join(f"- [{t}]({s}/index.md)" for t, s in child_links) + "\n\n"
            md += references_md(pdfs, transcripts, attachments, rel_to_root, mslug, mod)
            (out_dir / "index.md").write_text(md, encoding="utf-8")

            entry_list = [f"{(out_dir / 'index.md').relative_to(DOCS).as_posix()}"] + sub_articles
            parent_key = slug_rel.parent.as_posix()
            children_nav.setdefault(parent_key, []).append({title: entry_list})
            if slug_rel.parent == Path():
                n_pdfs = len(pdfs)
                topic_rows.append((title, slug_rel.name, n_pdfs))

        # attach child entries (depth-1 topics get their subtrees)
        def nav_for(slug_rel: Path):
            entries = []
            for item in children_nav.get(slug_rel.as_posix(), []):
                (t, lst), = item.items()
                own = lst[0]
                subs = lst[1:]
                child_slug = own.rsplit("/", 2)[-2] if own.endswith("/index.md") else own
                deeper = nav_for(slug_rel / child_slug)
                entries.append({t: [own] + subs + deeper})
            return entries

        nav_for_root = nav_for(Path())

        # module curriculum page
        mtitle = f"{mod} — {MODULE_TITLES[mod]}"
        lines = [f"# {mtitle}", "", MODULE_BLURBS[mod], "", "## Curriculum", "",
                 "| Topic | Source decks |", "|---|---|"]
        for ttitle, tslug, n_pdfs in topic_rows:
            lines.append(f"| [{ttitle}]({tslug}/index.md) | {n_pdfs} |")
        lines.append("")
        (DOCS / mod_slug / "index.md").write_text("\n".join(lines), encoding="utf-8")
        stats["topics"] += len(topic_rows)
        nav_modules.append({mtitle: [f"{mod_slug}/index.md"] + nav_for_root})
    return nav_modules, stats


# ------------------------------------------------------------- glossary etc.

def build_glossary_nav():
    src = ROOT / "Files" / "cards_export.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    cards = data["cards"]
    tabs: dict[str, list] = {}
    for c in cards:
        tabs.setdefault(c["tab"], []).append(c)

    gdir = DOCS / "glossary"
    gdir.mkdir(exist_ok=True)
    index_lines = [
        "# Glossary", "",
        f"Acronym and term reference cards ({len(cards)} entries), grouped by topic.", "",
        "## Topics", "",
    ]
    entries = []
    for tab in sorted(tabs):
        slug_tab = re.sub(r"[^a-z0-9]+", "-", tab.lower()).strip("-")
        lines = [f"# {tab}", ""]
        for c in sorted(tabs[tab], key=lambda x: x["name"].lower()):
            acr = c.get("acronym") or ""
            lines.append(f"## {c['name']}" + (f" — *{acr}*" if acr else ""))
            lines += ["", c.get("desc") or ""]
            bullets = c.get("bullets") or []
            if bullets:
                lines += [""] + [f"- {b}" for b in bullets]
            lines.append("")
        (gdir / f"{slug_tab}.md").write_text("\n".join(lines), encoding="utf-8")
        index_lines.append(f"- [{tab}]({slug_tab}.md) — {len(tabs[tab])} entries")
        entries.append({tab: f"glossary/{slug_tab}.md"})
    (gdir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return [{"Overview": "glossary/index.md"}] + entries


def build_resources():
    lines = ["# External Resources", "", "Video links referenced by the academy materials.", ""]
    for fname in ["VideoLinks.txt", "MIL2_Links.txt"]:
        src = ROOT / "Files" / fname
        if not src.exists():
            continue
        lines.append(f"## {pretty(fname)}")
        lines.append("")
        for ln in src.read_text(encoding="utf-8", errors="replace").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if " - " in ln:
                name, url = ln.split(" - ", 1)
                lines.append(f"- [{name.strip()}]({url.strip()})")
            elif ln.startswith("http"):
                lines.append(f"- <{ln}>")
            else:
                lines.append(f"- {ln}")
        lines.append("")
    cheat = ROOT / "MIL1" / "vv_cheat_sheet.html"
    if cheat.exists():
        lines += ["## Cheat sheets", "", "- [V&V Cheat Sheet](assets/mil1/vv_cheat_sheet.html)", ""]
    (DOCS / "resources.md").write_text("\n".join(lines), encoding="utf-8")


def build_home(stats):
    md = f"""# Kineton Academy Wiki

The knowledge base for the Academy bootcamp in automotive E/E engineering.
Every article is **written for reading on the web** — distilled from the
academy's slide decks and lecture recordings, with diagrams, key takeaways and
links to the original files at the bottom of each page.

**{stats['topics']} topics · {stats['articles']} articles · {stats['pdfs']} source decks**,
organized into the four bootcamp modules below. Use the search bar to jump to
any concept.

<div class="grid cards" markdown>

-   :material-school: __MIL1 — Vehicle Fundamentals__

    ---

    {MODULE_BLURBS["MIL1"]}

    [:octicons-arrow-right-24: Start with MIL1](mil1/index.md)

-   :material-tools: __MIL2 — Tools & Testing Basics__

    ---

    {MODULE_BLURBS["MIL2"]}

    [:octicons-arrow-right-24: Continue to MIL2](mil2/index.md)

-   :material-engine: __MIL3 — Requirements, HIL & Calibration__

    ---

    {MODULE_BLURBS["MIL3"]}

    [:octicons-arrow-right-24: Continue to MIL3](mil3/index.md)

-   :material-check-decagram: __MIL4 — Verification & Validation__

    ---

    {MODULE_BLURBS["MIL4"]}

    [:octicons-arrow-right-24: Continue to MIL4](mil4/index.md)

-   :material-book-alphabet: __Glossary__

    ---

    Acronyms and term cards: protocols, diagnostics, calibration,
    Vector tools, files & formats, ECU topology.

    [:octicons-arrow-right-24: Open glossary](glossary/index.md)

-   :material-play-circle: __External Resources__

    ---

    Curated YouTube videos and reference cheat sheets.

    [:octicons-arrow-right-24: See resources](resources.md)

</div>

!!! tip "How to use this wiki during the bootcamp"
    - Follow the modules in order — each module page is the curriculum.
    - Articles are self-contained study notes; the **Source material** and
      **Downloads** sections at the bottom link the original PDFs, DBC/CDD
      databases and lecture transcripts.
    - Diagrams are drawn with Mermaid or cropped from the original slides where
      a figure was worth keeping.
"""
    (DOCS / "index.md").write_text(md, encoding="utf-8")


MKDOCS_HEADER = """\
site_name: Kineton Academy Wiki
site_description: Bootcamp knowledge base for automotive E/E engineering
docs_dir: docs
edit_uri: ""
use_directory_urls: true
theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      toggle:
        icon: material/weather-night
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      toggle:
        icon: material/weather-sunny
        name: Switch to light mode
  features:
    - navigation.sections
    - navigation.indexes
    - navigation.top
    - navigation.footer
    - toc.follow
    - search.highlight
    - search.suggest
plugins:
  - search
markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
exclude_docs: |
  *.mp3
"""


def write_mkdocs(nav_modules, glossary_entries):
    import yaml

    nav = (
        [{"Home": "index.md"}]
        + nav_modules
        + [{"Glossary": glossary_entries}]
        + [{"Resources": "resources.md"}]
    )
    nav_yaml = yaml.safe_dump({"nav": nav}, sort_keys=False, allow_unicode=True, width=120)
    (WIKI / "mkdocs.yml").write_text(MKDOCS_HEADER + nav_yaml, encoding="utf-8")


# ------------------------------------------------------------------ manifest

def write_manifest():
    """Authoring aid: for every directory, list its article path and source
    material (deck-extraction cache JSONs, transcripts, other files)."""
    sys.path.insert(0, str(WIKI))
    import extract_decks

    decks = extract_decks.load_cache()  # {(mod, slug): deck data}
    cache_by_pdf = {}
    for (mod, _), d in decks.items():
        cache_by_pdf[(mod, d["pdf"])] = (
            WIKI / ".cache" / "decks" / mod.lower() / f"{d['slug']}-{d['key'][:8]}.json"
        )

    manifest = {}
    for mod in MODULES:
        for dir_path, mslug, slug_rel in walk_module(mod):
            if not slug_rel.parts:
                continue
            files = [p for p in dir_path.iterdir() if p.is_file()]
            pdfs, transcripts, attachments = classify(files)
            rel_dir = dir_path.relative_to(ROOT / mod).as_posix()
            entry = {
                "title": pretty(dir_path.name),
                "module": mod,
                "source_dir": str(dir_path),
                "article_path": str(ARTICLES / mslug / slug_rel / "index.md"),
                "slide_images_dir": str(WIKI / ".cache" / "img" / mod.lower()),
                "decks": [],
                "transcripts": [str(t) for t in transcripts],
                "other_files": [str(a) for a in attachments],
            }
            for p in pdfs:
                rel_pdf = p.relative_to(ROOT / mod).as_posix()
                cj = cache_by_pdf.get((mod, rel_pdf))
                if cj and cj.exists():
                    d = decks.get((mod, re.sub(r"^\d+-", "",
                             re.sub(r"[^a-z0-9]+", "-", p.stem.lower()).strip("-")) or "deck"))
                    entry["decks"].append({
                        "pdf": str(p),
                        "cache_json": str(cj),
                        "title": d["title"] if d else pretty(p.name),
                        "pages": d["pages"] if d else None,
                        "img_dir": d["img_dir"] if d else None,
                    })
            manifest[f"{mslug}/{slug_rel.as_posix()}"] = entry
    out = WIKI / ".cache" / "source_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"manifest: {out} ({len(manifest)} directories)")


def main():
    assert (ROOT / "MIL1").is_dir(), "run from project root"
    if "--manifest" in sys.argv:
        write_manifest()
        return
    DOCS.mkdir(parents=True, exist_ok=True)
    # clean generated markdown/pages but keep assets/ (symlinks + nothing else)
    for child in DOCS.iterdir():
        if child.name == "assets":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    nav_modules, stats = build_tree()
    build_home(stats)
    build_resources()
    glossary_entries = build_glossary_nav()
    write_mkdocs(nav_modules, glossary_entries)
    print(f"wiki assembled: {stats['topics']} topics, {stats['articles']} articles, "
          f"{stats['pdfs']} source decks")


if __name__ == "__main__":
    main()
