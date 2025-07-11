"""
Test command implementation.

This module contains the test command implementation for
running the test suite.
"""

import click
import logging
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def test_command(
    test_data: Optional[str] = None,
    verbose: bool = False,
    coverage: bool = False,
    output: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run test suite.

    Args:
        test_data: Test data file path (optional)
        verbose: Enable verbose output
        coverage: Generate coverage report
        output: Output file for test results

    Returns:
        Test results dictionary
    """
    logger.info("Running test suite...")

    if test_data:
        logger.info(f"Using test data: {test_data}")

    if verbose:
        logger.info("Verbose mode enabled")

    if coverage:
        logger.info("Coverage reporting enabled")

    # Run tests
    test_results = run_tests(test_data, verbose, coverage)

    # Print summary
    print_test_summary(test_results)

    # Save results if output specified
    if output:
        save_test_results(test_results, output)

    return test_results


def run_tests(
    test_data: Optional[str] = None, verbose: bool = False, coverage: bool = False
) -> Dict[str, Any]:
    """
    Run the actual tests using pytest.

    Args:
        test_data: Test data file path
        verbose: Enable verbose output
        coverage: Generate coverage report

    Returns:
        Test results
    """
    start_time = datetime.now()

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add verbosity
    if verbose:
        cmd.extend(["-v"])

    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src/ocrinvoice", "--cov-report=term-missing"])

    # Add test data environment variable if provided
    env = None
    if test_data:
        env = {"OCRINVOICE_TEST_DATA": test_data}

    try:
        logger.info(f"Running pytest command: {' '.join(cmd)}")

        # Run pytest
        result = subprocess.run(
            cmd, capture_output=True, text=True, env=env, cwd=Path.cwd()
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Parse test results
        test_results = parse_pytest_output(result, duration)

        return test_results

    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return {
            "status": "error",
            "error": str(e),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0,
            "tests": [],
            "stdout": "",
            "stderr": "",
        }


def parse_pytest_output(
    result: subprocess.CompletedProcess, duration: float
) -> Dict[str, Any]:
    """
    Parse pytest output to extract test results.

    Args:
        result: Completed process result from pytest
        duration: Test execution duration

    Returns:
        Parsed test results
    """
    stdout = result.stdout
    stderr = result.stderr

    # Extract test summary from output
    lines = stdout.split("\n")

    # Look for pytest summary line
    summary_line = None
    for line in reversed(lines):
        if "passed" in line and ("failed" in line or "error" in line):
            summary_line = line
            break

    # Parse summary
    total_tests = 0
    passed = 0
    failed = 0

    if summary_line:
        # Example: "198 passed, 5 failed in 45.23s"
        parts = summary_line.split()
        for part in parts:
            if part.isdigit():
                if "passed" in summary_line and part in summary_line:
                    passed = int(part)
                elif "failed" in summary_line and part in summary_line:
                    failed = int(part)
                elif "error" in summary_line and part in summary_line:
                    failed = int(part)

    total_tests = passed + failed

    # Extract individual test results if verbose
    tests = []
    if "::" in stdout:
        for line in lines:
            if "::" in line and (
                "PASSED" in line or "FAILED" in line or "ERROR" in line
            ):
                test_name = line.split("::")[1].split()[0] if "::" in line else line
                status = "PASS" if "PASSED" in line else "FAIL"
                tests.append(
                    {
                        "name": test_name,
                        "status": status,
                        "duration": 0.0,  # Individual test duration not easily extractable
                    }
                )

    # If no individual tests found, create summary
    if not tests and total_tests > 0:
        tests = [
            {
                "name": f"Test Suite ({total_tests} tests)",
                "status": "PASS" if failed == 0 else "FAIL",
                "duration": duration,
            }
        ]

    return {
        "status": "success" if failed == 0 else "failure",
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "duration": duration,
        "tests": tests,
        "stdout": stdout,
        "stderr": stderr,
        "return_code": result.returncode,
        "timestamp": datetime.now().isoformat(),
    }


def print_test_summary(results: Dict[str, Any]) -> None:
    """
    Print test summary.

    Args:
        results: Test results dictionary
    """
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if results.get("error"):
        print(f"❌ Error: {results['error']}")
        return

    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Duration: {results['duration']:.2f}s")
    print(f"Status: {results['status'].upper()}")

    # Show coverage if available
    if "coverage" in results:
        coverage = results["coverage"]
        print(f"Coverage: {coverage.get('total', 0):.1f}%")

    if results["failed"] > 0:
        print("\nFailed Tests:")
        for test in results["tests"]:
            if test["status"] == "FAIL":
                print(f"  ✗ {test['name']}")

    # Show return code
    if results.get("return_code") is not None:
        print(f"\nExit Code: {results['return_code']}")

    print("=" * 60)


def save_test_results(results: Dict[str, Any], output_path: str) -> None:
    """
    Save test results to file.

    Args:
        results: Test results dictionary
        output_path: Output file path
    """
    logger.info(f"Saving test results to: {output_path}")

    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Test results saved to: {output_path}")

    except Exception as e:
        logger.error(f"Error saving test results: {e}")
        raise


def load_test_data(test_data_path: str) -> Dict[str, Any]:
    """
    Load test data from file.

    Args:
        test_data_path: Path to test data file

    Returns:
        Test data dictionary
    """
    logger.info(f"Loading test data from: {test_data_path}")

    try:
        with open(test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        return {}


def run_specific_tests(
    test_patterns: List[str], verbose: bool = False
) -> Dict[str, Any]:
    """
    Run specific tests by pattern.

    Args:
        test_patterns: List of test patterns to run
        verbose: Enable verbose output

    Returns:
        Test results
    """
    cmd = [sys.executable, "-m", "pytest"]

    if verbose:
        cmd.extend(["-v"])

    cmd.extend(test_patterns)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return parse_pytest_output(result, 0.0)
    except Exception as e:
        logger.error(f"Error running specific tests: {e}")
        return {
            "status": "error",
            "error": str(e),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0,
            "tests": [],
        }
