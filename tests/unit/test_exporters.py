"""Tests for report.utils.exporters module"""
import json
import pytest

from report.git.commits import CommitInfo
from report.utils.exporters import (
    export_to_json,
    export_to_markdown,
    export_to_html,
    export_to_email,
    export_commits,
)


@pytest.fixture
def sample_commits_for_export():
    """Sample commits for testing exporters"""
    return [
        CommitInfo(
            hash="abc1234",
            author="John Doe",
            date="2024-01-10 10:00",
            message="feat: Add new feature",
        ),
        CommitInfo(
            hash="def5678",
            author="Jane Smith",
            date="2024-01-10 11:00",
            message="fix: Fix bug",
        ),
    ]


class TestExportToJson:
    """Test export_to_json function"""
    
    def test_export_to_json_structure(self, sample_commits_for_export):
        result = export_to_json(sample_commits_for_export)
        
        data = json.loads(result)
        
        assert "metadata" in data
        assert "commits" in data
        assert "total_commits" in data
        assert "exported_at" in data
        
        assert data["total_commits"] == 2
        assert len(data["commits"]) == 2
    
    def test_export_to_json_commit_fields(self, sample_commits_for_export):
        result = export_to_json(sample_commits_for_export)
        data = json.loads(result)
        
        commit = data["commits"][0]
        assert "hash" in commit
        assert "author" in commit
        assert "date" in commit
        assert "message" in commit
        
        assert commit["hash"] == "abc1234"
        assert commit["author"] == "John Doe"
    
    def test_export_to_json_with_metadata(self, sample_commits_for_export):
        metadata = {
            "title": "Daily Report",
            "date_range": "2024-01-10",
            "author": "John Doe",
        }
        
        result = export_to_json(sample_commits_for_export, metadata)
        data = json.loads(result)
        
        assert data["metadata"]["title"] == "Daily Report"
        assert data["metadata"]["date_range"] == "2024-01-10"
    
    def test_export_to_json_empty_commits(self):
        result = export_to_json([])
        data = json.loads(result)
        
        assert data["total_commits"] == 0
        assert data["commits"] == []


class TestExportToMarkdown:
    """Test export_to_markdown function"""
    
    def test_export_to_markdown_structure(self, sample_commits_for_export):
        result = export_to_markdown(sample_commits_for_export)
        
        assert "# Git Commit Report" in result
        assert "**Total Commits:** 2" in result
        assert "| Hash | Author | Date | Message |" in result
        assert "|------|--------|------|---------|" in result
    
    def test_export_to_markdown_with_metadata(self, sample_commits_for_export):
        metadata = {
            "title": "Weekly Report",
            "date_range": "2024-01-08 to 2024-01-14",
            "author": "Team Lead",
        }
        
        result = export_to_markdown(sample_commits_for_export, metadata)
        
        assert "# Weekly Report" in result
        assert "**Period:** 2024-01-08 to 2024-01-14" in result
        assert "**Author:** Team Lead" in result
    
    def test_export_to_markdown_grouped(self, sample_commits_for_export):
        grouped = {
            "Console": [sample_commits_for_export[0]],
            "Server": [sample_commits_for_export[1]],
        }
        
        result = export_to_markdown(sample_commits_for_export, None, grouped)
        
        assert "## Console" in result
        assert "## Server" in result
        assert "feat: Add new feature" in result
        assert "fix: Fix bug" in result
    
    def test_export_to_markdown_commit_data(self, sample_commits_for_export):
        result = export_to_markdown(sample_commits_for_export)
        
        assert "abc1234" in result
        assert "John Doe" in result
        assert "2024-01-10 10:00" in result
        assert "feat: Add new feature" in result


