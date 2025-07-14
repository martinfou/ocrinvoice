#!/usr/bin/env python3
"""
Windows CI Test Runner

Runs tests in Windows CI environment, excluding GUI tests to prevent hanging.
"""

import os
import sys
import subprocess
import platform


def main() -> int:
    """Run tests with Windows CI optimizations."""
    print("Starting Windows CI Test Runner")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    print(f"CI Environment: {os.environ.get('CI', 'Not set')}")

    # Set CI environment variable if not already set
    if not os.environ.get("CI"):
        os.environ["CI"] = "true"
        print("Set CI environment variable")

    # Base test command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--durations=10",
        "--tb=short",
        "-v",
        "--disable-warnings",
        "--strict-markers",
        "--strict-config",
    ]

    # Exclude GUI tests on Windows CI
    if platform.system() == "Windows" or os.environ.get("CI"):
        print("Windows CI detected - excluding GUI tests")
        cmd.extend(["--ignore=tests/unit/test_gui/", "-m", "not gui"])

    # Add test paths
    cmd.extend(["tests/unit/", "tests/integration/"])

    print(f"Running command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print("All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"Test runner error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
