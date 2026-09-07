"""MkDocs hooks for the CMP portal.

Two jobs, both in service of one rule: a results entry is written once, in its
markdown file, and everything else is derived from it.

1. Before every build, regenerate cmp/docs/results/index.json and the timeline
   block in cmp/docs/results/index.md from the entries' front matter. So
   `mkdocs serve` always shows what the entries currently say, and an agent who
   forgets to run the generator by hand still sees the truth locally.

2. Expand the `{{ csv_table("results/data/<file>.csv") }}` directive into a
   markdown table read from the CSV at build time. Benchmark numbers live in
   cmp/docs/results/data/ as CSV, not retyped into prose, so a rerun of a
   benchmark updates the page by replacing one file.

The CSV reader is fifteen lines of the standard library rather than a plugin
and a dataframe stack: the tables here are a few dozen rows of numbers, and a
dependency that large would have to earn its place.
"""

from __future__ import annotations

import csv
import importlib.util
import io
import logging
import posixpath
import re
import shutil
import sys
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.cmp-portal")

CMP_DIR = Path(__file__).resolve().parent.parent
GENERATOR = CMP_DIR / "hooks" / "results_index.py"

# Building the docs must not leave anything behind. __pycache__ directories are
# build output, the workspace audit fails on them, and an agent whose only crime
# was running `mkdocs build` should not have to work out why. This stops the
# generator's bytecode being written; on_post_build below removes the hook's
# own, which MkDocs' importer creates before any of this code runs.
sys.dont_write_bytecode = True


_MODULE_NAME = "cmp_results_index"


def _load_generator():
    """Import the generator, whose filename is hyphenated and so not importable.

    It is registered in sys.modules before execution because @dataclass resolves
    its own module by name; a module executed outside sys.modules fails there.
    Reloaded on every call so `mkdocs serve` picks up an edited generator.
    """
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, GENERATOR)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot load {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_MODULE_NAME, None)
        raise
    return module


def on_pre_build(config, **kwargs) -> None:
    try:
        generator = _load_generator()
        entries = generator.load_entries()
        outputs = {
            generator.INDEX_JSON: generator.build_json(entries),
            generator.TIMELINE_MD: generator.splice(
                generator.TIMELINE_MD.read_text(encoding="utf-8"),
                generator.build_timeline(entries),
            ),
        }
        changed = []
        for path, text in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                path.write_text(text, encoding="utf-8")
                changed.append(path.name)
        if changed:
            log.info("regenerated %s from %d results entries", ", ".join(changed), len(entries))
    except Exception as exc:  # surfaced, never swallowed: a stale index is a lie
        log.error("results index generation failed: %s", exc)


def on_post_build(config, **kwargs) -> None:
    """Remove the bytecode caches importing this hook creates.

    Runs after every build and every `mkdocs serve` rebuild, so previewing the
    site can never be the reason the workspace audit fails.
    """
    for cache in (CMP_DIR / "hooks" / "__pycache__", CMP_DIR / "scripts" / "__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def _csv_table(docs_dir: Path, rel_path: str, page_url: str) -> str:
    path = docs_dir / rel_path
    if not path.is_file():
        log.warning("csv_table: no such file: %s", rel_path)
        return (
            f'!!! warning "Not published yet"\n\n'
            f"    `{rel_path}` is not in this checkout. A benchmark CSV is\n"
            f"    published deliberately once its run has completed and its rows\n"
            f"    are verified, so this is the expected state while a run is in\n"
            f"    flight. See `cmp/.gitignore` for the publish step.\n"
        )

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))

    if not rows:
        log.warning("csv_table: %s is empty", rel_path)
        return f'!!! warning "Empty data file"\n\n    `{rel_path}` has no header row.\n'

    header, body = rows[0], rows[1:]
    out = io.StringIO()
    if not body:
        out.write(
            f'!!! info "No rows yet"\n\n'
            f"    `{rel_path}` carries its header and no measurements. A run that\n"
            f"    produced no complete row is not a result; the table appears here\n"
            f"    as soon as one does.\n\n"
        )
    out.write("| " + " | ".join(h.replace("_", " ") for h in header) + " |\n")
    out.write("|" + "|".join("---" for _ in header) + "|\n")
    for row in body:
        cells = (row + [""] * len(header))[: len(header)]
        out.write("| " + " | ".join(c.strip() or "&mdash;" for c in cells) + " |\n")
    # Relative, never rooted at "/": the site is published under a project path
    # on GitHub Pages, where an absolute link would leave the site.
    href = posixpath.relpath(rel_path, start=posixpath.dirname(page_url.rstrip("/")))
    out.write(f"\n[Download `{Path(rel_path).name}`]({href}){{ .cmp-data-link download }}\n")
    return out.getvalue()


_FENCE = re.compile(r"^\s*(```+|~~~+)")


def on_page_markdown(markdown: str, page, config, **kwargs) -> str:
    if "csv_table(" not in markdown:
        return markdown
    docs_dir = Path(config["docs_dir"])
    page_url = page.file.url
    pattern = _load_generator().CSV_TABLE

    # Substitute outside fenced blocks only, so a page can document the
    # directive by showing it in a code fence without expanding it.
    out: list[str] = []
    fence: str | None = None
    for line in markdown.split("\n"):
        marker = _FENCE.match(line)
        if fence is None and marker:
            fence = marker.group(1)
        elif fence is not None and marker and marker.group(1).startswith(fence):
            fence = None
        elif fence is None and pattern.search(line):
            # Re-indent to the directive's own column so the block stays inside
            # whatever admonition, content tab or list item contains it.
            indent = line[: len(line) - len(line.lstrip())]
            block = pattern.sub(
                lambda m: _csv_table(docs_dir, m.group("path"), page_url), line.strip()
            )
            line = "\n".join(indent + ln if ln else "" for ln in block.rstrip("\n").split("\n"))
        out.append(line)
    return "\n".join(out)
