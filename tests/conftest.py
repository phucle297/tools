"""Pytest configuration and fixtures"""
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from git import Repo

from report.git.commits import CommitInfo


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        
        # Configure git user
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
            config.set_value("user", "email", "test@example.com")
        
        # Create initial commit
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Repo\n")
        repo.index.add([str(readme)])
        repo.index.commit("Initial commit")
        
        yield tmpdir, repo


@pytest.fixture
def populated_git_repo(temp_git_repo):
    """Create a git repository with multiple commits"""
    tmpdir, repo = temp_git_repo
    
    commits = []
    base_time = datetime.now() - timedelta(days=7)
    
    # Create commits with different dates
    for i in range(5):
        file_path = Path(tmpdir) / f"file{i}.txt"
        file_path.write_text(f"Content {i}\n")
        repo.index.add([str(file_path)])
        
        # Set commit date - format as git expects (without microseconds)
        commit_date = base_time + timedelta(days=i)
        commit_time = commit_date.strftime("%Y-%m-%d %H:%M:%S")
        
        commit = repo.index.commit(
            f"Commit {i}: Test message",
            author_date=commit_time,
            commit_date=commit_time
        )
        commits.append(commit)
    
    yield tmpdir, repo, commits


@pytest.fixture
def sample_commits():
    """Sample commit data for testing"""
    return [
        CommitInfo(
            hash="abc1234",
            author="John Doe",
            date="2024-01-10 10:00",
            message="feat: Add console UI component",
        ),
        CommitInfo(
            hash="def5678",
            author="Jane Smith",
            date="2024-01-10 11:00",
            message="fix: Fix server API endpoint",
        ),
        CommitInfo(
            hash="ghi9012",
            author="John Doe",
            date="2024-01-10 12:00",
            message="docs: Update README",
        ),
    ]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _set_env
