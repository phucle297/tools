"""Tests for report.ai.summarizer module"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from report.ai.summarizer import AICommitSummarizer


class TestAICommitSummarizer:
    """Test AICommitSummarizer class"""
    
    def test_init_with_api_key(self):
        summarizer = AICommitSummarizer(api_key="test-key")
        assert summarizer.api_key == "test-key"
    
    def test_init_with_env_var(self, mock_env_vars):
        mock_env_vars(GROQ_API_KEY="env-key")
        summarizer = AICommitSummarizer()
        assert summarizer.api_key == "env-key"
    
    def test_init_without_api_key(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            AICommitSummarizer()
    
    def test_init_with_verify_ssl(self):
        summarizer = AICommitSummarizer(api_key="test-key", verify_ssl=False)
        assert summarizer.verify_ssl is False
    
    def test_init_verify_ssl_from_env(self, mock_env_vars):
        mock_env_vars(GROQ_API_KEY="test-key", GROQ_VERIFY_SSL="false")
        summarizer = AICommitSummarizer()
        assert summarizer.verify_ssl is False
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_success(self, mock_post):
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Summary of commits"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        summarizer = AICommitSummarizer(api_key="test-key")
        commits = ["feat: Add feature", "fix: Fix bug"]
        
        result = summarizer.summarize(commits)
        
        assert result == "Summary of commits"
        assert mock_post.called
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_with_grouped_commits(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Grouped summary"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        summarizer = AICommitSummarizer(api_key="test-key")
        commits = ["feat: Add feature", "fix: Fix bug"]
        grouped = {
            "Console": ["feat: Add UI"],
            "Server": ["fix: Fix API"],
        }
        
        result = summarizer.summarize(commits, grouped=grouped)
        
        assert result == "Grouped summary"
        assert mock_post.called
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_api_error(self, mock_post):
        # Mock the post to raise a RequestException
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        summarizer = AICommitSummarizer(api_key="test-key")
        commits = ["feat: Add feature"]
        
        result = summarizer.summarize(commits)
        
        assert isinstance(result, str)
        assert "Error" in result
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_with_report_type(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Weekly summary"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        summarizer = AICommitSummarizer(api_key="test-key")
        commits = ["feat: Add feature"]
        
        result = summarizer.summarize(commits, report_type="weekly")
        
        assert result == "Weekly summary"
        
        # Check that the API was called with correct parameters
        call_args = mock_post.call_args
        assert call_args is not None
        
        # Verify the request includes report type in the prompt
        request_data = call_args[1]["json"]
        assert "messages" in request_data
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_empty_commits(self, mock_post):
        summarizer = AICommitSummarizer(api_key="test-key")
        
        result = summarizer.summarize([])
        
        # Should handle empty commits gracefully
        assert isinstance(result, str)
        # Should not call API for empty commits
        assert not mock_post.called
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_ssl_verification(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Summary"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        summarizer = AICommitSummarizer(api_key="test-key", verify_ssl=False)
        commits = ["feat: Add feature"]
        
        summarizer.summarize(commits)
        
        # Verify SSL verification parameter is passed
        call_args = mock_post.call_args
        assert call_args is not None
        assert call_args[1]["verify"] is False
    
    @patch('report.ai.summarizer.requests.post')
    def test_summarize_timeout(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        summarizer = AICommitSummarizer(api_key="test-key")
        commits = ["feat: Add feature"]
        
        result = summarizer.summarize(commits)
        
        # Should handle timeout gracefully
        assert isinstance(result, str)
        assert "Error" in result
