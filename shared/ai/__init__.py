"""AI helpers shared across tools.

This module exposes:
- AICommitSummarizer: existing helper used by report/commit/review
- chat_completion: generic helper for other tools (grammar, translate, ...)
"""

import os
from typing import Optional

import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    *,
    api_key: Optional[str] = None,
    verify_ssl: Optional[bool] = None,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> str:
    """Call Groq chat completions with a simple interface.

    This is intentionally generic so other tools can reuse it for
    tasks like translation or grammar checking.
    """

    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in .env file or environment variable."
        )

    base_url = "https://api.groq.com/openai/v1/chat/completions"

    try:
        response = requests.post(
            base_url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=30,
            verify=_resolve_verify_ssl(verify_ssl),
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.SSLError as e:
        return f"SSL Certificate Error: {str(e)}\n\nTo fix: Add 'GROQ_VERIFY_SSL=false' to .env"
    except requests.exceptions.RequestException as e:
        return f"Error calling Groq API: {str(e)}"


def _resolve_verify_ssl(override: Optional[bool]) -> bool:
    if override is not None:
        return override
    verify_env = os.getenv("GROQ_VERIFY_SSL", "true").lower()
    return verify_env not in ("false", "0", "no")


class AICommitSummarizer:
    def __init__(self, api_key: Optional[str] = None, verify_ssl: Optional[bool] = None):
        self.api_key = api_key
        self.verify_ssl = verify_ssl

    def summarize(
        self,
        commits: list[str],
        report_type: str = "daily",
        grouped: Optional[dict[str, list[str]]] = None,
    ) -> str:
        if not commits:
            return "No commits to summarize."

        prompt = self._build_prompt(commits, report_type, grouped)

        system_prompt = (
            "You are a helpful assistant that summarizes git commit messages "
            "into concise, professional reports."
        )

        return chat_completion(
            system_prompt,
            prompt,
            api_key=self.api_key,
            verify_ssl=self.verify_ssl,
        )

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
        commits_text = "\n".join(f"- {commit}" for commit in commits)
        return f"""Please summarize the following {report_type} git commits.

Organize by categories (Features, Bug Fixes, Improvements, etc.).

Commits:
{commits_text}

Provide a clear, professional summary in markdown format."""
