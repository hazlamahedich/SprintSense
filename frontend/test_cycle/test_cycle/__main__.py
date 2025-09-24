"""Main entry point for the test cycle automation framework."""

import asyncio
import logging
import os
from pathlib import Path
import sys
from typing import Dict, List, Optional

from .analyzer import FailureAnalysis
from .auto_fix import AutoFixer
from .warp_llm_fix import WarpLLMFixer
from .reporter import TestReporter
from .runner import TestResult, TestRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestCycle:
    """Manages the entire test cycle with automatic fixing."""
    
    def __init__(
        self,
        test_dir: str,
        max_retries: int = 3,
        max_fix_attempts: int = 3,
        cooldown_seconds: int = 5
    ):
        self.test_dir = Path(test_dir)
        self.max_retries = max_retries
        self.max_fix_attempts = max_fix_attempts
        self.cooldown_seconds = cooldown_seconds
        
        # Initialize components
        self.runner = TestRunner(
            test_path=str(test_dir),
            max_retries=max_retries,
            cooldown_seconds=cooldown_seconds,
            artifact_path='test-results'
        )
        self.auto_fixer = AutoFixer(test_dir)
        self.warp_fixer = WarpLLMFixer(test_dir)
        self.reporter = TestReporter(output_dir='test-reports')
        
        # Track progress
        self.fix_attempts: Dict[str, int] = {}
        self.current_analyses: Dict[str, FailureAnalysis] = {}
    
    async def run(self) -> bool:
        """Run the full test cycle with automatic fixing."""
        logger.info(f"Starting test cycle in {self.test_dir}")
        
        try:
            success = False
            attempt = 1
            
            while not success and attempt <= self.max_fix_attempts:
                logger.info(f"Test cycle attempt {attempt}/{self.max_fix_attempts}")
                
                # Run tests
                results = await self.runner.run_tests()
                
                if not self.runner.failed_tests:
                    logger.info("All tests passed!")
                    success = True
                    break
                
                # Analyze failures
                logger.info(f"Analyzing {len(self.runner.failed_tests)} failed tests...")
                analyses = {}
                for test in self.runner.failed_tests:
                    analysis = self.analyzer.analyze_failure(test)
                    if analysis:
                        analyses[test.test_name] = analysis
                        
                # Try to fix failures
                logger.info("Attempting to fix failed tests...")
                fix_attempts = []
                for test in self.runner.failed_tests:
                    if test.test_name not in self.fix_attempts:
                        self.fix_attempts[test.test_name] = 0
                    
                    if self.fix_attempts[test.test_name] < self.max_fix_attempts:
                        analysis = analyses.get(test.test_name)
                        if analysis:
                            # Try Warp LLM fix first
                            fix_attempt = await self.warp_fixer.attempt_fix(test, analysis)
                            
                            # Fall back to pattern-based fixes if Warp LLM fails
                            if not fix_attempt:
                                logger.info(f"Warp LLM fix failed for {test.test_name}, trying pattern-based fixes...")
                                fix_attempt = await self.auto_fixer.attempt_fix(test, analysis)
                                
                            if fix_attempt:
                                fix_attempts.append(fix_attempt)
                                self.fix_attempts[test.test_name] += 1
                
                if not fix_attempts:
                    logger.warning("No more fixes to attempt")
                    break
                
                # Wait before retrying
                logger.info(f"Waiting {self.cooldown_seconds}s before retrying...")
                await asyncio.sleep(self.cooldown_seconds)
                
                attempt += 1
            
            # Generate final report
            logger.info("Generating test report...")
            fix_stats = self.auto_fixer.get_fix_statistics()
            report_path = self.reporter.generate_report(
                test_results=self.runner.all_results,
                analyses=self.current_analyses,
                failure_patterns=fix_stats
            )
            
            # Final status
            if success:
                logger.info("🎉 All tests passing after fixes!")
            else:
                logger.warning("⚠️ Some tests still failing after maximum fix attempts")
                
            logger.info(f"Test cycle complete! Report available at: {report_path}")
            return success
            
        except Exception as e:
            logger.error(f"Error during test cycle: {e}")
            return False

async def main():
    """Main entry point for the test cycle automation."""
    
    # Get test directory from arguments or use default
    test_dir = sys.argv[1] if len(sys.argv) > 1 else os.getenv(
        'TEST_DIR',
        '/Users/sherwingorechomante/Sprintsense/frontend/tests/e2e'
    )
    
    if not os.path.exists(test_dir):
        logger.error(f"Test directory {test_dir} does not exist!")
        sys.exit(1)
    
    # Create and run test cycle
    cycle = TestCycle(
        test_dir=test_dir,
        max_retries=3,
        max_fix_attempts=3,
        cooldown_seconds=5
    )
    
    success = await cycle.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    asyncio.run(main())
