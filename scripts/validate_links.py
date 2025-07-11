#!/usr/bin/env python3
"""
Script to validate all markdown links in the documentation.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def extract_links_from_markdown(file_path: Path) -> List[Dict[str, Optional[str]]]:
    """Extract all markdown links from a file."""
    links: List[Dict[str, Optional[str]]] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Find all markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        for text, url in matches:
            links.append({
                'text': text,
                'url': url,
                'file': str(file_path),
                'line': None  # Could be enhanced to find line numbers
            })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return links


def validate_link(link: Dict[str, Optional[str]], docs_root: Path) -> Tuple[bool, str]:
    """Validate if a link is valid."""
    url = link['url'] or ''
    # Skip external URLs
    if url.startswith(('http://', 'https://', 'mailto:')):
        return True, "External link"
    # Handle relative links
    if url.startswith('./') or url.startswith('../'):
        # Resolve relative path
        link_file = Path(link['file'] or '.')
        target_path = (link_file.parent / url).resolve()
        if target_path.exists():
            return True, "Valid file"
        else:
            return False, f"File not found: {target_path}"
    # Handle anchor links (same file)
    if url.startswith('#'):
        return True, "Anchor link"
    # Handle absolute paths from docs root
    if url.startswith('/'):
        target_path = docs_root / url[1:]
        if target_path.exists():
            return True, "Valid file"
        else:
            return False, f"File not found: {target_path}"
    # Handle relative paths without ./
    link_file = Path(link['file'] or '.')
    target_path = link_file.parent / url
    if target_path.exists():
        return True, "Valid file"
    else:
        return False, f"File not found: {target_path}"


def main() -> None:
    """Main function to validate all links."""
    docs_root = Path("docs")
    if not docs_root.exists():
        print("Error: docs directory not found")
        sys.exit(1)
    # Find all markdown files
    markdown_files = list(docs_root.rglob("*.md"))
    if not markdown_files:
        print("No markdown files found in docs directory")
        sys.exit(1)
    print(f"Found {len(markdown_files)} markdown files")
    print("=" * 50)
    all_links: List[Dict[str, Optional[str]]] = []
    invalid_links: List[Dict[str, Optional[str]]] = []
    # Extract links from all files
    for file_path in markdown_files:
        links = extract_links_from_markdown(file_path)
        all_links.extend(links)
        print(f"\n{file_path}:")
        for link in links:
            is_valid, message = validate_link(link, docs_root)
            status = "✓" if is_valid else "✗"
            print(f"  {status} [{link['text']}]({link['url']}) - {message}")
            if not is_valid:
                invalid_links.append(link)
    # Summary
    print("\n" + "=" * 50)
    print(f"Total links found: {len(all_links)}")
    print(f"Valid links: {len(all_links) - len(invalid_links)}")
    print(f"Invalid links: {len(invalid_links)}")
    if invalid_links:
        print("\nInvalid links:")
        for link in invalid_links:
            print(f"  - {link['file']}: [{link['text']}]({link['url']})")
        sys.exit(1)
    else:
        print("\nAll links are valid! ✓")
        sys.exit(0)


if __name__ == "__main__":
    main()
