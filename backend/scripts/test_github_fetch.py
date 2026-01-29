import asyncio
import sys
import os

# Ensure backend root is in path
sys.path.append(os.getcwd())

from app.services.github_extractor import fetch_github_summary

async def main():
    # Test cases
    urls = [
        "https://github.com/torvalds", # Famous profile
        "https://github.com/definitely_not_a_valid_user_12345", # Invalid
        "https://github.com/microsoft" # Org
    ]

    for url in urls:
        print(f"\n--- Testing: {url} ---")
        summary = await fetch_github_summary(url)
        print(summary)

if __name__ == "__main__":
    asyncio.run(main())