class TestExportToHtml:
    """Test export_to_html function"""
    
    def test_export_to_html_structure(self, sample_commits_for_export):
        result = export_to_html(sample_commits_for_export)
        
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "</html>" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "<table>" in result
    
    def test_export_to_html_title(self, sample_commits_for_export):
        result = export_to_html(sample_commits_for_export)
        
        assert "<title>Git Commit Report</title>" in result
        assert "<h1>Git Commit Report</h1>" in result
    
    def test_export_to_html_with_metadata(self, sample_commits_for_export):
        metadata = {
            "title": "Daily Report",
            "date_range": "2024-01-10",
            "author": "John Doe",
        }
        
        result = export_to_html(sample_commits_for_export, metadata)
        
        assert "<title>Daily Report</title>" in result
        assert "<strong>Period:</strong> 2024-01-10" in result
        assert "<strong>Author:</strong> John Doe" in result
    
    def test_export_to_html_styling(self, sample_commits_for_export):
        result = export_to_html(sample_commits_for_export)
        
        assert "<style>" in result
        assert "body {" in result
        assert "table {" in result
    
    def test_export_to_html_commit_data(self, sample_commits_for_export):
        result = export_to_html(sample_commits_for_export)
        
        assert "abc1234" in result
        assert "John Doe" in result
        assert "feat: Add new feature" in result
    
    def test_export_to_html_grouped(self, sample_commits_for_export):
        grouped = {
            "Console": [sample_commits_for_export[0]],
            "Server": [sample_commits_for_export[1]],
        }
        
        result = export_to_html(sample_commits_for_export, None, grouped)
        
        assert "<h2>Console" in result
        assert "<h2>Server" in result


class TestExportToEmail:
    """Test export_to_email function"""
    
    def test_export_to_email_structure(self, sample_commits_for_export):
        result = export_to_email(sample_commits_for_export)
        
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "</html>" in result
        assert "<body" in result
    
    def test_export_to_email_inline_styles(self, sample_commits_for_export):
        result = export_to_email(sample_commits_for_export)
        
        # Email format should use inline styles
        assert "style=" in result
        assert "font-family" in result
    
    def test_export_to_email_with_metadata(self, sample_commits_for_export):
        metadata = {
            "title": "Weekly Team Report",
            "date_range": "2024-01-08 to 2024-01-14",
            "team_members": "5",
        }
        
        result = export_to_email(sample_commits_for_export, metadata)
        
        assert "Weekly Team Report" in result
        assert "2024-01-08 to 2024-01-14" in result
        assert "<strong>Team Members:</strong> 5" in result
    
    def test_export_to_email_grouped(self, sample_commits_for_export):
        grouped = {
            "Console": [sample_commits_for_export[0]],
            "Server": [sample_commits_for_export[1]],
        }
        
        result = export_to_email(sample_commits_for_export, None, grouped)
        
        assert "Console" in result
        assert "Server" in result


class TestExportCommits:
    """Test export_commits dispatcher function"""
    
    def test_export_commits_json(self, sample_commits_for_export):
        result = export_commits(sample_commits_for_export, "json")
        
        data = json.loads(result)
        assert "commits" in data
    
    def test_export_commits_markdown(self, sample_commits_for_export):
        result = export_commits(sample_commits_for_export, "markdown")
        
        assert "# Git Commit Report" in result
    
    def test_export_commits_html(self, sample_commits_for_export):
        result = export_commits(sample_commits_for_export, "html")
        
        assert "<!DOCTYPE html>" in result
    
    def test_export_commits_email(self, sample_commits_for_export):
        result = export_commits(sample_commits_for_export, "email")
        
        assert "<!DOCTYPE html>" in result
        assert "style=" in result
    
    def test_export_commits_invalid_format(self, sample_commits_for_export):
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_commits(sample_commits_for_export, "pdf")  # type: ignore
    
    def test_export_commits_with_all_params(self, sample_commits_for_export):
        metadata = {"title": "Test Report"}
        grouped = {"Console": sample_commits_for_export}
        
        result = export_commits(
            sample_commits_for_export,
            "markdown",
            metadata,
            grouped
        )
        
        assert "Test Report" in result
        assert "Console" in result
