from __future__ import annotations
from bs4 import BeautifulSoup


def parse_index(html: str) -> list[dict]:
    """Return [{title, url}, ...] for all accepted papers on an NDSS year index page."""
    soup = BeautifulSoup(html, "html.parser")
    entries = []
    seen = set()
    for h in soup.select("h2.pt-cv-title"):
        a = h.find("a", href=True)
        if not a:
            continue
        url = a["href"].strip()
        if "/ndss-paper/" not in url or url in seen:
            continue
        seen.add(url)
        entries.append({"title": a.get_text(strip=True), "url": url})
    return entries


def parse_paper_page(html: str) -> dict:
    """Extract authors (list[str]) and abstract (str) from an NDSS paper page."""
    soup = BeautifulSoup(html, "html.parser")
    data = soup.select_one("div.paper-data") or soup.select_one("div.entry-content")
    if data is None:
        return {"authors": [], "abstract": ""}

    strong = data.find("strong")
    authors_text = strong.get_text(" ", strip=True) if strong else ""
    if strong:
        strong.extract()

    abstract = data.get_text(" ", strip=True)
    return {"authors": _split_authors(authors_text), "abstract": abstract}


def _split_authors(s: str) -> list[str]:
    """'Alice (Foo), Bob (Bar)' → ['Alice', 'Bob']."""
    if not s:
        return []
    out = []
    depth = 0
    cur = []
    for ch in s:
        if ch == "(":
            depth += 1
            continue
        if ch == ")":
            depth = max(0, depth - 1)
            continue
        if depth > 0:
            continue
        if ch == "," and depth == 0:
            name = "".join(cur).strip()
            if name:
                out.append(name)
            cur = []
        else:
            cur.append(ch)
    name = "".join(cur).strip()
    if name:
        out.append(name)
    return out
