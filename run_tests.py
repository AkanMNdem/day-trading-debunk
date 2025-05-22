#!/usr/bin/env python
"""
Run all tests for the day-trading-debunk project.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py unit         # Run only unit tests
    python run_tests.py integration  # Run only integration tests
"""
import subprocess
import sys


def run_tests(test_type=None):
    """Run tests with pytest."""
    print(f"Running {'all' if test_type is None else test_type} tests...")
    
    # Base command
    cmd = ['pytest', '-v']
    
    # Add coverage reporting
    cmd.extend(['--cov=src', '--cov=data', '--cov-report=term', '--cov-report=html'])
    
    # Add test type filter if specified
    if test_type == 'unit':
        cmd.append('-m unit')
    elif test_type == 'integration':
        cmd.append('-m integration')
    
    # Run the tests
    result = subprocess.run(' '.join(cmd), shell=True)
    
    # Return exit code
    return result.returncode


if __name__ == '__main__':
    # Get test type from command line argument
    test_type = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Validate test type
    valid_types = [None, 'unit', 'integration']
    if test_type not in valid_types:
        print(f"Error: Invalid test type '{test_type}'. Must be one of: {', '.join(str(t) for t in valid_types if t is not None)}.")
        sys.exit(1)
    
    # Run tests
    exit_code = run_tests(test_type)
    
    # Exit with the same code as pytest
    sys.exit(exit_code) 