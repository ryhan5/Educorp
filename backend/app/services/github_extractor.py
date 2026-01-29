import httpx
import asyncio
from typing import Optional

async def fetch_github_summary(github_url: str) -> str:
    """
    Fetches a summary of a user's public GitHub repositories.
    Extracts languages, descriptions, and top repo names.
    """
    if not github_url:
        return ""

    # Extract username from URL (e.g., https://github.com/torvalds -> torvalds)
    try:
        username = github_url.rstrip("/").split("/")[-1]
    except Exception:
        return f"Invalid GitHub URL provided: {github_url}"

    api_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url, 
                headers={"User-Agent": "EduCorp-Hackathon-Bot"},
                timeout=10.0
            )
            
            if response.status_code == 404:
                return f"GitHub User '{username}' not found."
            
            if response.status_code == 403:
                return "GitHub API Rate Limit Exceeded. Cannot fetch details right now."
                
            if response.status_code != 200:
                return f"Failed to fetch GitHub data. Status: {response.status_code}"

            repos = response.json()
            
            if not repos:
                return f"User '{username}' has no public repositories."

            # Summarize Data
            summary_lines = [f"--- GitHub Portfolio Summary for {username} ---"]
            
            languages = {}
            repo_details = []

            for repo in repos:
                name = repo.get("name", "Unknown")
                desc = repo.get("description") or "No description"
                lang = repo.get("language")
                stars = repo.get("stargazers_count", 0)
                
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
                
                repo_details.append(f"- {name} ({lang or 'Misc'}): {desc} [Stars: {stars}]")

            # Top Languages
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            top_langs = ", ".join([f"{l} ({c})" for l, c in sorted_langs])
            
            summary_lines.append(f"Top Languages: {top_langs}")
            summary_lines.append("Recent Repositories:")
            summary_lines.extend(repo_details[:5]) # Top 5 recent
            
            return "\n".join(summary_lines)

    except Exception as e:
        return f"Error connecting to GitHub: {str(e)}"
