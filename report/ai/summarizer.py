import os
from typing import Optional

import requests

# Suppress SSL warnings when SSL verification is disabled
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


class AICommitSummarizer:
    """Summarize git commits using Groq API"""

    def __init__(self, api_key: Optional[str] = None, verify_ssl: Optional[bool] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in .env file or environment variable."
            )

        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"  # Fast and free model

        # Allow disabling SSL verification via env var or parameter
        # Set GROQ_VERIFY_SSL=false in .env if you have SSL issues
        if verify_ssl is not None:
            self.verify_ssl = verify_ssl
        else:
            verify_env = os.getenv("GROQ_VERIFY_SSL", "true").lower()
            self.verify_ssl = verify_env not in ("false", "0", "no")

    def summarize(
        self,
        commits: list[str],
        report_type: str = "daily",
        grouped: dict[str, list[str]] | None = None,
    ) -> str:
        """
        Summarize a list of commit messages into a concise report

        Args:
            commits: List of commit messages
            report_type: Type of report ('daily' or 'weekly')
            grouped: Optional grouped commits by component (Console/Server/Others)

        Returns:
            Summarized report text
        """
        if not commits:
            return "No commits to summarize."

        prompt = self._build_prompt(commits, report_type, grouped)

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that summarizes git commit messages into concise, professional reports. Focus on key achievements, features, fixes, and improvements.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                },
                timeout=30,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()
            return summary

        except requests.exceptions.SSLError as e:
            return (
                f"SSL Certificate Error: {str(e)}\n\n"
                "To fix this issue, you can:\n"
                "1. Add 'GROQ_VERIFY_SSL=false' to your .env file (not recommended for production)\n"
                "2. Update your system's SSL certificates\n"
                "3. Check if you're behind a corporate proxy/firewall"
            )
        except requests.exceptions.RequestException as e:
            return f"Error calling Groq API: {str(e)}"

    def _build_prompt(
        self, commits: list[str], report_type: str, grouped: dict[str, list[str]] | None = None
    ) -> str:
        """Build the prompt for the AI model"""
        if grouped:
            # Build prompt with grouped commits
            commits_text = ""
            for component, component_commits in grouped.items():
                if component_commits:
                    commits_text += f"\n## {component}\n"
                    commits_text += "\n".join(f"- {commit}" for commit in component_commits)
                    commits_text += "\n"

            prompt = f"""Please summarize the following {report_type} git commits into a concise report.

The commits are already grouped by component (Console, Server, Others).

For each component:
1. Summarize the main achievements and changes
2. Group by categories (Features, Bug Fixes, Improvements, Refactoring, etc.) if there are many commits
3. Keep it concise and professional

Commits by Component:
{commits_text}

Please provide a clear, professional summary in markdown format, maintaining the Console/Server/Others structure."""
        else:
            # Original prompt for non-grouped commits
            commits_text = "\n".join(f"- {commit}" for commit in commits)
            prompt = f"""Please summarize the following {report_type} git commits into a concise report.

Organize the summary by categories (e.g., Features, Bug Fixes, Improvements, Refactoring, Documentation, etc.).

Commits:
{commits_text}

Please provide a clear, professional summary in markdown format."""

        return prompt
