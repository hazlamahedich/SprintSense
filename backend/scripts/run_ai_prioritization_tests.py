#!/usr/bin/env python3
"""
Script to run AI Prioritization tests with proper setup and validation.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path


def check_prerequisites():
    """Check if all required dependencies are installed."""
    print("🔍 Checking prerequisites...")

    required_packages = [
        "pytest",
        "pytest-asyncio",
        "httpx",
        "sqlalchemy",
        "fastapi",
        "pydantic",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False

    print("✅ All prerequisites satisfied")
    return True


def validate_project_structure():
    """Validate that the project structure is correct."""
    print("\n🏗️  Validating project structure...")

    required_paths = [
        "backend/app/domains/services/ai_prioritization_service.py",
        "backend/app/domains/schemas/ai_prioritization.py",
        "backend/app/domains/routers/ai_prioritization.py",
        "backend/tests/unit/services/test_ai_prioritization_service.py",
        "backend/tests/integration/api/test_ai_prioritization_api.py",
        "backend/tests/performance/test_ai_prioritization_performance.py",
    ]

    missing_files = []

    for path in required_paths:
        if not Path(path).exists():
            print(f"  ❌ {path}")
            missing_files.append(path)
        else:
            print(f"  ✅ {path}")

    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False

    print("✅ Project structure is valid")
    return True


def run_tests(test_type="all"):
    """Run the specified test type."""
    print(f"\n🧪 Running {test_type} tests...")

    test_commands = {
        "unit": [
            "python",
            "-m",
            "pytest",
            "tests/unit/services/test_ai_prioritization_service.py",
            "-v",
            "--tb=short",
        ],
        "integration": [
            "python",
            "-m",
            "pytest",
            "tests/integration/api/test_ai_prioritization_api.py",
            "-v",
            "--tb=short",
        ],
        "performance": [
            "python",
            "-m",
            "pytest",
            "tests/performance/test_ai_prioritization_performance.py",
            "-v",
            "--tb=short",
            "-s",
        ],
        "all": [
            "python",
            "-m",
            "pytest",
            "-k",
            "ai_prioritization",
            "-v",
            "--tb=short",
        ],
    }

    if test_type not in test_commands:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_commands.keys())}")
        return False

    try:
        # Change to backend directory
        os.chdir("backend")

        # Run the tests
        result = subprocess.run(
            test_commands[test_type], capture_output=True, text=True
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ {test_type.title()} tests passed!")
            return True
        else:
            print(
                f"❌ {test_type.title()} tests failed with exit code {result.returncode}"
            )
            return False

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_coverage_report():
    """Run tests with coverage reporting."""
    print("\n📊 Running coverage analysis...")

    coverage_cmd = [
        "python",
        "-m",
        "pytest",
        "-k",
        "ai_prioritization",
        "--cov=app.domains.services.ai_prioritization_service",
        "--cov=app.domains.routers.ai_prioritization",
        "--cov=app.domains.schemas.ai_prioritization",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
    ]

    try:
        os.chdir("backend")
        result = subprocess.run(coverage_cmd, capture_output=True, text=True)

        print("Coverage Report:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Coverage analysis complete!")
            print("📁 HTML report generated in backend/htmlcov/")
            return True
        else:
            print(f"❌ Coverage analysis failed with exit code {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return False


def main():
    """Main function to orchestrate test execution."""
    print("🚀 AI Prioritization Test Runner")
    print("=" * 50)

    # Check arguments
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    run_coverage = "--coverage" in sys.argv

    # Validate setup
    if not check_prerequisites():
        sys.exit(1)

    if not validate_project_structure():
        sys.exit(1)

    # Run tests
    success = True

    if run_coverage:
        success = run_coverage_report()
    else:
        success = run_tests(test_type)

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        print("\n💡 Next steps:")
        print("  - Review test results and coverage")
        print("  - Fix any failing tests")
        print("  - Consider adding more edge case tests")
        print("  - Run performance tests under load")
    else:
        print("❌ Tests failed. Please review the output above.")
        print("\n🔧 Troubleshooting tips:")
        print("  - Check database connection")
        print("  - Ensure Redis is running")
        print("  - Verify all dependencies are installed")
        print("  - Check application logs")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
