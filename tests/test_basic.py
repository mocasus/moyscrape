"""Tests run on the deploy host (BF VPS) after pip install -r requirements.txt."""
from moyscrape.core import store, extract


def test_store_roundtrip(tmp_path):
    db = str(tmp_path / "t.db")
    store.save(db, "https://x.com", "x.com", "scrape", "markdown", "hello", {"a": 1})
    import sqlite3
    con = sqlite3.connect(db)
    row = con.execute("SELECT url, content FROM scrapes").fetchone()
    con.close()
    assert row[0] == "https://x.com"
    assert row[1] == "hello"


def test_selectors():
    html = '<h1>Hi</h1><a href="/a">A</a><a href="/b">B</a>'
    out = extract.extract_selectors(html, {"title": "h1::text", "links": "a::href"})
    assert out["title"] == "Hi"
    assert out["links"] == ["/a", "/b"]


def test_markdown():
    html = ("<html><head><title>T</title></head><body>"
            "<article><p>Hello world</p></article></body></html>")
    md = extract.to_markdown(html, "https://x.com")
    assert "Hello world" in md
