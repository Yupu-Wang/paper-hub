from pathlib import Path
from scrapers.common.aaai import (
    parse_archive_for_year,
    parse_issue_articles,
    parse_paper_abstract,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_archive_finds_all_aaai26_tracks():
    html = (FIXTURES / "aaai_archive.html").read_text()
    issues = parse_archive_for_year(html, year=2026)
    assert len(issues) == 25
    assert all(u.startswith("https://ojs.aaai.org/index.php/AAAI/issue/view/") for u in issues)


def test_parse_issue_articles_returns_title_authors_url():
    html = (FIXTURES / "aaai_track_sample.html").read_text()
    articles = parse_issue_articles(html)
    assert len(articles) > 50
    a = articles[0]
    assert a["title"]
    assert isinstance(a["authors"], list)
    assert len(a["authors"]) >= 1
    assert a["url"].startswith("https://ojs.aaai.org/index.php/AAAI/article/view/")
    # No affiliation parens in author names
    for name in a["authors"]:
        assert "(" not in name


def test_parse_paper_abstract_extracts_text():
    html = (FIXTURES / "aaai_paper_sample.html").read_text()
    abstract = parse_paper_abstract(html)
    assert isinstance(abstract, str)
    assert len(abstract) > 100
    # Should not include the "Abstract" heading prefix
    assert not abstract.lower().startswith("abstract")
