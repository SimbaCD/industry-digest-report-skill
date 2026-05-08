from __future__ import annotations

import argparse
import csv
import glob
import html
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_IMAGE = "ghcr.io/rachelos/we-mp-rss:latest"
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
BUILTIN_TEMPLATE_DIR = PACKAGE_ROOT / "templates"
DB_CANDIDATE_NAMES = {"db.db", "database.sqlite"}
DEFAULT_CONTENT_LIMIT = 8000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generic industry-digest setup and WeRSS inspection helper.")
    parser.add_argument(
        "command",
        choices=[
            "init",
            "doctor",
            "write-werss-compose",
            "templates",
            "select-template",
            "stats",
            "targets",
            "candidates",
            "render",
        ],
        help="Command to run",
    )
    parser.add_argument("--project", default=".", help="Project/workspace directory")
    parser.add_argument("--period", help="Target month, e.g. 2026-04")
    parser.add_argument("--theme", default="default", help="Theme name under themes/<name>.json")
    parser.add_argument("--output", help="Output file for targets, JSON or CSV")
    parser.add_argument("--limit", type=int, default=160, help="Maximum target rows")
    parser.add_argument("--min-score", type=int, default=2, help="Minimum title-screen score")
    parser.add_argument("--input", help="Input JSON path for render; defaults to outputs/<period>/validated_items.json")
    parser.add_argument("--port", type=int, default=8001, help="WeRSS host port for generated compose file")
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="WeRSS Docker image for generated compose file")
    parser.add_argument(
        "--template",
        default="starter",
        help="Template slug, template file path, or 'starter' for the minimal built-in starter",
    )
    return parser.parse_args()


def project_root(args: argparse.Namespace) -> Path:
    return Path(args.project).expanduser().resolve()


def month_bounds(period: str) -> tuple[str, str]:
    if not period or not re.fullmatch(r"\d{4}-\d{2}", period):
        raise ValueError("--period must be in YYYY-MM form")
    year, month = map(int, period.split("-"))
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def template_slug(path: Path) -> str:
    stem = path.stem
    return stem.removeprefix("template-")


def template_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return path.stem
    match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    if match:
        return clean_text(match.group(1))
    return path.stem


def builtin_templates() -> list[dict[str, str]]:
    items = [
        {
            "slug": "starter",
            "title": "Starter minimal template",
            "path": "",
            "notes": "Minimal HTML starter. Use when the user wants a blank, conservative base.",
        }
    ]
    if BUILTIN_TEMPLATE_DIR.exists():
        for path in sorted(BUILTIN_TEMPLATE_DIR.glob("*.html")):
            items.append(
                {
                    "slug": template_slug(path),
                    "title": template_title(path),
                    "path": str(path),
                    "notes": template_notes(template_slug(path)),
                }
            )
    return items


def template_notes(slug: str) -> str:
    notes = {
        "chronicle": "Timeline/chronicle layout. Best for date-order policy, research, and text-heavy digests.",
        "nocturne": "Magazine-grid layout. Best for authoritative business, financial, legal, or market reviews with a strong lead story.",
    }
    return notes.get(slug, "User-provided HTML template.")


def print_templates() -> int:
    print_kv({"templates": builtin_templates()})
    return 0


def resolve_template(template: str) -> Path | None:
    if not template or template == "starter":
        return None
    candidate = Path(template).expanduser()
    if candidate.exists():
        return candidate.resolve()
    for item in builtin_templates():
        if item["slug"] == template and item["path"]:
            return Path(item["path"])
    raise FileNotFoundError(f"Template not found: {template}. Run industryctl templates to list available templates.")


