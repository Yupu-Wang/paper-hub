from __future__ import annotations
from bs4 import BeautifulSoup


def parse_archive_for_year(html: str, year: int) -> list[str]:
    """Return issue URLs whose title contains 'AAAI-<yy>' for the given year."""
    yy = str(year)[-2:]  # 2026 → "26"
    needle = f"AAAI-{yy}"
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.select("a.title"):
        if needle in a.get_text():
            href = a.get("href", "").strip()
            if href:
                out.append(href)
    return out


def parse_issue_articles(html: str) -> list[dict]:
    """Return [{title, authors[list], url}] for an AAAI/OJS issue page."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for div in soup.select("div.obj_article_summary"):
        title_a = div.select_one("h3.title a")
        if not title_a:
            continue
        url = title_a.get("href", "").strip()
        if not url:
            continue
        title = title_a.get_text(strip=True)
        authors_el = div.select_one("div.authors")
        authors_text = authors_el.get_text(strip=True) if authors_el else ""
        authors = [a.strip() for a in authors_text.split(",") if a.strip()]
        out.append({"title": title, "authors": authors, "url": url})
    return out


def parse_paper_abstract(html: str) -> str:
    """Extract abstract text from an OJS article page; strips 'Abstract' label."""
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one("section.item.abstract") or soup.select_one(".item.abstract")
    if el is None:
        return ""
    # Remove the heading "Abstract" if present
    h = el.find(["h2", "h3"])
    if h:
        h.extract()
    return el.get_text(" ", strip=True)
