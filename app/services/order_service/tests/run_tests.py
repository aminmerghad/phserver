#!/usr/bin/env python
"""
Test runner script for Order Service tests.
This script provides a convenient way to run different test suites
for the Order Service with various options.
"""

import os
import sys
import subprocess
import argparse

# Get the root directory of the project
# This assumes this script is located in app/services/order_service/tests
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../'))
ORDER_SERVICE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../'))

def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests for the order service"""
    cmd = ['pytest', os.path.join(SCRIPT_DIR, 'unit')]
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app.services.order_service.domain', '--cov-report=term'])
    
    print("\n=== Running Unit Tests ===")
    subprocess.run(cmd)

def run_integration_tests(verbose=False, coverage=False):
    """Run integration tests for the order service"""
    cmd = ['pytest', os.path.join(SCRIPT_DIR, 'integration')]
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app.services.order_service', '--cov-report=term'])
    
    print("\n=== Running Integration Tests ===")
    subprocess.run(cmd)

def run_api_tests(verbose=False, coverage=False):
    """Run API tests for the order service"""
    cmd = ['pytest', os.path.join(SCRIPT_DIR, 'test_order_api.py')]
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app.services.order_service', '--cov-report=term'])
    
    print("\n=== Running API Tests ===")
    subprocess.run(cmd)

def run_all_tests(verbose=False, coverage=False):
    """Run all tests for the order service"""
    cmd = ['pytest', SCRIPT_DIR]
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app.services.order_service', '--cov-report=term'])
    
    print("\n=== Running All Tests ===")
    subprocess.run(cmd)

def generate_coverage_report():
    """Generate a complete HTML coverage report"""
    cmd = [
        'pytest', SCRIPT_DIR,
        '--cov=app.services.order_service',
        '--cov-report=html:coverage_html',
        '--cov-report=term'
    ]
    
    print("\n=== Generating Coverage Report ===")
    subprocess.run(cmd)
    print(f"\nCoverage report generated in {os.path.join(SCRIPT_DIR, 'coverage_html')}")

def main():
    parser = argparse.ArgumentParser(description='Run Order Service tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--api', action='store_true', help='Run API tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage data')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Change to project root directory for proper imports
    os.chdir(PROJECT_ROOT)
    
    # If no test type specified, run all tests
    if not any([args.unit, args.integration, args.api, args.all, args.html_report]):
        args.all = True
    
    # Run selected test types
    if args.unit:
        run_unit_tests(args.verbose, args.coverage)
    
    if args.integration:
        run_integration_tests(args.verbose, args.coverage)
    
    if args.api:
        run_api_tests(args.verbose, args.coverage)
    
    if args.all:
        run_all_tests(args.verbose, args.coverage)
    
    if args.html_report:
        generate_coverage_report()
    
    print("\nTest execution completed!")

if __name__ == "__main__":
    main()