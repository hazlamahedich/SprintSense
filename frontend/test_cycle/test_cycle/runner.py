"""Test runner module for executing Playwright tests with smart retries."""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pytest
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Represents the result of a test execution."""
    test_name: str
    status: str  # 'passed', 'failed', 'skipped'
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    duration: float = 0.0
    timestamp: str = datetime.now().isoformat()
    artifacts: dict = None

    def to_dict(self) -> dict:
        """Convert the test result to a dictionary."""
        return {
            'test_name': self.test_name,
            'status': self.status,
            'error_message': self.error_message,
            'error_type': self.error_type,
            'retry_count': self.retry_count,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'artifacts': self.artifacts or {}
        }

class TestRunner:
    """Manages the execution of Playwright tests with failure tracking and retries."""

    def __init__(
        self,
        test_path: str,
        max_retries: int = 3,
        cooldown_seconds: int = 5,
        artifact_path: Optional[str] = None
    ):
        self.test_path = Path(test_path)
        self.max_retries = max_retries
        self.cooldown_seconds = cooldown_seconds
        self.artifact_path = Path(artifact_path) if artifact_path else Path('test-results')
        self.failed_tests: List[TestResult] = []
        self.all_results: List[TestResult] = []

        # Ensure artifact directory exists
        self.artifact_path.mkdir(parents=True, exist_ok=True)

    async def run_tests(self) -> List[TestResult]:
        """Execute the test suite and capture results."""
        logger.info(f"Starting test execution in {self.test_path}")

        # Configure pytest arguments
        pytest_args = [
            str(self.test_path),
            '--capture=no',  # Show test output in real time
            f'--html={self.artifact_path}/report.html',
            '--self-contained-html',
            '--tb=short',  # Shorter traceback format
            '-v'  # Verbose output
        ]

        try:
            # Run tests and capture results
            pytest.main(pytest_args)

            # Process results and collect artifacts
            await self._process_test_results()

            return self.all_results

        except Exception as e:
            logger.error(f"Error during test execution: {e}")
            raise

    async def retry_failed_tests(self) -> List[TestResult]:
        """Retry failed tests with cooldown period."""
        if not self.failed_tests:
            logger.info("No failed tests to retry")
            return []

        retry_results = []

        for test in self.failed_tests:
            if test.retry_count >= self.max_retries:
                logger.warning(f"Test {test.test_name} has reached maximum retry count")
                continue

            logger.info(f"Retrying test {test.test_name} (attempt {test.retry_count + 1})")

            # Implement cooldown period
            await asyncio.sleep(self.cooldown_seconds)

            # Run single test
            pytest_args = [
                str(self.test_path),
                '-k', test.test_name,
                '--capture=no',
                f'--html={self.artifact_path}/retry-{test.test_name}.html',
                '--self-contained-html'
            ]

            pytest.main(pytest_args)

            # Update retry count and process results
            test.retry_count += 1
            await self._process_test_results(test_name=test.test_name)

            retry_results.append(test)

        return retry_results

    async def _process_test_results(self, test_name: Optional[str] = None):
        """Process test results and collect artifacts."""
        # Implement result processing logic here
        # This would parse pytest results and create TestResult objects
        pass

    def _collect_artifacts(self, test_name: str) -> dict:
        """Collect test artifacts (traces, screenshots, videos)."""
        artifacts = {}
        artifact_types = ['trace.zip', 'screenshot.png', 'video.webm']

        for artifact_type in artifact_types:
            pattern = f"**/*{test_name}*{artifact_type}"
            matches = list(self.artifact_path.glob(pattern))

            if matches:
                artifacts[artifact_type] = str(matches[0].relative_to(self.artifact_path))

        return artifacts

    def save_results(self):
        """Save test results to a JSON file."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.all_results),
            'failed_tests': len(self.failed_tests),
            'results': [result.to_dict() for result in self.all_results]
        }

        output_file = self.artifact_path / 'test-results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Test results saved to {output_file}")
