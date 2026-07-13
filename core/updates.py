"""
Checks GitHub's public Releases API to see if a newer BungusTweaks version
is available. Uses only the standard library (urllib) - no new dependency,
no auth needed since the repo is public. Best-effort: any failure (offline,
rate-limited, repo renamed, etc.) just returns None rather than raising.
"""

import json
import urllib.request

GITHUB_API_URL = "https://api.github.com/repos/J750N/bungustweaks/releases/latest"
GITHUB_RELEASES_URL = "https://github.com/J750N/bungustweaks/releases"


def _version_parts(v: str):
    return [int(p) for p in v.strip().lstrip("vV").split(".") if p.isdigit()]


def check_for_update(current_version: str, timeout: int = 5):
    """Returns a dict describing the latest release, or None if the check
    failed for any reason (no internet, rate-limited, etc). Never raises."""
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "BungusTweaks"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        latest_version = data.get("tag_name", "").strip()
        notes = (data.get("body") or "").strip()
        url = data.get("html_url", GITHUB_RELEASES_URL)

        try:
            is_newer = _version_parts(latest_version) > _version_parts(current_version)
        except Exception:
            is_newer = latest_version.lstrip("vV") != current_version.lstrip("vV")

        return {
            "available": is_newer,
            "latest_version": latest_version,
            "notes": notes,
            "url": url,
        }
    except Exception:
        return None


def parse_release_notes(markdown_text: str):
    """Turns GitHub release markdown into a simple structured list the UI can
    render as real widgets (not raw markdown syntax). Handles the subset we
    actually write in release notes: ## / ### headers, - bullets, **bold**,
    `code`, > blockquotes, [links](url), and plain paragraphs."""
    import re

    def clean_inline(text):
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)       # **bold** -> bold
        text = re.sub(r"`(.+?)`", r"\1", text)             # `code` -> code
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", text)  # [text](url) -> text
        return text.strip()

    lines_out = []
    for raw_line in markdown_text.replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("### "):
            lines_out.append({"type": "h3", "text": clean_inline(line[4:])})
        elif line.startswith("## "):
            lines_out.append({"type": "h2", "text": clean_inline(line[3:])})
        elif line.startswith("# "):
            lines_out.append({"type": "h2", "text": clean_inline(line[2:])})
        elif line.startswith("- ") or line.startswith("* "):
            lines_out.append({"type": "bullet", "text": clean_inline(line[2:])})
        elif line.startswith(">"):
            lines_out.append({"type": "quote", "text": clean_inline(line.lstrip("> "))})
        else:
            lines_out.append({"type": "text", "text": clean_inline(line)})
    return lines_out
