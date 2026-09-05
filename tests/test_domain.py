from notebook_app.domain import append_exchange, page_title


def test_page_title_prefers_h1() -> None:
    assert page_title("research/copy.md", "# Copy containment\n\nText") == "Copy containment"


def test_page_title_falls_back_to_filename() -> None:
    assert page_title("research/copy-containment.md", "Text") == "Copy Containment"


def test_append_exchange_is_plain_markdown() -> None:
    result = append_exchange("# Parser", "Alex", "Try option 2", "It is cleaner.")
    assert result == (
        "# Parser\n\n---\n\n### Alex\n\nTry option 2\n\n### AI\n\nIt is cleaner.\n"
    )
