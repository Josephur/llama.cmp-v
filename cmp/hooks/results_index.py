#!/usr/bin/env python3
"""Build the machine-readable results index from the timeline entries.

The markdown files under cmp/docs/results/ are the single source of truth. This
script reads their YAML front matter and derives two things from it:

  cmp/docs/results/index.json   the index agents read
  cmp/docs/results/index.md     the human timeline, between the TIMELINE markers

Nothing here invents content. Every field in the JSON either comes from an
entry's front matter verbatim or is derived from the entry's own body, so an
entry is edited in exactly one place.

Usage:

    cmp/hooks/results_index.py                  regenerate the outputs
    cmp/hooks/results_index.py --check          fail if outputs are stale
    cmp/hooks/results_index.py --validate-only  check the entries only

--validate-only is what cmp/scripts/close-experiment.sh wants before it changes
anything: it says whether the entries themselves are valid, without judging
outputs that the close-out is about to rewrite anyway. It pairs with
--allow-missing-patch <mechanism>, which waives the "a kept entry names an
existing patch file" rule for exactly one mechanism: the close-out script has to
validate an entry in the moment before it writes that entry's patch, and without
this the rule would make a kept verdict impossible to reach. The waiver is
per-mechanism and never applies to --check, which is what CI runs.

--check is what CI and the pre-push hook want: it never writes, and it exits
non-zero when a committed output does not match what the entries say. That
keeps a regenerated file from turning the working tree dirty and failing the
workspace audit.

Validation is deliberately strict. An entry that is missing a field, that
carries an unknown verdict, or that has no diagram is rejected with the reason
named, because an entry nobody can trust is worse than no entry at all.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guidance only
    sys.exit(
        "PyYAML is required.\n"
        "  python3 -m venv cmp/.venv\n"
        "  cmp/.venv/bin/pip install -r cmp/docs-requirements.txt\n"
        "then run this script with cmp/.venv/bin/python."
    )

CMP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = CMP_DIR / "docs" / "results"
PATCHES_DIR = CMP_DIR / "patches"
INDEX_JSON = RESULTS_DIR / "index.json"
TIMELINE_MD = RESULTS_DIR / "index.md"

BEGIN = "<!-- BEGIN GENERATED TIMELINE -->"
END = "<!-- END GENERATED TIMELINE -->"

SCHEMA_VERSION = 1

VERDICTS = ("kept", "rejected", "inconclusive", "superseded", "template")
BYTE_EXACT = (True, False, "not-applicable")
REQUIRED = (
    "title",
    "mechanism",
    "date",
    "verdict",
    "selectors",
    "contexts",
    "byte_exact",
    "deltas",
    "commit",
    "upstream_base",
    "upstream_prs",
)
# "template" is deliberately NOT a field: mkdocs reserves that page-meta key
# for choosing a Jinja template. The template entry is identified by its
# verdict instead.
OPTIONAL = ("evidence", "tags", "supersedes", "superseded_by", "patch", "data", "promotion")

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
FILENAME = re.compile(r"\A(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)\.md\Z")
SELECTOR = re.compile(r"\A[A-Z][A-Z0-9_]*\Z")
MERMAID = re.compile(r"^```\s*mermaid\s*$", re.MULTILINE)
# A patch is the machine-applicable record of a KEPT mechanism, named after the
# mechanism it implements so a patch and its write-up can never drift apart.
# See cmp/patches/README.md and cmp/docs/results/schema.md.
PATCH_FILE = re.compile(r"\Acmp/patches/\d{4}-([a-z0-9][a-z0-9-]*)\.patch\Z")
# The upstream commit the fork sat on when this was measured. Required, because
# two results both describing "stock" taken either side of a rebase measure
# different upstreams and are otherwise indistinguishable. Short or full sha.
UPSTREAM_BASE = re.compile(r"\A[0-9a-f]{7,40}\Z")
PATCH_REQUIRED = ("kept",)
PATCH_ALLOWED = ("kept", "superseded")

CSV_TABLE = re.compile(r"\{\{\s*csv_table\(\s*['\"](?P<path>[^'\"]+)['\"]\s*\)\s*\}\}")


class EntryError(Exception):
    pass


@dataclass
class Entry:
    path: Path
    meta: dict
    body: str

    @property
    def url(self) -> str:
        return f"results/{self.path.stem}/"

    @property
    def summary(self) -> str:
        """First prose paragraph of the body, derived rather than duplicated."""
        for block in re.split(r"\n\s*\n", self.body.strip()):
            # Indented blocks belong to an admonition, tab or list item; they are
            # not the entry's lead paragraph even when they read like one.
            if block.startswith(("    ", "\t")):
                continue
            block = block.strip()
            if not block or block.startswith(("#", "```", "<!--", "!!!", "===", "|", "<", "-", "*", ">")):
                continue
            text = re.sub(r"\s+", " ", block)
            text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links to their text
            text = re.sub(r"[*_`]", "", text)
            return text
        return ""

    @property
    def headline(self) -> dict | None:
        deltas = self.meta.get("deltas") or []
        for delta in deltas:
            if delta.get("headline"):
                return delta
        return deltas[0] if deltas else None


def read_entry(path: Path) -> Entry | None:
    """Parse one results file. Returns None for pages that are not entries."""
    raw = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(raw)
    if not match:
        return None
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict) or "mechanism" not in meta:
        return None  # a normal page such as schema.md, not a timeline entry
    return Entry(path=path, meta=meta, body=match.group(2))


def validate(entry: Entry, seen: dict[str, Path], pending_patch: str | None = None) -> list[str]:
    problems: list[str] = []
    meta = entry.meta
    name = entry.path.name

    for key in REQUIRED:
        if key not in meta:
            problems.append(f"missing required front-matter key: {key}")
    known = set(REQUIRED) | set(OPTIONAL)
    for key in meta:
        if key not in known:
            problems.append(f"unknown front-matter key: {key}")
    base = meta.get("upstream_base")
    if base is not None and not UPSTREAM_BASE.match(str(base)):
        problems.append(f"upstream_base must be a git sha (7-40 hex chars), got {base!r}")
    prs = meta.get("upstream_prs")
    if prs is not None and not isinstance(prs, list):
        problems.append("upstream_prs must be a list (use [] when the base is unmodified)")
    elif isinstance(prs, list):
        for n in prs:
            if not isinstance(n, int):
                problems.append(f"upstream_prs entries must be PR numbers as integers, got {n!r}")

    mechanism = meta.get("mechanism")
    if isinstance(mechanism, str):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", mechanism):
            problems.append(f"mechanism must be a lowercase slug, got {mechanism!r}")
        if mechanism in seen:
            problems.append(f"mechanism {mechanism!r} already used by {seen[mechanism].name}")
        else:
            seen[mechanism] = entry.path

    date = str(meta.get("date", ""))
    if not DATE.match(date):
        problems.append(f"date must be YYYY-MM-DD, got {date!r}")

    if name != "template.md":
        stem = FILENAME.match(name)
        if not stem:
            problems.append("filename must be YYYY-MM-DD-<mechanism>.md")
        else:
            if stem.group(1) != date:
                problems.append(f"filename date {stem.group(1)} does not match front matter {date}")
            if stem.group(2) != mechanism:
                problems.append(f"filename mechanism {stem.group(2)!r} does not match front matter {mechanism!r}")

    verdict = meta.get("verdict")
    if verdict not in VERDICTS:
        problems.append(f"verdict must be one of {', '.join(VERDICTS)}, got {verdict!r}")
    if (verdict == "template") != (name == "template.md"):
        problems.append("verdict 'template' is reserved for template.md, and template.md must use it")

    selectors = meta.get("selectors")
    if not isinstance(selectors, list):
        problems.append("selectors must be a list, [] when the mechanism has none")
    else:
        for sel in selectors:
            if not isinstance(sel, str) or not SELECTOR.match(sel):
                problems.append(f"selector {sel!r} is not an ENV_STYLE_NAME")

    contexts = meta.get("contexts")
    if not isinstance(contexts, list) or not contexts:
        problems.append("contexts must be a non-empty list of prompt token counts")
    elif not all(isinstance(c, int) for c in contexts):
        problems.append("contexts must be integers, in tokens")

    if meta.get("byte_exact") not in BYTE_EXACT:
        problems.append("byte_exact must be true, false, or not-applicable")

    if verdict == "kept" and meta.get("byte_exact") is not True:
        problems.append("kept requires byte_exact: true")
    if meta.get("promotion") not in (None, "awaiting-decision", "accepted", "declined"):
        problems.append("promotion must be awaiting-decision, accepted or declined")

    if verdict == "kept":
        evidence = meta.get("evidence")
        if not isinstance(evidence, str) or not evidence.startswith("cmp/docs/results/data/") or ".." in evidence:
            problems.append("kept requires reviewed evidence under cmp/docs/results/data/")
        elif not (CMP_DIR.parent / evidence).is_file():
            problems.append("evidence file does not exist")

    deltas = meta.get("deltas")
    if not isinstance(deltas, list):
        problems.append("deltas must be a list, [] when nothing was measured")
    else:
        for i, delta in enumerate(deltas):
            if not isinstance(delta, dict):
                problems.append(f"deltas[{i}] must be a mapping")
                continue
            for key in ("metric", "context", "change_pct"):
                if key not in delta:
                    problems.append(f"deltas[{i}] is missing {key}")
            if "change_pct" in delta and not isinstance(delta["change_pct"], (int, float)):
                problems.append(f"deltas[{i}].change_pct must be a number, signed, in percent")

    for key in ("tags", "supersedes", "data"):
        if key in meta and not isinstance(meta[key], list):
            problems.append(f"{key} must be a list")

    # The patch field. A rejected mechanism that leaves a patch file behind is
    # indistinguishable from a kept one a year later, which is how a closed
    # question gets re-opened; so the field is policed rather than suggested.
    # cmp/scripts/close-experiment.sh is allowed to validate one entry whose patch
    # it is about to write; nothing else may.
    pending = pending_patch is not None and mechanism == pending_patch
    patch = meta.get("patch")
    if patch in (None, "", "null"):
        patch = None
        if verdict in PATCH_REQUIRED and not pending:
            problems.append(
                f"verdict '{verdict}' requires a patch: field naming a file in cmp/patches/ "
                "(cmp/scripts/close-experiment.sh writes it)"
            )
    elif not isinstance(patch, str):
        problems.append("patch must be a path string such as cmp/patches/0005-example.patch")
    else:
        if verdict not in PATCH_ALLOWED:
            problems.append(
                f"verdict '{verdict}' must not carry a patch: field. Only a kept mechanism "
                "gets a patch file; for a rejection the write-up is the artifact, not the code."
            )
        stem = PATCH_FILE.match(patch)
        if not stem:
            problems.append(f"patch must be cmp/patches/NNNN-<mechanism>.patch, got {patch!r}")
        elif stem.group(1) != mechanism:
            problems.append(
                f"patch {patch!r} names mechanism {stem.group(1)!r} but this entry is {mechanism!r}; "
                "a patch and its write-up are matched on the slug"
            )
        if not pending and not (CMP_DIR.parent / patch).exists():
            problems.append(f"patch file not found: {patch}")

    for csv_name in meta.get("data") or []:
        if not (RESULTS_DIR / "data" / str(csv_name)).exists():
            problems.append(f"data file not found: docs/results/data/{csv_name}")

    if not MERMAID.search(entry.body):
        problems.append("no mermaid diagram: every entry must carry one, see results/schema.md")

    return problems


def load_entries(pending_patch: str | None = None) -> list[Entry]:
    entries: list[Entry] = []
    seen: dict[str, Path] = {}
    failures: list[str] = []
    for path in sorted(RESULTS_DIR.glob("*.md")):
        entry = read_entry(path)
        if entry is None:
            continue
        problems = validate(entry, seen, pending_patch)
        if problems:
            failures.extend(f"{path.relative_to(CMP_DIR.parent)}: {p}" for p in problems)
        entries.append(entry)
    if failures:
        raise EntryError("\n".join(failures))
    entries.sort(key=lambda e: (str(e.meta["date"]), e.meta["mechanism"]), reverse=True)
    return entries


def build_json(entries: list[Entry]) -> str:
    records = []
    for entry in entries:
        record = {
            "mechanism": entry.meta["mechanism"],
            "title": entry.meta["title"],
            "date": str(entry.meta["date"]),
            "verdict": entry.meta["verdict"],
            "selectors": entry.meta.get("selectors", []),
            "contexts": entry.meta.get("contexts", []),
            "byte_exact": entry.meta.get("byte_exact"),
            "deltas": entry.meta.get("deltas", []),
            "commit": entry.meta.get("commit"),
            "upstream_base": entry.meta.get("upstream_base"),
            "upstream_prs": entry.meta.get("upstream_prs") or [],
            "patch": entry.meta.get("patch"),
            "evidence": entry.meta.get("evidence"),
            "promotion": entry.meta.get("promotion"),
            "tags": sorted(entry.meta.get("tags", [])),
            "supersedes": entry.meta.get("supersedes", []),
            "superseded_by": entry.meta.get("superseded_by"),
            "data": entry.meta.get("data", []),
            "template": entry.meta["verdict"] == "template",
            "source": f"cmp/docs/results/{entry.path.name}",
            "url": entry.url,
            "summary": entry.summary,
        }
        records.append(record)

    by_selector: dict[str, list[str]] = {}
    by_verdict: dict[str, list[str]] = {}
    by_tag: dict[str, list[str]] = {}
    for record in records:
        if record["template"]:
            continue
        for sel in record["selectors"]:
            by_selector.setdefault(sel, []).append(record["mechanism"])
        by_verdict.setdefault(record["verdict"], []).append(record["mechanism"])
        for tag in record["tags"]:
            by_tag.setdefault(tag, []).append(record["mechanism"])

    document = {
        "schema_version": SCHEMA_VERSION,
        "generator": "cmp/hooks/results_index.py",
        "source_of_truth": "cmp/docs/results/*.md",
        "note": "Generated. Do not edit. Edit the markdown entry and regenerate.",
        "schema_reference": None,
        "entry_count": len(records),
        "entries": records,
        "by_selector": {k: sorted(v) for k, v in sorted(by_selector.items())},
        "by_verdict": {k: sorted(v) for k, v in sorted(by_verdict.items())},
        "by_tag": {k: sorted(v) for k, v in sorted(by_tag.items())},
    }
    # No generation timestamp: the output must be a pure function of the inputs,
    # or every rebuild dirties the tree and the workspace audit fails.
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def fmt_context(tokens: int) -> str:
    if tokens >= 1000 and tokens % 1024 == 0:
        return f"{tokens // 1024}K"
    if tokens >= 1000:
        return f"{tokens / 1000:g}K"
    return str(tokens)


def fmt_headline(delta: dict | None) -> str:
    if not delta:
        return "no measurement claimed"
    pct = delta.get("change_pct")
    sign = "+" if isinstance(pct, (int, float)) and pct > 0 else ""
    metric = str(delta.get("metric", "")).replace("_", " ")
    where = delta.get("context")
    at = f" at {fmt_context(where)}" if isinstance(where, int) else ""
    return f"{sign}{pct}% {metric}{at}"


def build_timeline(entries: list[Entry]) -> str:
    if not entries:
        return (
            '<p class="cmp-timeline-empty">No entries yet. The first experiment to '
            "finish writes the first one.</p>"
        )

    byte_exact_label = {True: "byte-exact", False: "output changed", "not-applicable": "n/a"}
    rows = []
    for entry in entries:
        meta = entry.meta
        verdict = str(meta["verdict"])
        classes = f"cmp-entry cmp-verdict-{verdict}"
        selectors = ", ".join(f"<code>{escape(s)}</code>" for s in meta.get("selectors") or []) or "none"
        contexts = ", ".join(fmt_context(c) for c in meta.get("contexts") or []) or "none"
        commit = meta.get("commit")
        commit_html = f'<code>{escape(str(commit))}</code>' if commit else "not retained"
        banner = ""
        if verdict == "template":
            banner = (
                '<p class="cmp-entry-banner">Template placeholder. Not a real result. '
                "It exists to show the shape of an entry.</p>"
            )
        rows.append(
            f'<li class="{classes}">\n'
            f'  <div class="cmp-entry-when"><time datetime="{escape(str(meta["date"]))}">'
            f'{escape(str(meta["date"]))}</time></div>\n'
            f'  <div class="cmp-entry-card">\n'
            f'    <p class="cmp-entry-head">'
            f'<a href="{escape(entry.path.stem)}/">{escape(str(meta["title"]))}</a>'
            f'<span class="cmp-pill cmp-pill-{verdict}">{escape(verdict)}</span></p>\n'
            f"{banner}\n"
            f'    <p class="cmp-entry-summary">{escape(entry.summary)}</p>\n'
            f'    <dl class="cmp-entry-meta">\n'
            f"      <dt>headline</dt><dd>{escape(fmt_headline(entry.headline))}</dd>\n"
            f"      <dt>selectors</dt><dd>{selectors}</dd>\n"
            f"      <dt>contexts</dt><dd>{contexts}</dd>\n"
            f"      <dt>output</dt><dd>"
            f'{escape(byte_exact_label.get(meta.get("byte_exact"), "unknown"))}</dd>\n'
            f"      <dt>commit</dt><dd>{commit_html}</dd>\n"
            f"    </dl>\n"
            f"  </div>\n"
            f"</li>"
        )
    return '<ol class="cmp-timeline">\n' + "\n".join(rows) + "\n</ol>"


def splice(markdown: str, block: str) -> str:
    if BEGIN not in markdown or END not in markdown:
        raise EntryError(
            f"{TIMELINE_MD} is missing the {BEGIN} / {END} markers; "
            "the generated timeline has nowhere to go."
        )
    head, rest = markdown.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n{block}\n{END}{tail}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="do not write; fail if outputs are stale")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate the entries and stop; do not read or compare the generated outputs",
    )
    parser.add_argument(
        "--allow-missing-patch",
        metavar="MECHANISM",
        help="waive the kept-entry patch-file rule for one mechanism whose patch is "
        "about to be written. Only cmp/scripts/close-experiment.sh should pass this.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.allow_missing_patch and args.check:
        print("--allow-missing-patch cannot be combined with --check", file=sys.stderr)
        return 2

    try:
        entries = load_entries(args.allow_missing_patch)
    except EntryError as exc:
        print("results entries are invalid:\n" + str(exc), file=sys.stderr)
        return 1

    if args.validate_only:
        if not args.quiet:
            print(f"results entries are valid ({len(entries)} entries)")
        return 0

    outputs = {
        INDEX_JSON: build_json(entries),
        TIMELINE_MD: splice(TIMELINE_MD.read_text(encoding="utf-8"), build_timeline(entries)),
    }

    stale = [p for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]

    if args.check:
        if stale:
            print(
                "results index is stale:\n"
                + "\n".join(f"  {p.relative_to(CMP_DIR.parent)}" for p in stale)
                + "\nRun cmp/hooks/results_index.py and commit the result.",
                file=sys.stderr,
            )
            return 1
        if not args.quiet:
            print(f"results index is up to date ({len(entries)} entries)")
        return 0

    for path, text in outputs.items():
        if path in stale:
            path.write_text(text, encoding="utf-8")
    if not args.quiet:
        written = ", ".join(p.name for p in stale) or "nothing (already current)"
        print(f"{len(entries)} entries indexed; wrote {written}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
