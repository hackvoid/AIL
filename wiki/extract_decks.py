#!/usr/bin/env python3
"""Extract text + rendered images from every PDF deck in the MIL* trees.

For each unique PDF (deduplicated by sha1), produces:
  - wiki/.cache/decks/<mod>/<slug>-<hash>.json  (slide titles, cleaned body text)
  - wiki/docs/assets/img/<mod>/<slug>-<hash>/p-NNN.webp  (rendered slide images)

Identical file copies share one extraction (alias cache entries point to the
shared slide data and image dir). Cached by content hash so re-runs are cheap.

Run from the project root:  wiki-venv/bin/python wiki/extract_decks.py [MIL...]
"""

import hashlib
import json
import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.CRITICAL)

import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
CACHE_DIR = WIKI / ".cache" / "decks"
IMG_DIR = WIKI / ".cache" / "img"
MODULES = ["MIL1", "MIL2", "MIL3", "MIL4"]

MAX_IMG_WIDTH = 1280  # px; slides render sharp at this width
WEBP_QUALITY = 80

# boilerplate lines to drop from slide text
BOILERPLATE = re.compile(
    r"(strictly confidential|kineton s\.r\.l|all contents in this document|"
    r"© ?\d{4}|^\d{1,3}$)",
    re.IGNORECASE,
)


def sha1_of(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_slug(path: Path) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return re.sub(r"^\d+-", "", s) or "deck"


def slide_title(page) -> str:
    """Largest-font text on the page = slide title."""
    chunks = []

    def visitor(text, cm, tm, font_dict, font_size):
        t = " ".join(text.split())
        if t and font_size:
            chunks.append((t, font_size))

    try:
        page.extract_text(visitor_text=visitor)
    except Exception:
        return ""
    if not chunks:
        return ""
    maxsz = max(sz for _, sz in chunks)
    if maxsz < 8:
        return ""
    title = " ".join(t for t, sz in chunks if sz >= maxsz * 0.85)
    title = re.sub(r"\s+", " ", title).strip(" -|•")
    return title[:120]


def slide_body(page, title: str) -> str:
    try:
        raw = page.extract_text() or ""
    except Exception:
        return ""
    lines = []
    pending_bullet = False
    for ln in raw.splitlines():
        ln = " ".join(ln.split())
        if not ln:
            continue
        if BOILERPLATE.search(ln):
            continue
        if title and ln in title and len(ln) > 3:
            continue  # drop title echoed in the body
        if ln in ("•", "-", "–", "·"):
            pending_bullet = True
            continue
        if pending_bullet:
            ln = f"- {ln.lstrip('•-–· ')}"
            pending_bullet = False
        elif ln.startswith(("•", "·")):
            ln = f"- {ln.lstrip('•· ')}"
        lines.append(ln)
    # drop duplicated adjacent lines (PDF text run artifacts)
    out = []
    for ln in lines:
        if not out or out[-1] != ln:
            out.append(ln)
    return "\n".join(out)


def render_pages(pdf_path: Path, out_dir: Path, n_pages: int) -> list[str | None]:
    """Render each page to webp. Returns img filename or None per page."""
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[str | None] = [None] * n_pages
    try:
        pdf = pdfium.PdfDocument(str(pdf_path))
        for i in range(n_pages):
            try:
                page = pdf[i]
                w_pt = page.get_width()
                scale = max(0.3, min(2.0, MAX_IMG_WIDTH / w_pt))
                img = page.render(scale=scale).to_pil()
                if img.width > MAX_IMG_WIDTH:
                    h = round(img.height * MAX_IMG_WIDTH / img.width)
                    img = img.resize((MAX_IMG_WIDTH, h))
                name = f"p-{i + 1:03d}.webp"
                img.save(out_dir / name, quality=WEBP_QUALITY, method=6)
                results[i] = name
            except Exception:
                continue
        pdf.close()
    except Exception:
        pass
    # fallback: pdftoppm (poppler) for pages pdfium failed on
    for i in [i for i, r in enumerate(results) if r is None]:
        try:
            with tempfile.TemporaryDirectory() as td:
                prefix = Path(td) / "pg"
                subprocess.run(
                    ["pdftoppm", "-f", str(i + 1), "-l", str(i + 1), "-png",
                     "-scale-to-x", str(MAX_IMG_WIDTH), "-scale-to-y", "-1",
                     "-singlefile", str(pdf_path), str(prefix)],
                    check=True, capture_output=True, timeout=120,
                )
                src = prefix.with_suffix(".png")
                if src.exists():
                    from PIL import Image
                    name = f"p-{i + 1:03d}.webp"
                    Image.open(src).save(out_dir / name, quality=WEBP_QUALITY, method=6)
                    results[i] = name
        except Exception:
            continue
    return results


def extract_pdf(pdf_path: Path, mod: str, sha1_index: dict) -> dict | None:
    h = sha1_of(pdf_path)
    slug = pdf_slug(pdf_path)
    rel = pdf_path.relative_to(ROOT / mod)
    cache_file = CACHE_DIR / mod.lower() / f"{slug}-{h[:8]}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    if h in sha1_index:
        # identical content extracted elsewhere: alias with this file's own path
        base = sha1_index[h]
        data = dict(base, pdf=rel.as_posix(), pdf_name=pdf_path.name, mod=mod)
    else:
        img_dir = f"{slug}-{h[:8]}"
        try:
            reader = PdfReader(str(pdf_path))
            n_pages = len(reader.pages)
        except Exception as e:
            print(f"!! cannot read {pdf_path}: {e}", file=sys.stderr)
            return None
        images = render_pages(pdf_path, IMG_DIR / mod.lower() / img_dir, n_pages)
        slides = []
        for i in range(n_pages):
            title = slide_title(reader.pages[i])
            slides.append({
                "n": i + 1,
                "title": title,
                "body": slide_body(reader.pages[i], title),
                "img": images[i],
            })
        deck_title = slides[0]["title"] or pretty_fallback(pdf_path)
        data = {
            "key": h,
            "pdf": rel.as_posix(),
            "pdf_name": pdf_path.name,
            "mod": mod,
            "slug": slug,
            "img_dir": img_dir,
            "title": deck_title,
            "pages": n_pages,
            "slides": slides,
        }
        sha1_index[h] = data

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def pretty_fallback(path: Path) -> str:
    s = re.sub(r"^\d+_", "", path.stem).replace("___", " - ").replace("_", " ")
    return re.sub(r"\s+", " ", s).strip()


def extract_all(mods=MODULES, verbose=True) -> None:
    sha1_index: dict[str, dict] = {}
    for f in CACHE_DIR.rglob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            sha1_index.setdefault(d["key"], d)
        except Exception:
            continue
    for mod in mods:
        mod_dir = ROOT / mod
        if not mod_dir.is_dir():
            continue
        for pdf_path in sorted(mod_dir.rglob("*.pdf")):
            d = extract_pdf(pdf_path, mod, sha1_index)
            if d and verbose:
                print(f"[{mod}] {d['slug']}: {d['pages']} slides")


def load_cache() -> dict[tuple[str, str], dict]:
    """(mod, slug) -> deck data for everything currently in the cache."""
    decks = {}
    if not CACHE_DIR.is_dir():
        return decks
    for f in CACHE_DIR.rglob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            decks[(d["mod"], d["slug"])] = d
        except Exception:
            continue
    return decks


if __name__ == "__main__":
    extract_all(mods=[m for m in sys.argv[1:] if m.upper().startswith("MIL")] or MODULES)
