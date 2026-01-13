"""Commit message generator - AI summarizer"""

from shared.ai import AICommitSummarizer


def generate_ai_commit_message(diff_content: str) -> str:
    """Generate commit message using AI"""
    try:
        summarizer = AICommitSummarizer()
        return summarizer.summarize([diff_content], "commit")
    except ValueError as e:
        raise ValueError(f"AI generation failed: {e}")
