#!/usr/bin/env python3
"""
CI Test Runner

This script runs tests in CI mode, skipping GUI tests that can cause hanging.
"""

import os
import sys
import subprocess
import time


def main() -> int:
    """Run tests in CI mode."""
    print("🚀 Starting CI test run...")

    # Set CI environment variable
    os.environ["CI"] = "true"

    # Determine test command based on environment
    if os.name == "nt":  # Windows
        print("🪟 Running on Windows - skipping GUI tests")
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "-m",
            "not gui",
            "--disable-warnings",
        ]
    else:  # Unix/Linux
        print("🐧 Running on Unix/Linux - skipping GUI tests")
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "-m",
            "not gui",
            "--disable-warnings",
        ]

    print(f"📋 Running command: {' '.join(cmd)}")

    # Run tests with timeout
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            timeout=600,  # 10 minute timeout for entire test suite
            capture_output=True,
            text=True,
        )

        elapsed_time = time.time() - start_time
        print(f"⏱️  Tests completed in {elapsed_time:.2f} seconds")

        # Print output
        if result.stdout:
            print("📤 STDOUT:")
            print(result.stdout)

        if result.stderr:
            print("⚠️  STDERR:")
            print(result.stderr)

        # Return appropriate exit code
        if result.returncode == 0:
            print("✅ All tests passed!")
            return 0
        else:
            print(f"❌ Tests failed with exit code {result.returncode}")
            return result.returncode

    except subprocess.TimeoutExpired:
        print("⏰ Test suite timed out after 10 minutes")
        return 1
    except Exception as e:
        print(f"💥 Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
