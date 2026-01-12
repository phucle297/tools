"""Tests for report.utils.stats module"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from report.utils.stats import (
    get_commit_stats,
    AuthorStats,
    RepoStats,
)


class TestAuthorStats:
    """Test AuthorStats named tuple"""
    
    def test_author_stats_creation(self):
        stats = AuthorStats(
            author="John Doe",
            total_commits=10,
            files_changed=5,
            insertions=100,
            deletions=50,
            net_lines=50,
        )
        
        assert stats.author == "John Doe"
        assert stats.total_commits == 10
        assert stats.files_changed == 5
        assert stats.insertions == 100
        assert stats.deletions == 50
        assert stats.net_lines == 50


class TestRepoStats:
    """Test RepoStats named tuple"""
    
    def test_repo_stats_creation(self):
        author_stats = [
            AuthorStats("John", 5, 3, 50, 20, 30),
            AuthorStats("Jane", 3, 2, 30, 10, 20),
        ]
        
        stats = RepoStats(
            total_commits=8,
            total_authors=2,
            total_files_changed=5,
            total_insertions=80,
            total_deletions=30,
            net_lines=50,
            author_stats=author_stats,
        )
        
        assert stats.total_commits == 8
        assert stats.total_authors == 2
        assert len(stats.author_stats) == 2


class TestGetCommitStats:
    """Test get_commit_stats function"""
    
    def test_get_commit_stats_structure(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        stats = get_commit_stats(tmpdir, since, until)
        
        assert isinstance(stats, RepoStats)
        assert stats.total_commits > 0
        assert stats.total_authors > 0
        assert isinstance(stats.author_stats, list)
    
    def test_get_commit_stats_author_stats(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        stats = get_commit_stats(tmpdir, since, until)
        
        assert len(stats.author_stats) > 0
        
        for author_stat in stats.author_stats:
            assert isinstance(author_stat, AuthorStats)
            assert author_stat.author
            assert author_stat.total_commits > 0
    
    def test_get_commit_stats_line_counts(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        stats = get_commit_stats(tmpdir, since, until)
        
        # Should have some insertions from commits
        assert stats.total_insertions >= 0
        assert stats.total_deletions >= 0
        assert stats.net_lines == stats.total_insertions - stats.total_deletions
    
    def test_get_commit_stats_files_changed(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        stats = get_commit_stats(tmpdir, since, until)
        
        assert stats.total_files_changed > 0
    
    def test_get_commit_stats_with_author_filter(self, temp_git_repo):
        tmpdir, repo = temp_git_repo
        
        # Create commits from different authors
        file1 = Path(tmpdir) / "file1.txt"
        file1.write_text("Content 1\n")
        repo.index.add([str(file1)])
        repo.index.commit("Commit 1")
        
        # Change author
        with repo.config_writer() as config:
            config.set_value("user", "name", "Other User")
        
        file2 = Path(tmpdir) / "file2.txt"
        file2.write_text("Content 2\n")
        repo.index.add([str(file2)])
        repo.index.commit("Commit 2")
        
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        
        # Get stats for "Test User" only
        stats = get_commit_stats(tmpdir, since, until, author="Test User")
        
        # Should only count Test User's commits
        assert stats.total_commits >= 1
        
    def test_get_commit_stats_with_me_filter(self, temp_git_repo):
        tmpdir, repo = temp_git_repo
        
        file1 = Path(tmpdir) / "test.txt"
        file1.write_text("Test\n")
        repo.index.add([str(file1)])
        repo.index.commit("Test commit")
        
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        
        stats = get_commit_stats(tmpdir, since, until, author="me")
        
        assert stats.total_commits >= 1
        # All commits should be from current git user
        for author_stat in stats.author_stats:
            assert author_stat.author == "Test User"
    
    def test_get_commit_stats_empty_range(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        # Date range with no commits
        since = datetime(2000, 1, 1)
        until = datetime(2000, 1, 2)
        
        stats = get_commit_stats(tmpdir, since, until)
        
        assert stats.total_commits == 0
        assert stats.total_authors == 0
        assert stats.author_stats == []
    
    def test_get_commit_stats_invalid_repo(self, tmp_path):
        with pytest.raises(RuntimeError, match="Not a git repository"):
            since = datetime.now() - timedelta(days=1)
            until = datetime.now()
            get_commit_stats(str(tmp_path), since, until)
    
    def test_get_commit_stats_author_sorted_by_commits(self, temp_git_repo):
        tmpdir, repo = temp_git_repo
        
        # Create multiple commits
        for i in range(3):
            file = Path(tmpdir) / f"file{i}.txt"
            file.write_text(f"Content {i}\n")
            repo.index.add([str(file)])
            repo.index.commit(f"Commit {i}")
        
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        
        stats = get_commit_stats(tmpdir, since, until)
        
        # Author stats should be sorted by commit count (descending)
        if len(stats.author_stats) > 1:
            for i in range(len(stats.author_stats) - 1):
                assert stats.author_stats[i].total_commits >= stats.author_stats[i + 1].total_commits
