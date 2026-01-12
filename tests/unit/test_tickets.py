"""Tests for report.utils.tickets module"""
import pytest

from report.git.commits import CommitInfo
from report.utils.tickets import (
    extract_ticket_from_message,
    group_commits_by_ticket,
    format_ticket_summary,
    TicketCommits,
)


class TestExtractTicketFromMessage:
    """Test extract_ticket_from_message function"""
    
    def test_extract_jira_ticket(self):
        assert extract_ticket_from_message("PROJECT-123: Add feature") == "PROJECT-123"
        assert extract_ticket_from_message("Fix bug in PROJECT-456") == "PROJECT-456"
        assert extract_ticket_from_message("[JIRA-789] Update documentation") == "JIRA-789"
    
    def test_extract_github_issue(self):
        assert extract_ticket_from_message("Fix #123: Bug fix") == "123"
        assert extract_ticket_from_message("Closes #456") == "456"
        # GH-789 returns the full match including GH-
        result = extract_ticket_from_message("GH-789: Feature")
        assert result in ["789", "GH-789"]  # Accept either format
    
    def test_extract_linear_ticket(self):
        assert extract_ticket_from_message("LIN-123: Add feature") == "LIN-123"
    
    def test_extract_generic_ticket(self):
        assert extract_ticket_from_message("ticket #123: Fix bug") == "123"
        assert extract_ticket_from_message("issue: 456") == "456"
        assert extract_ticket_from_message("Ticket: #789") == "789"
    
    def test_extract_no_ticket(self):
        assert extract_ticket_from_message("No ticket in this message") is None
        assert extract_ticket_from_message("Just a regular commit message") is None
        assert extract_ticket_from_message("feat: Add new feature") is None
    
    def test_extract_case_insensitive(self):
        assert extract_ticket_from_message("project-123: feature") == "project-123"
        assert extract_ticket_from_message("TICKET #456") == "456"
    
    def test_extract_custom_pattern(self):
        patterns = [r'CUSTOM-(\d+)']
        assert extract_ticket_from_message("CUSTOM-123: Fix", patterns) == "123"


class TestGroupCommitsByTicket:
    """Test group_commits_by_ticket function"""
    
    @pytest.fixture
    def sample_commits_with_tickets(self):
        return [
            CommitInfo("abc1234", "John", "2024-01-10 10:00", "PROJECT-123: Add feature"),
            CommitInfo("def5678", "Jane", "2024-01-10 11:00", "PROJECT-123: Fix bug"),
            CommitInfo("ghi9012", "Bob", "2024-01-10 12:00", "PROJECT-456: New feature"),
            CommitInfo("jkl3456", "Alice", "2024-01-10 13:00", "No ticket here"),
            CommitInfo("mno7890", "John", "2024-01-10 14:00", "Fix #789: Bug fix"),
        ]
    
    def test_group_commits_by_ticket(self, sample_commits_with_tickets):
        grouped, unmatched = group_commits_by_ticket(sample_commits_with_tickets)
        
        assert len(grouped) == 3  # PROJECT-123, PROJECT-456, 789
        assert len(unmatched) == 1
    
    def test_group_commits_ticket_structure(self, sample_commits_with_tickets):
        grouped, unmatched = group_commits_by_ticket(sample_commits_with_tickets)
        
        assert isinstance(grouped[0], TicketCommits)
        assert hasattr(grouped[0], 'ticket_id')
        assert hasattr(grouped[0], 'commits')
    
    def test_group_commits_normalized_ids(self, sample_commits_with_tickets):
        grouped, unmatched = group_commits_by_ticket(sample_commits_with_tickets)
        
        # Ticket IDs should be uppercase
        ticket_ids = [t.ticket_id for t in grouped]
        assert all(tid == tid.upper() for tid in ticket_ids)
    
    def test_group_commits_sorted_by_id(self, sample_commits_with_tickets):
        grouped, unmatched = group_commits_by_ticket(sample_commits_with_tickets)
        
        ticket_ids = [t.ticket_id for t in grouped]
        assert ticket_ids == sorted(ticket_ids)
    
    def test_group_commits_multiple_per_ticket(self, sample_commits_with_tickets):
        grouped, unmatched = group_commits_by_ticket(sample_commits_with_tickets)
        
        # Find PROJECT-123 group
        project_123 = next(t for t in grouped if t.ticket_id == "PROJECT-123")
        assert len(project_123.commits) == 2
    
    def test_group_commits_unmatched(self, sample_commits_with_tickets):
        grouped, unmatched = group_commits_by_ticket(sample_commits_with_tickets)
        
        assert len(unmatched) == 1
        assert unmatched[0].message == "No ticket here"
    
    def test_group_empty_commits(self):
        grouped, unmatched = group_commits_by_ticket([])
        
        assert grouped == []
        assert unmatched == []
    
    def test_group_with_custom_patterns(self):
        commits = [
            CommitInfo("abc1234", "John", "2024-01-10 10:00", "CUSTOM-123: Feature"),
            CommitInfo("def5678", "Jane", "2024-01-10 11:00", "Regular commit"),
        ]
        
        patterns = [r'CUSTOM-(\d+)']
        grouped, unmatched = group_commits_by_ticket(commits, patterns)
        
        assert len(grouped) == 1
        assert grouped[0].ticket_id == "123"
        assert len(unmatched) == 1


class TestFormatTicketSummary:
    """Test format_ticket_summary function"""
    
    def test_format_empty_tickets(self):
        result = format_ticket_summary([])
        
        assert "No tickets found" in result
    
    def test_format_single_ticket(self):
        tickets = [
            TicketCommits(
                ticket_id="PROJECT-123",
                commits=[
                    CommitInfo("abc1234", "John", "2024-01-10 10:00", "Add feature"),
                ]
            )
        ]
        
        result = format_ticket_summary(tickets)
        
        assert "PROJECT-123" in result
        assert "1 commits" in result
        assert "Add feature" in result
    
    def test_format_multiple_tickets(self):
        tickets = [
            TicketCommits(
                ticket_id="PROJECT-123",
                commits=[
                    CommitInfo("abc1234", "John", "2024-01-10 10:00", "Feature 1"),
                    CommitInfo("def5678", "Jane", "2024-01-10 11:00", "Feature 2"),
                ]
            ),
            TicketCommits(
                ticket_id="PROJECT-456",
                commits=[
                    CommitInfo("ghi9012", "Bob", "2024-01-10 12:00", "Bug fix"),
                ]
            ),
        ]
        
        result = format_ticket_summary(tickets)
        
        assert "PROJECT-123" in result
        assert "2 commits" in result
        assert "PROJECT-456" in result
        assert "1 commits" in result
    
    def test_format_includes_emoji(self):
        tickets = [
            TicketCommits(
                ticket_id="TEST-1",
                commits=[
                    CommitInfo("abc1234", "John", "2024-01-10 10:00", "Test"),
                ]
            )
        ]
        
        result = format_ticket_summary(tickets)
        
        assert "📋" in result


class TestTicketCommits:
    """Test TicketCommits named tuple"""
    
    def test_ticket_commits_creation(self):
        commits = [
            CommitInfo("abc1234", "John", "2024-01-10 10:00", "Test commit"),
        ]
        
        ticket = TicketCommits(ticket_id="PROJECT-123", commits=commits)
        
        assert ticket.ticket_id == "PROJECT-123"
        assert ticket.commits == commits
        assert len(ticket.commits) == 1
