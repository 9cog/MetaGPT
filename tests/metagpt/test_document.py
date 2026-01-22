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
