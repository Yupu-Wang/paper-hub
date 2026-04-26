from pathlib import Path
from scrapers.common.ndss import parse_index, parse_paper_page

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_index_returns_paper_entries():
    html = (FIXTURES / "ndss_index_2026.html").read_text()
    entries = parse_index(html)
    # NDSS 2026 has ~265 accepted papers
    assert len(entries) > 200
    # Each entry has a title and url
    assert all("title" in e and "url" in e for e in entries)
    assert all(e["url"].startswith("https://www.ndss-symposium.org/ndss-paper/") for e in entries)
    assert all(e["title"] for e in entries)


def test_parse_paper_page_extracts_authors_and_abstract():
    html = (FIXTURES / "ndss_paper_sample.html").read_text()
    meta = parse_paper_page(html)
    assert isinstance(meta["authors"], list)
    assert len(meta["authors"]) >= 1
    # Author names should not contain affiliation parens
    for a in meta["authors"]:
        assert "(" not in a, f"author should be clean: {a!r}"
    assert isinstance(meta["abstract"], str)
    assert len(meta["abstract"]) > 100


def test_authors_split_correctly():
    """Real sample has 8 co-authors."""
    html = (FIXTURES / "ndss_paper_sample.html").read_text()
    meta = parse_paper_page(html)
    assert len(meta["authors"]) == 8
    assert "Licheng Pan" in meta["authors"]
    assert "Kui Ren" in meta["authors"]
