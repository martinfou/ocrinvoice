#!/usr/bin/env python3
"""
OCR Invoice Parser - Release Creation Script

This script automates the release process by:
1. Updating version numbers across all relevant files
2. Running tests to ensure everything works
3. Creating a Git tag
4. Building the release
5. Creating a GitHub release

Usage:
    python scripts/create_release.py --version 1.2.1
    python scripts/create_release.py --version 1.2.1 --skip-tests
    python scripts/create_release.py --version 1.2.1 --dry-run
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Dict, Any


class ReleaseManager:
    """Manages the release process for OCR Invoice Parser."""
    
    def __init__(self, version: str, dry_run: bool = False, skip_tests: bool = False):
        self.version = version
        self.dry_run = dry_run
        self.skip_tests = skip_tests
        self.project_root = Path(__file__).parent.parent
        
        # Files that contain version numbers
        self.version_files = [
            "src/ocrinvoice/gui/__init__.py",
            "src/ocrinvoice/gui/ocr_main_window.py", 
            "src/ocrinvoice/gui/main_window.py",
            "pyproject.toml",
            "README.md"
        ]
        
        # Version patterns to update
        self.version_patterns = [
            (r'__version__\s*=\s*["\']([^"\']+)["\']', '__version__ = "{}"'),
            (r'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)', 'Version: {}'),
            (r'v([0-9]+\.[0-9]+\.[0-9]+)', 'v{}'),
            (r'version\s*=\s*["\']([^"\']+)["\']', 'version = "{}"'),
            (r'Business Mappings Manager v([0-9]+\.[0-9]+\.[0-9]+)', 'Business Mappings Manager v{}'),
            (r'setApplicationVersion\(["\']([^"\']+)["\']\)', 'setApplicationVersion("{}")'),
            (r'python_version\s*=\s*["\']([^"\']+)["\']', 'python_version = "{}"'),
        ]
    
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command."""
        print(f"🔄 Running: {' '.join(command)}")
        if self.dry_run:
            print(f"   [DRY RUN] Would run: {' '.join(command)}")
            return subprocess.CompletedProcess(command, 0, "", "")
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=self.project_root)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   Error: {result.stderr}")
            sys.exit(1)
        return result
    
    def check_git_status(self) -> None:
        """Check if Git repository is clean."""
        print("🔍 Checking Git status...")
        result = self.run_command(["git", "status", "--porcelain"])
        if result.stdout.strip():
            print("❌ Git repository is not clean. Please commit or stash changes.")
            print("   Uncommitted changes:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")
            sys.exit(1)
        print("✅ Git repository is clean")
    
    def update_version_in_file(self, file_path: str) -> bool:
        """Update version number in a single file."""
        file_path = self.project_root / file_path
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False
        
        print(f"📝 Updating version in {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply version patterns
        for pattern, replacement in self.version_patterns:
            content = re.sub(pattern, replacement.format(self.version), content)
        
        # Check if content changed
        if content == original_content:
            print(f"   No version found to update in {file_path}")
            return False
        
        if not self.dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"   ✅ Updated version to {self.version}")
        return True
    
    def update_all_versions(self) -> None:
        """Update version numbers in all relevant files."""
        print(f"🚀 Updating version to {self.version}...")
        
        updated_files = []
        for file_path in self.version_files:
            if self.update_version_in_file(file_path):
                updated_files.append(file_path)
        
        if not updated_files:
            print("⚠️  No files were updated. Check version patterns.")
        else:
            print(f"✅ Updated {len(updated_files)} files")
    
    def run_tests(self) -> None:
        """Run the test suite."""
        if self.skip_tests:
            print("⏭️  Skipping tests as requested")
            return
        
        print("🧪 Running tests...")
        # Run pytest without capturing output to allow proper terminal interaction
        if self.dry_run:
            print(f"   [DRY RUN] Would run: python -m pytest tests/ -v")
            return
        
        print("🔄 Running: python -m pytest tests/ -v")
        result = subprocess.run(["python", "-m", "pytest", "tests/", "-v"], 
                              cwd=self.project_root, 
                              capture_output=False)
        
        if result.returncode != 0:
            print(f"❌ Tests failed with exit code {result.returncode}")
            sys.exit(1)
        
        print("✅ All tests passed")
    
    def commit_version_changes(self) -> None:
        """Commit version changes."""
        print("📝 Committing version changes...")
        
        # Add all modified files
        self.run_command(["git", "add", "."])
        
        # Commit with version bump message
        commit_message = f"chore(release): bump version to {self.version}\n\n- Update version numbers across all files\n- Prepare for release {self.version}"
        self.run_command(["git", "commit", "-m", commit_message])
        
        print("✅ Version changes committed")
    
    def create_git_tag(self) -> None:
        """Create a Git tag for the release."""
        print(f"🏷️  Creating Git tag v{self.version}...")
        self.run_command(["git", "tag", f"v{self.version}"])
        print("✅ Git tag created")
    
    def push_changes(self) -> None:
        """Push changes and tag to remote."""
        print("📤 Pushing changes to remote...")
        self.run_command(["git", "push"])
        self.run_command(["git", "push", "--tags"])
        print("✅ Changes pushed to remote")
    
    def build_release(self) -> None:
        """Build the release packages."""
        print("🔨 Building release packages...")
        
        # Run PyInstaller build
        self.run_command(["python", "-m", "PyInstaller", "OCRInvoiceParser.spec"])
        
        print("✅ Release packages built")
    
    def create_github_release(self) -> None:
        """Create GitHub release using gh CLI."""
        print("🚀 Creating GitHub release...")
        
        # Check if gh CLI is available
        try:
            self.run_command(["gh", "--version"], check=False)
        except FileNotFoundError:
            print("⚠️  GitHub CLI (gh) not found. Please create release manually:")
            print(f"   Visit: https://github.com/martinfou/ocrinvoice/releases/new")
            print(f"   Tag: v{self.version}")
            return
        
        # Create release
        release_notes = self.generate_release_notes()
        
        # Create temporary release notes file
        notes_file = self.project_root / "RELEASE_NOTES.md"
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(release_notes)
        
        try:
            self.run_command([
                "gh", "release", "create", f"v{self.version}",
                "--title", f"Release v{self.version}",
                "--notes-file", "RELEASE_NOTES.md",
                "--draft"
            ])
            print("✅ GitHub release created (draft)")
        finally:
            # Clean up
            if notes_file.exists():
                notes_file.unlink()
    
    def generate_release_notes(self) -> str:
        """Generate release notes."""
        return f"""# OCR Invoice Parser v{self.version}

## 🎉 What's New

### Dark Theme Improvements
- Fixed readability issues in Single PDF tab data table
- Improved Business Alias tab Match Type column visibility
- All tables now properly adapt to system theme (light/dark)

### Bug Fixes
- Fixed column headers not showing correctly in Single PDF tab
- Removed hardcoded colors that caused dark theme issues
- Improved overall UI consistency across all tabs

### Technical Improvements
- Better theme compatibility across all GUI components
- Consistent styling with Project and Official Names tables
- Enhanced user experience in dark mode environments

## 📦 Installation

### Windows
Download `OCRInvoiceParser.exe` from the assets below.

### macOS
Download `OCRInvoiceParser` from the assets below.

### From Source
```bash
pip install ocrinvoice=={self.version}
```

## 🔧 Requirements
- Python 3.8+
- Tesseract OCR
- See README.md for full installation instructions

## 📝 Changelog
For detailed changes, see the commit history and pull requests.

## 🐛 Bug Reports
Please report any issues on the GitHub repository.

---
*Released on {self.get_current_date()}*
"""
    
    def get_current_date(self) -> str:
        """Get current date in a nice format."""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")
    
    def run_release_process(self) -> None:
        """Run the complete release process."""
        print(f"🚀 Starting release process for version {self.version}")
        print("=" * 60)
        
        try:
            # Step 1: Check Git status
            self.check_git_status()
            
            # Step 2: Update version numbers
            self.update_all_versions()
            
            # Step 3: Run tests
            self.run_tests()
            
            if self.dry_run:
                print("🔍 DRY RUN COMPLETE - No changes were made")
                return
            
            # Step 4: Commit changes
            self.commit_version_changes()
            
            # Step 5: Create Git tag
            self.create_git_tag()
            
            # Step 6: Push changes
            self.push_changes()
            
            # Step 7: Build release
            self.build_release()
            
            # Step 8: Create GitHub release
            self.create_github_release()
            
            print("=" * 60)
            print(f"🎉 Release {self.version} completed successfully!")
            print(f"📋 Next steps:")
            print(f"   1. Review the draft release on GitHub")
            print(f"   2. Publish the release when ready")
            print(f"   3. Update any documentation if needed")
            
        except Exception as e:
            print(f"❌ Release failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create a new release of OCR Invoice Parser")
    parser.add_argument("--version", required=True, help="Version number (e.g., 1.2.1)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    
    args = parser.parse_args()
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', args.version):
        print("❌ Invalid version format. Use semantic versioning (e.g., 1.2.1)")
        sys.exit(1)
    
    # Create and run release manager
    release_manager = ReleaseManager(
        version=args.version,
        dry_run=args.dry_run,
        skip_tests=args.skip_tests
    )
    
    release_manager.run_release_process()


if __name__ == "__main__":
    main() 