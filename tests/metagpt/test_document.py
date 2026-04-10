#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/2 21:00
@Author  : alexanderwu
@File    : test_document.py
"""
import json
import tempfile
from pathlib import Path

import pandas as pd

from metagpt.config2 import config
from metagpt.document import Document, Repo
from metagpt.logs import logger


def set_existing_repo(path):
    repo1 = Repo.from_path(path)
    repo1.set("doc/wtf_file.md", "wtf content")
    repo1.set("code/wtf_file.py", "def hello():\n    print('hello')")
    logger.info(repo1)  # check doc


def load_existing_repo(path):
    repo = Repo.from_path(path)
    logger.info(repo)
    logger.info(repo.eda())

    assert repo
    assert repo.get("doc/wtf_file.md").content == "wtf content"
    assert repo.get("code/wtf_file.py").content == "def hello():\n    print('hello')"


def test_repo_set_load():
    repo_path = config.workspace.path / "test_repo"
    set_existing_repo(repo_path)
    load_existing_repo(repo_path)


def test_document_multi_format():
    """Test Document support for Excel, CSV, and JSON formats"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Test Excel format
        excel_path = tmpdir / "test.xlsx"
        doc_excel = Document.from_text("Hello Excel", path=excel_path)
        doc_excel.to_path()
        assert excel_path.exists()
        
        # Read back Excel
        doc_excel_read = Document.from_path(excel_path)
        assert "Hello Excel" in doc_excel_read.content
        
        # Test CSV format
        csv_path = tmpdir / "test.csv"
        doc_csv = Document.from_text("Hello CSV", path=csv_path)
        doc_csv.to_path()
        assert csv_path.exists()
        
        # Read back CSV
        doc_csv_read = Document.from_path(csv_path)
        assert "Hello CSV" in doc_csv_read.content
        
        # Test JSON format
        json_path = tmpdir / "test.json"
        doc_json = Document.from_text("Hello JSON", path=json_path)
        doc_json.to_path()
        assert json_path.exists()
        
        # Read back JSON
        doc_json_read = Document.from_path(json_path)
        assert "Hello JSON" in doc_json_read.content
        
        # Verify JSON structure
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        assert json_data["content"] == "Hello JSON"


def test_document_from_text():
    """Document.from_text creates a Document with the given content."""
    doc = Document.from_text("hello world")
    assert doc.content == "hello world"
    assert doc.path is None

    doc_with_path = Document.from_text("data", path=Path("/tmp/demo.txt"))
    assert doc_with_path.path == Path("/tmp/demo.txt")


def test_document_to_path_no_path_raises():
    """to_path() without a path must raise ValueError."""
    import pytest

    doc = Document.from_text("content")
    with pytest.raises(ValueError):
        doc.to_path()


def test_document_from_path_not_found():
    """from_path() with a missing file must raise FileNotFoundError."""
    import pytest

    with pytest.raises(FileNotFoundError):
        Document.from_path(Path("/nonexistent/file.txt"))


def test_document_persist_roundtrip():
    """persist() writes content to disk; subsequent from_path() recovers it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "note.txt"
        doc = Document.from_text("persist me", path=path)
        doc.persist()
        assert path.exists()
        recovered = Document.from_path(path)
        assert recovered.content == "persist me"


def test_repo_get_missing_returns_none():
    """Repo.get() for a filename that was never added returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.from_path(Path(tmpdir))
        assert repo.get("does_not_exist.md") is None


def test_repo_get_text_documents():
    """get_text_documents() returns docs and codes but not plain assets."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.from_path(Path(tmpdir))
        repo.set("readme.md", "# readme")
        repo.set("main.py", "print('hi')")
        text_docs = repo.get_text_documents()
        names = [d.name for d in text_docs]
        assert any("readme.md" in n for n in names)
        assert any("main.py" in n for n in names)
