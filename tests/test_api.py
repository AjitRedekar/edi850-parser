import requests

from api_post import post_order


class FakeResponse:
    """Stands in for requests.Response: only the parts post_order uses."""

    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body
        self.text = str(body)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"[self.status_code] error")

    def json(self):
        return self._body


def test_post_success(monkeypatch):
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append({"url": url, "json": json, "headers": headers})
        return FakeResponse(200, {"ok": True})

    monkeypatch.setattr(requests, "post", fake_post)

    result = post_order("https://example.test/orders", "key-123", {"po_number": "1"})

    assert result is True
    assert len(calls) == 1
    assert calls[0]["headers"]["Authorization"] == "Bearer key-123"
    assert calls[0]["json"] == {"po_number": "1"}


def test_post_server_error_returns_false(monkeypatch):
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append({"url": url, "json": json, "headers": headers})
        return FakeResponse(500, {})

    monkeypatch.setattr(requests, "post", fake_post)

    result = post_order(
        "https://example.fake500test/orders", "key-321", {"po_number": "1"}
    )

    assert result is False
    assert len(calls) == 1
    assert calls[0]["headers"]["Authorization"] == "Bearer key-321"
    assert calls[0]["json"] == {"po_number": "1"}


def test_post_timeout_returns_false(monkeypatch):
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append(
            {"url": url, "json": json, "headers": headers, "timeout": "too_slow"}
        )
        return FakeResponse(404, {})

    monkeypatch.setattr(requests, "post", fake_post)

    result = post_order(
        "https://example.fake500test/orders", "key-321", {"po_number": "1"}
    )

    assert result is False
    assert calls[0]["timeout"] == "too_slow"
    assert len(calls) == 1
    assert calls[0]["headers"]["Authorization"] == "Bearer key-321"
    assert calls[0]["json"] == {"po_number": "1"}
