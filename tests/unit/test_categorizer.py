"""Tests for report.utils.categorizer module"""
import pytest

from report.utils.categorizer import (
    categorize_commit,
    group_commits_by_component,
    ComponentType,
)


class TestCategorizeCommit:
    """Test categorize_commit function"""
    
    def test_categorize_console_commits(self):
        console_messages = [
            "feat: Add console UI component",
            "fix: Update ui-block styling",
            "style: Improve button component",
            "feat: Add React modal dialog",
            "fix: Fix frontend layout issue",
        ]
        
        for msg in console_messages:
            assert categorize_commit(msg) == "Console"
    
    def test_categorize_server_commits(self):
        server_messages = [
            "feat: Add server API endpoint",
            "fix: Fix nestcore service",
            "refactor: Update backend controller",
            "feat: Add database migration",
            "fix: Fix API endpoint bug",
        ]
        
        for msg in server_messages:
            assert categorize_commit(msg) == "Server"
    
    def test_categorize_others_commits(self):
        other_messages = [
            "docs: Update README",
            "chore: Update dependencies",
            "ci: Add GitHub Actions workflow",
            "test: Add unit tests",
        ]
        
        for msg in other_messages:
            assert categorize_commit(msg) == "Others"
    
    def test_categorize_case_insensitive(self):
        assert categorize_commit("CONSOLE: Update UI") == "Console"
        assert categorize_commit("SERVER: Update API") == "Server"
        assert categorize_commit("Frontend Update") == "Console"
        assert categorize_commit("BACKEND Update") == "Server"
    
    def test_categorize_mixed_keywords(self):
        # When multiple keywords present, first match wins
        assert categorize_commit("console and server update") == "Console"
    
    def test_categorize_partial_match(self):
        assert categorize_commit("Add console-related feature") == "Console"
        assert categorize_commit("Update server-side logic") == "Server"


class TestGroupCommitsByComponent:
    """Test group_commits_by_component function"""
    
    def test_group_empty_list(self):
        result = group_commits_by_component([])
        
        assert result == {
            "Console": [],
            "Server": [],
            "Others": [],
        }
    
    def test_group_single_commit(self):
        commits = ["feat: Add console UI"]
        result = group_commits_by_component(commits)
        
        assert result["Console"] == ["feat: Add console UI"]
        assert result["Server"] == []
        assert result["Others"] == []
    
    def test_group_multiple_commits(self):
        commits = [
            "feat: Add console UI",
            "fix: Fix server API",
            "docs: Update README",
            "style: Update button",
            "refactor: Refactor backend",
        ]
        
        result = group_commits_by_component(commits)
        
        assert len(result["Console"]) == 2
        assert len(result["Server"]) == 2
        assert len(result["Others"]) == 1
        
        assert "feat: Add console UI" in result["Console"]
        assert "fix: Fix server API" in result["Server"]
        assert "docs: Update README" in result["Others"]
    
    def test_group_preserves_order(self):
        commits = [
            "feat: Console feature 1",
            "feat: Console feature 2",
            "feat: Console feature 3",
        ]
        
        result = group_commits_by_component(commits)
        
        assert result["Console"] == commits
    
    def test_group_all_categories(self):
        commits = [
            "ui: Update console",
            "api: Update server",
            "docs: Update docs",
        ]
        
        result = group_commits_by_component(commits)
        
        assert len(result) == 3
        assert all(key in result for key in ["Console", "Server", "Others"])


class TestComponentType:
    """Test ComponentType type alias"""
    
    def test_component_type_values(self):
        # Ensure the type can hold the expected values
        console: ComponentType = "Console"
        server: ComponentType = "Server"
        others: ComponentType = "Others"
        
        assert console == "Console"
        assert server == "Server"
        assert others == "Others"
