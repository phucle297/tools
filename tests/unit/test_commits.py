"""Tests for report.git.commits module"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from git import InvalidGitRepositoryError
from report.git.commits import (
    CommitInfo,
    get_commits,
    get_commits_detailed,
    get_all_authors,
    get_commits_from_multiple_repos,
    discover_repos_in_directory,
)


class TestCommitInfo:
    """Test CommitInfo named tuple"""
    
    def test_commit_info_creation(self):
        commit = CommitInfo(
            hash="abc1234",
            author="Test User",
            date="2024-01-10 10:00",
            message="Test commit",
        )
        assert commit.hash == "abc1234"
        assert commit.author == "Test User"
        assert commit.date == "2024-01-10 10:00"
        assert commit.message == "Test commit"
        assert commit.repo == "."  # Default value
    
    def test_commit_info_with_repo(self):
        commit = CommitInfo(
            hash="abc1234",
            author="Test User",
            date="2024-01-10 10:00",
            message="Test commit",
            repo="my-repo",
        )
        assert commit.repo == "my-repo"


class TestGetCommits:
    """Test get_commits function"""
    
    def test_get_commits_returns_messages(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        messages = get_commits(tmpdir, since, until)
        
        assert isinstance(messages, list)
        assert len(messages) > 0
        assert all(isinstance(msg, str) for msg in messages)
    
    def test_get_commits_invalid_repo(self, tmp_path):
        with pytest.raises(RuntimeError, match="Not a git repository"):
            since = datetime.now() - timedelta(days=1)
            until = datetime.now()
            get_commits(str(tmp_path), since, until)


class TestGetCommitsDetailed:
    """Test get_commits_detailed function"""
    
    def test_get_commits_detailed_structure(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        detailed = get_commits_detailed(tmpdir, since, until)
        
        assert isinstance(detailed, list)
        assert len(detailed) > 0
        
        for commit in detailed:
            assert isinstance(commit, CommitInfo)
            assert len(commit.hash) == 7  # Short hash
            assert commit.author
            assert commit.date
            assert commit.message
    
    def test_get_commits_detailed_date_range(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        # Get commits from middle of range
        since = datetime.now() - timedelta(days=5)
        until = datetime.now() - timedelta(days=3)
        
        detailed = get_commits_detailed(tmpdir, since, until)
        
        # Should get some but not all commits
        assert len(detailed) < len(commits)
    
    def test_get_commits_detailed_author_filter_me(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        # Filter by "me" (current git user)
        detailed = get_commits_detailed(tmpdir, since, until, author="me")
        
        assert isinstance(detailed, list)
        # All commits should be from "Test User"
        for commit in detailed:
            assert commit.author == "Test User"
    
    def test_get_commits_detailed_author_filter_name(self, temp_git_repo):
        tmpdir, repo = temp_git_repo
        
        # Create commits with different authors
        file1 = Path(tmpdir) / "file1.txt"
        file1.write_text("Content 1")
        repo.index.add([str(file1)])
        
        # Change author for this commit
        with repo.config_writer() as config:
            config.set_value("user", "name", "Alice")
        
        repo.index.commit("Alice's commit")
        
        # Change back to Test User
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
        
        file2 = Path(tmpdir) / "file2.txt"
        file2.write_text("Content 2")
        repo.index.add([str(file2)])
        repo.index.commit("Test User's commit")
        
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        
        # Filter by Alice
        alice_commits = get_commits_detailed(tmpdir, since, until, author="alice")
        assert all("Alice" in c.author for c in alice_commits)
    
    def test_get_commits_detailed_no_merges(self, temp_git_repo):
        tmpdir, repo = temp_git_repo
        
        # Create a simple commit
        file1 = Path(tmpdir) / "test.txt"
        file1.write_text("Test")
        repo.index.add([str(file1)])
        repo.index.commit("Regular commit")
        
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        
        commits = get_commits_detailed(tmpdir, since, until)
        
        # Should not include merge commits (filtered by no_merges=True)
        assert len(commits) >= 1


class TestGetAllAuthors:
    """Test get_all_authors function"""
    
    def test_get_all_authors(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        authors = get_all_authors(tmpdir)
        
        assert isinstance(authors, list)
        assert len(authors) > 0
        assert "Test User" in authors
        assert authors == sorted(authors)  # Should be sorted
    
    def test_get_all_authors_with_date_range(self, populated_git_repo):
        tmpdir, repo, commits = populated_git_repo
        
        since = datetime.now() - timedelta(days=5)
        until = datetime.now()
        
        authors = get_all_authors(tmpdir, since=since, until=until)
        
        assert isinstance(authors, list)
        assert len(authors) >= 1
    
    def test_get_all_authors_invalid_repo(self, tmp_path):
        with pytest.raises(RuntimeError, match="Not a git repository"):
            get_all_authors(str(tmp_path))


class TestGetCommitsFromMultipleRepos:
    """Test get_commits_from_multiple_repos function"""
    
    def test_multiple_repos(self, populated_git_repo, temp_git_repo):
        tmpdir1, repo1, commits1 = populated_git_repo
        tmpdir2, repo2 = temp_git_repo
        
        # Add commit to second repo
        file = Path(tmpdir2) / "test.txt"
        file.write_text("Test")
        repo2.index.add([str(file)])
        repo2.index.commit("Second repo commit")
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        all_commits = get_commits_from_multiple_repos(
            [tmpdir1, tmpdir2], since, until
        )
        
        assert len(all_commits) > 0
        # Should have commits from both repos
        repos = set(c.repo for c in all_commits)
        assert len(repos) >= 1
    
    def test_multiple_repos_with_invalid(self, populated_git_repo, tmp_path):
        tmpdir1, repo1, commits1 = populated_git_repo
        invalid_path = str(tmp_path / "invalid")
        
        since = datetime.now() - timedelta(days=8)
        until = datetime.now()
        
        # Should skip invalid repos without crashing
        all_commits = get_commits_from_multiple_repos(
            [tmpdir1, invalid_path], since, until
        )
        
        assert len(all_commits) > 0


class TestDiscoverReposInDirectory:
    """Test discover_repos_in_directory function"""
    
    def test_discover_single_repo(self, temp_git_repo):
        tmpdir, repo = temp_git_repo
        parent = Path(tmpdir).parent
        
        repos = discover_repos_in_directory(str(parent))
        
        assert tmpdir in repos
    
    def test_discover_multiple_repos(self, tmp_path):
        # Create multiple repos in subdirectories
        from git import Repo as GitRepo
        
        repo1_path = tmp_path / "repo1"
        repo2_path = tmp_path / "repo2"
        
        repo1_path.mkdir()
        repo2_path.mkdir()
        
        GitRepo.init(str(repo1_path))
        GitRepo.init(str(repo2_path))
        
        repos = discover_repos_in_directory(str(tmp_path))
        
        assert len(repos) >= 2
        assert any("repo1" in r for r in repos)
        assert any("repo2" in r for r in repos)
    
    def test_discover_with_depth_limit(self, tmp_path):
        # Create nested repos
        from git import Repo as GitRepo
        
        deep_path = tmp_path / "level1" / "level2" / "level3"
        deep_path.mkdir(parents=True)
        GitRepo.init(str(deep_path))
        
        # Should not find deeply nested repo with max_depth=1
        repos = discover_repos_in_directory(str(tmp_path), max_depth=1)
        
        assert not any("level3" in r for r in repos)
