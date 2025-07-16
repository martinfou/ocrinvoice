#!/usr/bin/env python3
"""
Release script for OCR Invoice Parser.

This script handles version bumping, tagging, and release preparation.

Usage:
    python scripts/release.py [major|minor|patch]
    python scripts/release.py --version 1.2.3
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import Union


def run_command(
    command: str, check: bool = True
) -> Union[subprocess.CompletedProcess, None]:
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, check=check, shell=True, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None


def get_current_version() -> Union[str, None]:
    """Get the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return None

    with open(pyproject_path, "r") as f:
        content = f.read()

    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    print("❌ Could not find version in pyproject.toml")
    return None


def bump_version(current_version: str, bump_type: str) -> Union[str, None]:
    """Bump version based on type (major, minor, patch)."""
    parts = current_version.split(".")
    if len(parts) != 3:
        print(f"❌ Invalid version format: {current_version}")
        return None

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"❌ Invalid bump type: {bump_type}")
        return None

    return f"{major}.{minor}.{patch}"


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace version in pyproject.toml
    if file_path.name == "pyproject.toml":
        content = re.sub(
            r'version\s*=\s*["\'][^"\']+["\']', f'version = "{new_version}"', content
        )

    # Replace version in README.md
    elif file_path.name == "README.md":
        content = re.sub(
            r'version\s*=\s*["\'][^"\']+["\']', f'version = "{new_version}"', content
        )
        # Also replace any other version references
        content = re.sub(
            r"Current Version[:\s]*\d+\.\d+\.\d+",
            f"Current Version: {new_version}",
            content,
        )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def update_version(new_version: str) -> bool:
    """Update version in all relevant files."""
    files_to_update = [
        Path("pyproject.toml"),
        Path("README.md"),
    ]

    current_version = get_current_version()
    if not current_version:
        return False

    print(f"Updating version from {current_version} to {new_version}")

    for file_path in files_to_update:
        if file_path.exists():
            update_version_in_file(file_path, current_version, new_version)
            print(f"✅ Updated {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")

    return True


def check_git_status() -> bool:
    """Check if git repository is clean."""
    result = run_command("git status --porcelain")
    if not result or result.stdout.strip():
        print("❌ Git repository is not clean. Please commit or stash changes.")
        return False

    print("✅ Git repository is clean")
    return True


def create_git_tag(version: str) -> bool:
    """Create a git tag for the release."""
    tag_name = f"v{version}"

    # Check if tag already exists
    result = run_command(f"git tag -l {tag_name}")
    if result and result.stdout.strip():
        print(f"❌ Tag {tag_name} already exists")
        return False

    # Create and push tag
    result = run_command(f"git tag {tag_name}")
    if not result or result.returncode != 0:
        print(f"❌ Failed to create tag {tag_name}")
        return False

    result = run_command(f"git push origin {tag_name}")
    if not result or result.returncode != 0:
        print(f"❌ Failed to push tag {tag_name}")
        return False

    print(f"✅ Created and pushed tag {tag_name}")
    return True


def build_package() -> bool:
    """Build the package for distribution."""
    print("Building package...")

    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/")

    # Install build dependencies
    result = run_command("pip install build wheel setuptools")
    if not result or result.returncode != 0:
        print("❌ Failed to install build dependencies")
        return False

    # Build package
    result = run_command("python -m build")
    if not result or result.returncode != 0:
        print("❌ Failed to build package")
        return False

    print("✅ Package built successfully")
    return True


def run_tests() -> bool:
    """Run the test suite."""
    print("Running tests...")

    result = run_command("pytest tests/ -v")
    if not result or result.returncode != 0:
        print("❌ Tests failed")
        return False

    print("✅ Tests passed")
    return True


def main() -> None:
    """Main release function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/release.py [major|minor|patch]")
        print("   or: python scripts/release.py --version 1.2.3")
        sys.exit(1)

    # Parse arguments
    if sys.argv[1] == "--version":
        if len(sys.argv) < 3:
            print("❌ Please provide a version number")
            sys.exit(1)
        new_version = sys.argv[2]
        bump_type = None
    else:
        bump_type = sys.argv[1]
        if bump_type not in ["major", "minor", "patch"]:
            print("❌ Invalid bump type. Use: major, minor, or patch")
            sys.exit(1)

        current_version = get_current_version()
        if not current_version:
            sys.exit(1)

        new_version_result = bump_version(current_version, bump_type)
        if not new_version_result:
            sys.exit(1)
        new_version = new_version_result

    print(f"🚀 Preparing release {new_version}")
    print("=" * 50)

    # Check git status
    if not check_git_status():
        sys.exit(1)

    # Run tests
    if not run_tests():
        sys.exit(1)

    # Update version
    if not update_version(new_version):
        sys.exit(1)

    # Build package
    if not build_package():
        sys.exit(1)

    # Commit changes
    commit_message = f"""release: bump version to {new_version}

- Update version numbers across all configuration files
- Prepare for release {new_version}
- Automated version bump by release script"""
    
    result = run_command(f'git add . && git commit -m "{commit_message}"')
    if not result or result.returncode != 0:
        print("❌ Failed to commit version changes")
        sys.exit(1)

    # Push changes
    result = run_command("git push origin main")
    if not result or result.returncode != 0:
        print("❌ Failed to push changes")
        sys.exit(1)

    # Create and push tag
    if not create_git_tag(new_version):
        sys.exit(1)

    print("\n🎉 Release prepared successfully!")
    print(f"Version: {new_version}")
    print("\nNext steps:")
    print("1. Check GitHub Actions for build status")
    print("2. Review the generated release on GitHub")
    print("3. Publish the release if everything looks good")


if __name__ == "__main__":
    main()
