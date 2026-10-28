from finder import contacts, to_rows

def test_contacts():
    assert contacts("biz: team@example.com | discord.gg/abc123.") == ["discord.gg/abc123", "team@example.com"]
    assert contacts(None) == []

def test_filter_and_sort():
    streams = [
        {"user_id": "1", "user_login": "a", "user_name": "A", "language": "ar", "viewer_count": 50, "title": "x"},
        {"user_id": "2", "user_login": "b", "user_name": "B", "language": "ar", "viewer_count": 5, "title": "y"},
        {"user_id": "3", "user_login": "c", "user_name": "C", "language": "ar", "viewer_count": 900, "title": "z"},
    ]
    users = {"1": {"description": "mail me: a@example.com"}}
    rows = to_rows(streams, users, 10, 1000)
    assert [r["login"] for r in rows] == ["c", "a"]
    assert rows[1]["contacts_in_bio"] == "a@example.com"
