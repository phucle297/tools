"""AI-powered commit summarizer"""

import os
from typing import Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AICommitSummarizer:
    def __init__(self, api_key: Optional[str] = None, verify_ssl: Optional[bool] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in .env file or environment variable."
            )

        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"

        if verify_ssl is not None:
            self.verify_ssl = verify_ssl
        else:
            verify_env = os.getenv("GROQ_VERIFY_SSL", "true").lower()
            self.verify_ssl = verify_env not in ("false", "0", "no")

    def summarize(
        self,
        commits: list[str],
        report_type: str = "daily",
        grouped: Optional[dict[str, list[str]]] = None,
    ) -> str:
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
                            "content": "You are a helpful assistant that summarizes git commit messages into concise, professional reports.",
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
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.SSLError as e:
            return f"SSL Certificate Error: {str(e)}\n\nTo fix: Add 'GROQ_VERIFY_SSL=false' to .env"
        except requests.exceptions.RequestException as e:
            return f"Error calling Groq API: {str(e)}"

    def _build_prompt(
        self, commits: list[str], report_type: str, grouped: Optional[dict[str, list[str]]]
    ) -> str:
        if grouped:
            commits_text = ""
            for component, component_commits in grouped.items():
                if component_commits:
                    commits_text += f"\n## {component}\n"
                    commits_text += "\n".join(f"- {commit}" for commit in component_commits)
                    commits_text += "\n"

            return f"""Please summarize the following {report_type} git commits.

Commits by Component:
{commits_text}

Provide a clear, professional summary in markdown format."""
        else:
            commits_text = "\n".join(f"- {commit}" for commit in commits)
            return f"""Please summarize the following {report_type} git commits.

Organize by categories (Features, Bug Fixes, Improvements, etc.).

Commits:
{commits_text}

Provide a clear, professional summary in markdown format."""