def write_starter_template(path: Path) -> None:
    path.write_text(
        """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Industry Digest</title>
</head>
<body>
  <main>
    <h1>Industry Digest</h1>
    <p>Replace this starter template with your own H5/report template.</p>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def install_template(root: Path, template: str) -> dict[str, str]:
    template_path = root / "templates" / "report.html"
    source = resolve_template(template)
    if source is None:
        if not template_path.exists():
            write_starter_template(template_path)
        return {"template": "starter", "template_source": ""}
    shutil.copy2(source, template_path)
    return {"template": template_slug(source), "template_source": str(source)}


def init_project(root: Path, template: str) -> None:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "themes").mkdir(parents=True, exist_ok=True)
    (root / "outputs").mkdir(parents=True, exist_ok=True)
    (root / "templates").mkdir(parents=True, exist_ok=True)
    template_info = install_template(root, template)

    config_path = root / "config" / "config.json"
    if not config_path.exists():
        write_json(
            config_path,
            {
                "project_name": "Industry Digest",
                "output_root": "outputs",
                "theme": "default",
                "themes_dir": "themes",
                "template": template_info["template"],
                "templates_dir": "templates",
                "werss": {
                    "db_path": "",
                    "db_glob": "./werss-data/**/*",
                    "tracked_mp_ids": [],
                    "content_min_chars": 500,
                },
                "report": {
                    "max_final_items": 100,
                    "summary_min_chars": 160,
                    "summary_max_chars": 240,
                },
            },
        )

    theme_path = root / "themes" / "default.json"
    if not theme_path.exists():
        write_json(
            theme_path,
            {
                "name": "default",
                "display_name": "Industry Digest",
                "description": "A configurable public-account industry digest.",
                "keywords": ["industry", "policy", "market"],
                "strong_keywords": ["regulation", "project", "investment"],
                "negative_keywords": ["recruitment", "training", "livestream"],
                "sections": [
                    "Domestic Updates",
                    "Regional Updates",
                    "International Updates",
                    "Policy and Regulation",
                    "Professional Updates",
                ],
                "summary_chars": [160, 240],
                "max_final_items": 100,
            },
        )


def write_compose(root: Path, image: str, port: int) -> Path:
    path = root / "docker-compose.werss.yml"
    path.write_text(
        f"""services:
  werss:
    image: {image}
    container_name: we-mp-rss
    ports:
      - \"{port}:8001\"
    volumes:
      - ./werss-data:/app/data
    restart: unless-stopped
""",
        encoding="utf-8",
    )
    return path


def select_template(root: Path, template: str) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    (root / "templates").mkdir(parents=True, exist_ok=True)
    info = install_template(root, template)
    config_path = root / "config" / "config.json"
    if config_path.exists():
        config = load_json(config_path)
        config["template"] = info["template"]
        config["templates_dir"] = "templates"
        write_json(config_path, config)
    return info


def run_probe(command: list[str], timeout: int = 15) -> tuple[bool, str]:
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        return False, "not found"
    except Exception as exc:
        return False, str(exc)
    output = (proc.stdout or proc.stderr or "").strip().splitlines()
    return proc.returncode == 0, output[0] if output else f"exit={proc.returncode}"


def resolve_config(root: Path) -> dict[str, Any]:
    config_path = root / "config" / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config: {config_path}. Run industryctl init first.")
    return load_json(config_path)


def load_theme(root: Path, config: dict[str, Any], name: str) -> dict[str, Any]:
    themes_dir = root / str(config.get("themes_dir", "themes"))
    path = themes_dir / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing theme: {path}")
    return load_json(path)


def find_db(root: Path, config: dict[str, Any]) -> Path:
    werss = config.get("werss", {})
    if werss.get("db_path"):
        path = Path(str(werss["db_path"]))
        if not path.is_absolute():
            path = root / path
        if path.exists():
            return path
        raise FileNotFoundError(f"WeRSS DB not found: {path}")

    pattern = str(werss.get("db_glob") or "./werss-data/**/*")
    pattern_path = Path(pattern)
    if not pattern_path.is_absolute():
        pattern = str(root / pattern)
    matches = [Path(p) for p in glob.glob(pattern, recursive=True) if Path(p).name in DB_CANDIDATE_NAMES]
    if not matches:
        fallback_patterns = [root / "werss-data" / "**" / name for name in DB_CANDIDATE_NAMES]
        for fallback in fallback_patterns:
            matches.extend(Path(p) for p in glob.glob(str(fallback), recursive=True))
    if not matches:
        raise FileNotFoundError(f"WeRSS SQLite DB not found by glob: {pattern}")
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def quick_check(db_path: Path) -> str:
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return con.execute("PRAGMA quick_check").fetchone()[0]
    finally:
        con.close()


def article_columns(con: sqlite3.Connection) -> set[str]:
    return {row[1] for row in con.execute("PRAGMA table_info(articles)").fetchall()}


def inspect_schema(db_path: Path) -> dict[str, Any]:
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        tables = {row[0] for row in con.execute("select name from sqlite_master where type='table'").fetchall()}
        columns = article_columns(con) if "articles" in tables else set()
        return {
            "has_articles_table": "articles" in tables,
            "has_feeds_table": "feeds" in tables,
            "article_columns": sorted(columns),
            "has_content_field": bool({"content", "content_html"} & columns),
        }
    finally:
        con.close()


def sql_text_expr(columns: set[str], name: str) -> str:
    return f"coalesce(a.{name}, '')" if name in columns else "''"


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def read_rows(db_path: Path, config: dict[str, Any], period: str) -> list[dict[str, Any]]:
    start, end = month_bounds(period)
    ids = [str(x) for x in config.get("werss", {}).get("tracked_mp_ids", [])]
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        columns = article_columns(con)
        if not columns:
            raise RuntimeError("WeRSS DB has no articles table or articles table has no columns.")
        content_html = sql_text_expr(columns, "content_html")
        content = sql_text_expr(columns, "content")
        params: list[Any] = [start, end]
        source_clause = ""
        if ids:
            placeholders = ",".join("?" for _ in ids)
            source_clause = f"and a.mp_id in ({placeholders})"
            params = [*ids, start, end]
        rows = con.execute(
            f"""
            select
              a.id,
              a.mp_id,
              coalesce(f.mp_name, a.mp_id) as source,
              a.title,
              a.url,
              a.description,
              a.publish_time,
              datetime(a.publish_time, 'unixepoch', 'localtime') as published_local,
              {content_html} as content_html,
              {content} as content,
              length({content_html}) as content_html_len,
              length({content}) as content_len
            from articles a
            left join feeds f on f.id = a.mp_id
            where {source_clause[4:] if source_clause else '1=1'}
              and datetime(a.publish_time, 'unixepoch', 'localtime') >= ?
              and datetime(a.publish_time, 'unixepoch', 'localtime') < ?
            order by a.publish_time asc, a.id asc
            """,
            params,
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        con.close()


def effective_content(row: dict[str, Any]) -> str:
    return clean_text(row.get("content_html")) or clean_text(row.get("content"))


def row_pub_date(row: dict[str, Any]) -> str:
    published = str(row.get("published_local") or "")
    return published[:10]


def output_dir(root: Path, config: dict[str, Any], period: str) -> Path:
    out_root = Path(str(config.get("output_root") or "outputs"))
    if not out_root.is_absolute():
        out_root = root / out_root
    return out_root / period


def write_table_or_json(path: Path, payload_key: str, rows: list[dict[str, Any]], extra: dict[str, Any] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        fieldnames = sorted({key for row in rows for key in row.keys()}) or ["rank"]
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        payload = dict(extra or {})
        payload[payload_key] = rows
        write_json(path, payload)


def print_kv(payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            print(f"{key}=" + json.dumps(value, ensure_ascii=False))
        else:
            print(f"{key}={value}")


def doctor(root: Path) -> int:
    result: dict[str, Any] = {
        "status": "ok",
        "project": str(root),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    docker_ok, docker_msg = run_probe(["docker", "--version"])
    compose_ok, compose_msg = run_probe(["docker", "compose", "version"])
    daemon_ok, daemon_msg = run_probe(["docker", "info"], timeout=20)
    result.update(
        {
            "docker_cli": docker_msg,
            "docker_cli_ok": docker_ok,
            "docker_compose": compose_msg,
            "docker_compose_ok": compose_ok,
            "docker_daemon_ok": daemon_ok,
            "docker_daemon": daemon_msg,
        }
    )
    if not docker_ok or not compose_ok:
        result["status"] = "needs_docker_install"
    elif not daemon_ok:
        result["status"] = "needs_docker_start"
    try:
        config = resolve_config(root)
        result["config_ok"] = True
        try:
            db = find_db(root, config)
            result["werss_db"] = str(db)
            result["werss_quick_check"] = quick_check(db)
            result["schema"] = inspect_schema(db)
        except Exception as exc:
            result["werss_db_status"] = "missing_or_not_configured"
            result["werss_db_message"] = str(exc)
            if result["status"] == "ok":
                result["status"] = "needs_werss_data"
    except Exception as exc:
        result["config_ok"] = False
        result["config_error"] = str(exc)
        result["status"] = "needs_init"
    print_kv(result)
    return 0


def stats(root: Path, period: str) -> int:
    config = resolve_config(root)
    db = find_db(root, config)
    min_chars = int(config.get("werss", {}).get("content_min_chars", 500))
    rows = read_rows(db, config, period)
    by_source: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    ready = 0
    nonempty = 0
    for row in rows:
        source = clean_text(row.get("source") or row.get("mp_id") or "unknown")
        text = effective_content(row)
        by_source[source]["total"] += 1
        if text:
            nonempty += 1
        if len(text) >= min_chars:
            ready += 1
            by_source[source]["ready"] += 1
        else:
            by_source[source]["missing"] += 1
    print_kv(
        {
            "period": period,
            "werss_db": str(db),
            "content_min_chars": min_chars,
            "total_articles": len(rows),
            "content_nonempty": nonempty,
            "fulltext_ready": ready,
            "fulltext_missing": len(rows) - ready,
            "by_source": by_source,
        }
    )
    return 0


def score_row(row: dict[str, Any], theme: dict[str, Any], min_chars: int) -> tuple[int, list[str]]:
    text = clean_text(f"{row.get('title')} {row.get('description')}")
    score = 0
    reasons: list[str] = []
    for label, weight in [("strong_keywords", 4), ("keywords", 2)]:
        hits = [term for term in theme.get(label, []) if term and term in text]
        if hits:
            score += min(20, len(hits) * weight)
            reasons.append(label + ":" + "/".join(hits[:6]))
    negative = [term for term in theme.get("negative_keywords", []) if term and term in text]
    if negative:
        score -= min(10, len(negative) * 3)
        reasons.append("negative:" + "/".join(negative[:6]))
    content_len = len(effective_content(row))
    if content_len >= min_chars:
        reasons.append("ready")
    return score, reasons


def article_payload(row: dict[str, Any], score: int, reasons: list[str], include_content: bool) -> dict[str, Any]:
    content = effective_content(row)
    payload = {
        "score": score,
        "source": clean_text(row.get("source") or row.get("mp_id")),
        "mp_id": clean_text(row.get("mp_id")),
        "db_id": clean_text(row.get("id")),
        "pub_date": row_pub_date(row),
        "title": clean_text(row.get("title")),
        "url": clean_text(row.get("url")),
        "description": clean_text(row.get("description")),
        "content_len": len(content),
        "score_reasons": ";".join(reasons),
    }
    payload["fulltext_status"] = "ready" if payload["content_len"] else "missing"
    if include_content:
        payload["content_text"] = content[:DEFAULT_CONTENT_LIMIT]
        payload["content_truncated"] = len(content) > DEFAULT_CONTENT_LIMIT
        payload["content_limit"] = DEFAULT_CONTENT_LIMIT
    return payload


def targets(root: Path, period: str, theme_name: str, output: str | None, limit: int, min_score: int) -> int:
    config = resolve_config(root)
    theme = load_theme(root, config, theme_name)
    db = find_db(root, config)
    min_chars = int(config.get("werss", {}).get("content_min_chars", 500))
    rows = read_rows(db, config, period)
    items: list[dict[str, Any]] = []
    for row in rows:
        score, reasons = score_row(row, theme, min_chars)
        if score < min_score:
            continue
        content_len = len(effective_content(row))
        if content_len >= min_chars:
            continue
        payload = article_payload(row, score, reasons, include_content=False)
        payload["fulltext_status"] = "missing"
        items.append(payload)
    items.sort(key=lambda item: (-item["score"], item["pub_date"], item["title"]))
    items = items[: max(0, limit)]
    for index, item in enumerate(items, 1):
        item["rank"] = index
    if output:
        path = Path(output)
        if not path.is_absolute():
            path = root / path
    else:
        path = root / "outputs" / period / "title_repair_targets.json"
    write_table_or_json(path, "targets", items, {"period": period, "theme": theme_name})
    print_kv({"period": period, "theme": theme_name, "targets": len(items), "output": str(path)})
    return 0


def candidates(root: Path, period: str, theme_name: str, output: str | None, limit: int, min_score: int) -> int:
    config = resolve_config(root)
    theme = load_theme(root, config, theme_name)
    db = find_db(root, config)
    min_chars = int(config.get("werss", {}).get("content_min_chars", 500))
    rows = read_rows(db, config, period)
    items: list[dict[str, Any]] = []
    for row in rows:
        content_len = len(effective_content(row))
        if content_len < min_chars:
            continue
        score, reasons = score_row(row, theme, min_chars)
        if score < min_score:
            continue
        payload = article_payload(row, score, reasons, include_content=True)
        payload["fulltext_status"] = "ready"
        items.append(payload)
    items.sort(key=lambda item: (-item["score"], item["pub_date"], item["source"], item["title"]))
    items = items[: max(0, limit)]
    for index, item in enumerate(items, 1):
        item["rank"] = index
    if output:
        path = Path(output)
        if not path.is_absolute():
            path = root / path
    else:
        path = output_dir(root, config, period) / "candidates.json"
    write_table_or_json(path, "articles", items, {"period": period, "theme": theme_name})
    print_kv({"period": period, "theme": theme_name, "candidates": len(items), "output": str(path)})
    return 0


def h(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def listify(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean_text(v) for v in value if clean_text(v)]
    text = clean_text(value)
    return [text] if text else []


def read_template_assets(root: Path) -> dict[str, str]:
    template_path = root / "templates" / "report.html"
    if not template_path.exists():
        template_path = PACKAGE_ROOT / "templates" / "template-chronicle.html"
    text = template_path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    links = "\n".join(re.findall(r"<link\b[^>]*>", text, re.I))
    styles = "\n".join(re.findall(r"<style\b[^>]*>.*?</style>", text, re.I | re.S))
    return {"title": clean_text(title_match.group(1)) if title_match else "Industry Digest", "links": links, "styles": styles}


def normalize_report(root: Path, period: str, input_path: Path) -> dict[str, Any]:
    config = resolve_config(root)
    data = load_json(input_path)
    articles = data.get("articles") or data.get("items") or []
    meta = data.get("meta") or {}
    title = meta.get("title") or data.get("title") or config.get("project_name") or "Industry Digest"
    sections = data.get("sections") or []
    if not sections:
        seen: list[str] = []
        for item in articles:
            section = clean_text(item.get("section") or "Updates")
            if section not in seen:
                seen.append(section)
        sections = seen or ["Updates"]
    return {
        "period": period,
        "title": title,
        "subtitle": meta.get("subtitle") or data.get("subtitle") or "",
        "organization": meta.get("organization") or data.get("organization") or "",
        "issue": meta.get("issue") or data.get("issue") or "",
        "source_label": meta.get("source_label") or data.get("source_label") or "WeRSS local full text",
        "start_date": meta.get("start_date") or data.get("start_date") or "",
        "end_date": meta.get("end_date") or data.get("end_date") or "",
        "guide": listify(data.get("guide") or data.get("monthly_guide")),
        "about": listify(data.get("about")),
        "contacts": data.get("contacts") or [],
        "sections": sections,
        "articles": articles,
    }


def section_counts(report: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {section: 0 for section in report["sections"]}
    for item in report["articles"]:
        section = clean_text(item.get("section") or "Updates")
        counts[section] = counts.get(section, 0) + 1
    return counts


def render_key_facts(item: dict[str, Any], style: str) -> str:
    facts = item.get("key_facts") or item.get("facts") or []
    if not facts:
        return ""
    if style == "nocturne":
        parts = ['<div class="art-facts">']
        for fact in facts[:4]:
            parts.append(
                f'<div><span class="fv">{h(fact.get("value", ""))}</span>'
                f'<span class="fl">{h(fact.get("label", ""))}</span>'
                f'<span class="fc">{h(fact.get("context", ""))}</span></div>'
            )
        parts.append("</div>")
        return "\n".join(parts)
    parts = ['<div class="tl-facts">']
    for fact in facts[:4]:
        parts.append(
            f'<div class="tl-fact"><span class="fact-val">{h(fact.get("value", ""))}</span>'
            f'<span class="fact-lbl">{h(fact.get("label", ""))}</span>'
            f'<span class="fact-ctx">{h(fact.get("context", ""))}</span></div>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_visual_blocks(item: dict[str, Any], style: str) -> str:
    blocks = item.get("visual_blocks") or item.get("blocks") or []
    if not blocks:
        return ""
    block_class = "art-vblock" if style == "nocturne" else "tl-vblock"
    parts: list[str] = []
    for block in blocks[:2]:
        parts.append(f'<div class="{block_class}">')
        parts.append(f'<div class="vb-head">{h(block.get("type", "Info"))} · {h(block.get("title", ""))}</div>')
        for row in block.get("items", [])[:4]:
            parts.append(f'<div class="vb-row">{h(row)}</div>')
        parts.append("</div>")
    return "\n".join(parts)


def render_note(item: dict[str, Any], style: str) -> str:
    note = clean_text(item.get("note") or item.get("legal_note") or item.get("compliance_note"))
    if not note:
        return ""
    note_class = "art-note" if style == "nocturne" else "tl-note"
    label = clean_text(item.get("note_label") or "专业要点")
    return (
        f'<div class="{note_class}" onclick="toggleNote(this)">'
        f'<strong>{h(label)}</strong><span class="note-toggle">▸ 展开</span>'
        f'<div class="note-body">{h(note)}</div></div>'
    )


def render_chronicle(report: dict[str, Any], assets: dict[str, str]) -> str:
    year, month = (report["period"].split("-") + [""])[:2]
    counts = section_counts(report)
    nav = "\n".join(
        f'<button onclick="filterSec(this,\'s{i}\')">{h(section)}</button>' for i, section in enumerate(report["sections"], 1)
    )
    stats = "\n".join(
        f'<a class="stat-cell" href="#s{i}" style="--cell-color:var(--c{min(i,5)})">'
        f'<span class="stat-n">{counts.get(section, 0)}</span><span class="stat-lbl">{h(section)}</span></a>'
        for i, section in enumerate(report["sections"][:5], 1)
    )
    lead = "\n".join(f'<p class="lead-text">{h(p)}</p>' for p in report["guide"])
    sections: list[str] = []
    for i, section in enumerate(report["sections"], 1):
        items = [item for item in report["articles"] if clean_text(item.get("section") or "Updates") == section]
        sections.append(
            f'<div class="tl-section" id="s{i}" style="--sec-color:var(--c{min(i,5)})">'
            f'<span class="tl-sec-name">{h(section)}</span><span class="tl-sec-count">{len(items)} 则</span></div>'
        )
        for item in items:
            title = h(item.get("title"))
            url = h(item.get("url") or "#")
            sections.append(
                '<article class="tl-entry">'
                f'<div class="tl-date">{h(item.get("pub_date") or item.get("date"))}</div>'
                f'<div class="tl-title"><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></div>'
                f'<div class="tl-byline"><span class="src-pill">{h(item.get("source"))}</span><span class="badge badge-full">全文</span></div>'
                f'<div class="tl-summary">{h(item.get("summary"))}</div>'
                f'{render_key_facts(item, "chronicle")}{render_visual_blocks(item, "chronicle")}{render_note(item, "chronicle")}'
                '</article>'
            )
    about = "\n".join(f"<p>{h(p)}</p>" for p in report["about"])
    return html_page(
        report,
        assets,
        f"""
<div id="prog"></div>
<main class="page">
  <header class="masthead">
    <span class="masthead-ornament">{h(report["organization"] or report["source_label"])}</span>
    <div class="masthead-title">{h(report["title"])}</div>
    <div class="masthead-subtitle">{h(report["subtitle"])}</div>
    <div class="masthead-meta"><span>第 {h(report["issue"])} 期</span><span>{h(year)}年{h(month)}月</span><span>共 {len(report["articles"])} 则</span></div>
  </header>
  <div class="info-strip"><span>采集区间：<span class="info-strong">{h(report["start_date"] or report["period"])}</span> — <span class="info-strong">{h(report["end_date"] or report["period"])}</span> · 来源：{h(report["source_label"])}</span><button class="dl-btn" onclick="dlReport()">下载 HTML</button></div>
  <div class="stat-row">{stats}</div>
  <section class="lead-block"><div class="lead-label">本 期 导 读</div>{lead}</section>
  <nav id="sec-nav"><button class="active" onclick="filterSec(this,'')">全部</button>{nav}</nav>
  <section class="timeline">{"".join(sections)}</section>
  <section class="about-block"><div class="about-label">关 于 本 刊</div>{about}</section>
</main>
""",
    )


def render_nocturne(report: dict[str, Any], assets: dict[str, str]) -> str:
    year, month = (report["period"].split("-") + [""])[:2]
    counts = section_counts(report)
    stats = "\n".join(
        f'<a class="stat-cell" href="#s{i}" style="--cell-color:var(--c{min(i,5)})">'
        f'<span class="stat-n">{counts.get(section, 0)}</span><span class="stat-lbl">{h(section)}</span></a>'
        for i, section in enumerate(report["sections"][:5], 1)
    )
    nav = "\n".join(
        f'<button onclick="filterSec(this,\'s{i}\')">{h(section)}</button>' for i, section in enumerate(report["sections"], 1)
    )
    lead = "\n".join(f"<p>{h(p)}</p>" for p in report["guide"])
    sections: list[str] = []
    for i, section in enumerate(report["sections"], 1):
        items = [item for item in report["articles"] if clean_text(item.get("section") or "Updates") == section]
        sections.append(
            f'<div class="sec-block" id="s{i}"><div class="sec-header">'
            f'<div class="sec-name" style="--sec-color:var(--c{min(i,5)})">{h(section)}</div>'
            f'<div class="sec-rule"></div><div class="sec-count">{len(items)} 条</div></div><div class="article-grid">'
        )
        for index, item in enumerate(items):
            card_class = "art-card card-feature" if index == 0 else "art-card"
            title = h(item.get("title"))
            url = h(item.get("url") or "#")
            sections.append(
                f'<article class="{card_class}" style="--sec-color:var(--c{min(i,5)})">'
                f'<div><div class="art-title"><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></div>'
                f'<div class="art-byline"><span class="src-tag">{h(item.get("source"))}</span><span>{h(item.get("pub_date") or item.get("date"))}</span><span class="badge badge-full">全文</span></div>'
                f'<div class="art-summary">{h(item.get("summary"))}</div>'
                f'{render_key_facts(item, "nocturne")}{render_visual_blocks(item, "nocturne")}{render_note(item, "nocturne")}</div>'
                '</article>'
            )
        sections.append("</div></div>")
    about = "\n".join(f"<p>{h(p)}</p>" for p in report["about"])
    return html_page(
        report,
        assets,
        f"""
<div id="prog"></div>
<main class="page">
  <header class="header-band">
    <div class="header-top"><span class="header-firm">{h(report["organization"] or report["source_label"])}</span><span class="header-date-row">{h(year)}.{h(month)}</span></div>
    <div class="header-main"><div class="header-left"><div class="header-eyebrow">行业动态月度观察</div><div class="header-title">{h(report["title"])}</div><div class="header-tagline">{h(report["subtitle"])}</div></div><div class="header-right"><span class="issue-big">{h(report["issue"])}</span></div></div>
    <div class="info-line">采集：<strong>{h(report["start_date"] or report["period"])}</strong> — <strong>{h(report["end_date"] or report["period"])}</strong> · 来源：{h(report["source_label"])} · 入选：<strong>{len(report["articles"])}</strong> 条 <button class="dl-btn" onclick="dlReport()">下载 HTML</button></div>
  </header>
  <div class="stat-bar">{stats}</div>
  <div class="lead-strip"><div class="lead-strip-label">本 期 导 读</div><div class="lead-strip-line"></div></div>
  <section class="lead-card"><h2>编 辑 导 语</h2>{lead}</section>
  <nav id="sec-nav"><button class="active" onclick="filterSec(this,'')">全部</button>{nav}</nav>
  {"".join(sections)}
  <section class="about-block"><div class="about-label">关 于 本 刊</div>{about}</section>
</main>
""",
    )


def render_starter(report: dict[str, Any], assets: dict[str, str]) -> str:
    article_html = []
    for item in report["articles"]:
        article_html.append(
            f'<article><h3><a href="{h(item.get("url") or "#")}">{h(item.get("title"))}</a></h3>'
            f'<p>{h(item.get("source"))} · {h(item.get("pub_date") or item.get("date"))}</p>'
            f'<p>{h(item.get("summary"))}</p></article>'
        )
    return html_page(report, assets, f'<main><h1>{h(report["title"])}</h1>{"".join(article_html)}</main>')


def html_page(report: dict[str, Any], assets: dict[str, str], body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{h(report["title"])}</title>
{assets.get("links", "")}
{assets.get("styles", "")}
</head>
<body>
{body}
<script>
window.addEventListener('scroll',function(){{var p=document.getElementById('prog');if(!p)return;var h=document.documentElement.scrollHeight-window.innerHeight;p.style.width=(h>0?window.scrollY/h*100:0)+'%';}});
function filterSec(btn,sec){{document.querySelectorAll('#sec-nav button').forEach(function(b){{b.classList.remove('active');}});if(btn)btn.classList.add('active');document.querySelectorAll('.sec-block,section[id^="s"],.tl-section,.tl-entry').forEach(function(el){{if(!sec){{el.style.display='';return;}}var inside=false;if(el.id===sec)inside=true;var prev=el.previousElementSibling;while(prev){{if(prev.id===sec){{inside=true;break;}}if(/^s\\d+$/.test(prev.id||''))break;prev=prev.previousElementSibling;}}el.style.display=inside?'':'none';}});}}
function toggleNote(el){{el.classList.toggle('open');var t=el.querySelector('.note-toggle');if(t)t.textContent=el.classList.contains('open')?'▾ 收起':'▸ 展开';}}
function dlReport(){{var blob=new Blob(['<!doctype html>\\n'+document.documentElement.outerHTML],{{type:'text/html;charset=utf-8'}});var url=URL.createObjectURL(blob);var a=document.createElement('a');a.href=url;a.download='industry-digest-{h(report["period"])}.html';document.body.appendChild(a);a.click();setTimeout(function(){{document.body.removeChild(a);URL.revokeObjectURL(url);}},200);}}
</script>
</body>
</html>
"""


def render_report(root: Path, period: str, input_file: str | None, output_file: str | None) -> int:
    config = resolve_config(root)
    out_dir = output_dir(root, config, period)
    source = Path(input_file) if input_file else out_dir / "validated_items.json"
    if not source.is_absolute():
        source = root / source
    if not source.exists():
        raise FileNotFoundError(f"Missing validated items JSON: {source}")
    report = normalize_report(root, period, source)
    assets = read_template_assets(root)
    template = str(config.get("template") or "starter")
    if template == "chronicle":
        html_text = render_chronicle(report, assets)
    elif template == "nocturne":
        html_text = render_nocturne(report, assets)
    else:
        html_text = render_starter(report, assets)
    output = Path(output_file) if output_file else out_dir / "report.html"
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_text, encoding="utf-8")
    print_kv({"period": period, "template": template, "input": str(source), "report_html": str(output)})
    return 0


def main() -> int:
    args = parse_args()
    root = project_root(args)
    try:
        if args.command == "init":
            init_project(root, args.template)
            compose = write_compose(root, args.image, args.port)
            print_kv({"status": "ok", "project": str(root), "template": args.template, "compose": str(compose)})
            return 0
        if args.command == "write-werss-compose":
            root.mkdir(parents=True, exist_ok=True)
            compose = write_compose(root, args.image, args.port)
            print_kv({"status": "ok", "compose": str(compose)})
            return 0
        if args.command == "select-template":
            info = select_template(root, args.template)
            print_kv({"status": "ok", "project": str(root), **info, "installed": str(root / "templates" / "report.html")})
            return 0
        if args.command == "doctor":
            return doctor(root)
        if args.command == "templates":
            return print_templates()
        if args.command == "stats":
            return stats(root, args.period or "")
        if args.command == "targets":
            return targets(root, args.period or "", args.theme, args.output, args.limit, args.min_score)
        if args.command == "candidates":
            return candidates(root, args.period or "", args.theme, args.output, args.limit, args.min_score)
        if args.command == "render":
            return render_report(root, args.period or "", args.input, args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
