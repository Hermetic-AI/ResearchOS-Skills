"""Tests for paper-writing-assistant/scripts/online_verification.py — online
DOI / journal metadata verification via Crossref.

Uses a local HTTP server (stdlib http.server in a daemon thread) to mock the
Crossref API, so no real network access is required. Also tests the
"network unavailable" path by pointing at a port nothing is listening on.

Covers:
1. Mocked Crossref response -> match/mismatch detection.
2. Network unavailable -> "unavailable" status, no crash.
3. DOI not found in Crossref -> reported clearly.
4. Field mismatch (e.g., year differs) -> reported with details.
"""
from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "paper-writing-assistant" / "scripts" / "online_verification.py"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def load_module():
    spec = importlib.util.spec_from_file_location("researchos_online_verification", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=ENV, timeout=30, check=False,
    )


# ---------------------------------------------------------- Crossref mock server


def make_handler_class(responses: dict):
    """Build a handler that maps path -> (status, body) from ``responses``."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silence stderr
            pass

        def do_GET(self):
            # self.path is like /works/10.1234/abc?...  The DOI segment is
            # URL-encoded by urllib.parse.quote(doi, safe=""), so unquote it
            # before matching against the response map.
            raw_path = self.path.split("?")[0]
            path = urllib.parse.unquote(raw_path)
            if path in responses:
                status, body = responses[path]
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body.encode("utf-8") if isinstance(body, str)
                                 else body)
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"error","message":"not found"}')

    return Handler


class MockServer:
    def __init__(self, responses: dict):
        self.responses = responses
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0
        self.base_url = ""

    def __enter__(self):
        handler = make_handler_class(self.responses)
        self._server = HTTPServer(("127.0.0.1", 0), handler)
        self.port = self._server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True)
        self._thread.start()
        # wait briefly until the server accepts connections
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.1):
                    break
            except OSError:
                time.sleep(0.01)
        return self

    def __exit__(self, *exc):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()


def crossref_found_response(**overrides) -> dict:
    message = {
        "DOI": "10.1234/example",
        "title": ["An Example Paper Title"],
        "container-title": ["Journal of Examples"],
        "short-container-title": ["J. Examples"],
        "published-print": {"date-parts": [[2024]]},
        "page": "100-120",
        "author": [
            {"given": "Jane", "family": "Doe"},
            {"given": "John", "family": "Smith"},
        ],
        "type": "journal-article",
    }
    # Keys with hyphens (e.g. "published-print") cannot be passed as Python
    # keyword arguments, so callers use underscores and we translate here.
    translated = {}
    for key, value in overrides.items():
        translated[key.replace("_", "-")] = value
    message.update(translated)
    return {"status": "ok", "message": message}


# ---------------------------------------------------------- helpers

def _patch_urlopen(monkeypatch, responses: dict):
    """Patch urllib.request.urlopen so that requests to the mock server's base
    URL are served from ``responses`` (path -> (status, body))."""
    import urllib.request as ureq
    import io

    def fake_urlopen(request, timeout=None):
        url = request.full_url if hasattr(request, "full_url") else request
        path = url.split("?")[0]
        # strip scheme+host to get the /works/... path
        idx = path.find("/works/")
        key = path[idx:] if idx >= 0 else path
        if key in responses:
            status, body = responses[key]
            if status == 404:
                raise ureq.HTTPError(url, 404, "Not Found", {}, None)  # type: ignore[arg-type]
            if status == 500:
                raise ureq.HTTPError(url, 500, "Server Error", {}, None)  # type: ignore[arg-type]
            data = body.encode("utf-8") if isinstance(body, str) else body
            return io.BytesIO(data)  # type: ignore[return-value]
        raise ureq.URLError("connection refused")

    monkeypatch.setattr(ureq, "urlopen", fake_urlopen)


# ---------------------------------------------------------- tests

def _parsed_remote(overrides=None) -> dict:
    """Build a Crossref-parsed remote record (the shape returned by
    ``_parse_crossref_message``) for unit comparisons."""
    message = crossref_found_response(**(overrides or {}))
    mod = load_module()
    return mod._parse_crossref_message(message["message"])


def test_unit_match_detection():
    module = load_module()
    local = {
        "title": "An Example Paper Title",
        "author": "Doe, Jane and Smith, John",
        "year": "2024",
        "journal": "Journal of Examples",
        "pages": "100-120",
        "doi": "10.1234/example",
    }
    remote = _parsed_remote()
    comparison = module.compare_fields(local, remote)
    assert comparison["overall"] == "match"
    assert comparison["mismatch_count"] == 0
    assert comparison["fields"]["title"]["status"] == "match"
    assert comparison["fields"]["year"]["status"] == "match"
    assert comparison["fields"]["journal"]["status"] == "match"
    assert comparison["fields"]["pages"]["status"] == "match"
    assert comparison["fields"]["authors"]["status"] == "match"


def test_unit_year_mismatch_detected():
    module = load_module()
    local = {
        "title": "An Example Paper Title",
        "author": "Doe, Jane",
        "year": "2023",  # differs from remote 2024
        "journal": "Journal of Examples",
        "pages": "100-120",
        "doi": "10.1234/example",
    }
    remote = _parsed_remote()
    comparison = module.compare_fields(local, remote)
    assert comparison["overall"] == "mismatch"
    assert comparison["mismatch_count"] >= 1
    assert comparison["fields"]["year"]["status"] == "mismatch"
    assert comparison["fields"]["year"]["local"] == 2023
    assert comparison["fields"]["year"]["remote"] == 2024


def test_unit_title_mismatch_detected():
    module = load_module()
    local = {
        "title": "A Completely Different Title",
        "author": "Doe, Jane",
        "year": "2024",
        "journal": "Journal of Examples",
        "pages": "100-120",
        "doi": "10.1234/example",
    }
    remote = _parsed_remote()
    comparison = module.compare_fields(local, remote)
    assert comparison["fields"]["title"]["status"] == "mismatch"
    assert comparison["fields"]["title"]["confidence"] < 0.8


def test_unit_invalid_doi_rejected(monkeypatch):
    module = load_module()
    result = module.verify_doi("not-a-doi", 5.0, 1, "test-agent")
    assert result["doi_syntax_valid"] is False
    assert result["status"] == "invalid-syntax"


def test_unit_network_unavailable(monkeypatch):
    module = load_module()
    import urllib.request as ureq

    def raise_urlerror(*args, **kwargs):
        raise ureq.URLError("network is unreachable")

    monkeypatch.setattr(ureq, "urlopen", raise_urlerror)
    result = module.verify_doi("10.1234/example", 5.0, 1, "test-agent")
    assert result["status"] == "unavailable"
    assert result["crossref"]["status"] == "unavailable"


def test_unit_doi_not_found(monkeypatch):
    module = load_module()
    import urllib.request as ureq

    def raise_404(*args, **kwargs):
        raise ureq.HTTPError("http://x", 404, "Not Found", {}, None)  # type: ignore[arg-type]

    monkeypatch.setattr(ureq, "urlopen", raise_404)
    result = module.verify_doi("10.1234/missing", 5.0, 1, "test-agent")
    assert result["status"] == "not-found"
    assert result["crossref"]["status"] == "not-found"


def test_unit_bibtex_parsing():
    module = load_module()
    bib = (
        "@article{Doe2024,\n"
        "  title = {An Example Paper Title},\n"
        "  author = {Doe, Jane and Smith, John},\n"
        "  year = 2024,\n"
        "  journal = {Journal of Examples},\n"
        "  pages = {100-120},\n"
        "  doi = {10.1234/example}\n"
        "}\n"
    )
    records = module.parse_bib_dois.__wrapped__ if hasattr(module.parse_bib_dois, "__wrapped__") else None
    # call via a temp file
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".bib", delete=False,
                                     encoding="utf-8") as f:
        f.write(bib)
        path = Path(f.name)
    try:
        parsed = module.parse_bib_dois(path)
    finally:
        path.unlink()
    assert len(parsed) == 1
    rec = parsed[0]
    assert rec["key"] == "Doe2024"
    assert rec["doi"] == "10.1234/example"
    assert rec["doi_syntax_valid"] is True
    assert rec["year"] == "2024"
    assert rec["journal"] == "Journal of Examples"


# ---------------------------------------------------------- CLI tests

def test_cli_doi_match_via_mock_server(tmp_path):
    body = json.dumps(crossref_found_response())
    with MockServer({"/works/10.1234/example": (200, body)}) as srv:
        # Patch the module constant via env is not possible; instead, call the
        # module directly through a small wrapper that overrides CROSSREF_WORKS.
        mod = load_module()
        original = mod.CROSSREF_WORKS
        mod.CROSSREF_WORKS = srv.base_url + "/works/"
        try:
            result = mod.verify_doi("10.1234/example", 5.0, 1, "test-agent")
        finally:
            mod.CROSSREF_WORKS = original
    assert result["status"] == "found"
    assert result["crossref"]["title"] == "An Example Paper Title"
    assert result["crossref"]["year"] == 2024


def test_cli_doi_mismatch_via_mock_server(tmp_path):
    body = json.dumps(crossref_found_response(published_print={"date-parts": [[2022]]}))
    mod = load_module()
    with MockServer({"/works/10.1234/example": (200, body)}) as srv:
        original = mod.CROSSREF_WORKS
        mod.CROSSREF_WORKS = srv.base_url + "/works/"
        try:
            remote = mod.fetch_crossref("10.1234/example", 5.0, 1, "test-agent")
        finally:
            mod.CROSSREF_WORKS = original
    local = {
        "title": "An Example Paper Title",
        "author": "Doe, Jane",
        "year": "2024",
        "journal": "Journal of Examples",
        "pages": "100-120",
        "doi": "10.1234/example",
    }
    comparison = mod.compare_fields(local, remote)
    assert comparison["fields"]["year"]["status"] == "mismatch"
    assert comparison["fields"]["year"]["local"] == 2024
    assert comparison["fields"]["year"]["remote"] == 2022


def test_cli_doi_not_found_via_mock_server(tmp_path):
    mod = load_module()
    with MockServer({}) as srv:  # empty -> 404 for everything
        original = mod.CROSSREF_WORKS
        mod.CROSSREF_WORKS = srv.base_url + "/works/"
        try:
            result = mod.verify_doi("10.1234/missing", 5.0, 1, "test-agent")
        finally:
            mod.CROSSREF_WORKS = original
    assert result["status"] == "not-found"


def test_cli_network_unavailable_via_dead_port(tmp_path):
    mod = load_module()
    # Bind then immediately close a socket to get a free port nobody listens on
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    original = mod.CROSSREF_WORKS
    mod.CROSSREF_WORKS = base + "/works/"
    try:
        result = mod.verify_doi("10.1234/example", 2.0, 1, "test-agent")
    finally:
        mod.CROSSREF_WORKS = original
    assert result["status"] == "unavailable"


def test_cli_bibtex_batch_via_mock_server(tmp_path):
    body = json.dumps(crossref_found_response())
    bib = tmp_path / "refs.bib"
    bib.write_text(
        "@article{Doe2024,\n"
        "  title = {An Example Paper Title},\n"
        "  author = {Doe, Jane},\n"
        "  year = 2024,\n"
        "  journal = {Journal of Examples},\n"
        "  pages = {100-120},\n"
        "  doi = {10.1234/example}\n"
        "}\n"
        "@article{NoDoi2023,\n"
        "  title = {No DOI Here},\n"
        "  author = {Lee, A.},\n"
        "  year = 2023\n"
        "}\n",
        encoding="utf-8",
    )
    mod = load_module()
    with MockServer({"/works/10.1234/example": (200, body)}) as srv:
        original = mod.CROSSREF_WORKS
        mod.CROSSREF_WORKS = srv.base_url + "/works/"
        try:
            report = mod.verify_bib(bib, 5.0, 1, "test-agent")
        finally:
            mod.CROSSREF_WORKS = original
    assert report["source"] == str(bib)
    assert len(report["records"]) == 2
    doi_record = next(r for r in report["records"] if r["key"] == "Doe2024")
    assert doi_record["status"] == "found"
    assert doi_record["comparison"]["overall"] == "match"
    nodoi_record = next(r for r in report["records"] if r["key"] == "NoDoi2023")
    assert nodoi_record["status"] == "no-doi"


def test_cli_version_flag():
    result = run_cli("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_requires_doi_or_bibtex():
    result = run_cli()
    assert result.returncode != 0
    assert "--doi" in result.stderr or "required" in result.stderr


def test_cli_output_protected(tmp_path):
    out = tmp_path / "report.json"
    out.write_text("sentinel", encoding="utf-8")
    result = run_cli("--doi", "10.1234/example", "--out", str(out))
    assert result.returncode != 0
    assert out.read_text(encoding="utf-8") == "sentinel"


def test_cli_output_never_replaces_bibtex(tmp_path):
    bib = tmp_path / "refs.bib"
    bib.write_text("@article{x, title={T}, doi={10.1234/x}}\n", encoding="utf-8")
    result = run_cli("--bibtex", str(bib), "--out", str(bib), "--force")
    assert result.returncode != 0
    assert "must not replace" in result.stderr.lower() or "source" in result.stderr.lower()
