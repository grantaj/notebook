from __future__ import annotations


def page_title(path: str, markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            if title:
                return title
    leaf = path.rsplit("/", 1)[-1]
    return leaf.removesuffix(".md").replace("-", " ").replace("_", " ").title()


def append_exchange(markdown: str, author: str, user_text: str, ai_text: str) -> str:
    base = markdown.rstrip()
    separator = "\n\n" if base else ""
    return (
        f"{base}{separator}---\n\n"
        f"### {author}\n\n{user_text.strip()}\n\n"
        f"### AI\n\n{ai_text.strip()}\n"
    )
