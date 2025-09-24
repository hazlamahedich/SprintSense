"""Failure analysis module for categorizing and analyzing test failures."""

import logging
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional

from .runner import TestResult

logger = logging.getLogger(__name__)

@dataclass
class FailureAnalysis:
    """Contains analysis results for a test failure."""
    error_type: str
    error_category: str
    suggested_fix: Optional[str] = None
    confidence: float = 0.0
    pattern_matches: List[str] = None

    def to_dict(self) -> dict:
        """Convert the analysis to a dictionary."""
        return {
            'error_type': self.error_type,
            'error_category': self.error_category,
            'suggested_fix': self.suggested_fix,
            'confidence': self.confidence,
            'pattern_matches': self.pattern_matches or []
        }

class FailureAnalyzer:
    """Analyzes test failures to categorize issues and identify patterns."""
    
    # Error patterns for different categories
    ERROR_PATTERNS = {
        'selector': [
            r"Unable to locate element.*selector.*",
            r"Element.*not found.*",
            r"Element.*is not visible.*"
        ],
        'timeout': [
            r"Timeout.*waiting for.*",
            r"Operation timed out.*",
            r"Page load timeout.*"
        ],
        'network': [
            r"Network.*error.*",
            r"Failed to fetch.*",
            r"API.*request failed.*"
        ],
        'assertion': [
            r"AssertionError.*",
            r"Expected.*but got.*",
            r".*should.*but.*"
        ]
    }
    
    COMMON_FIXES = {
        'selector': [
            "Update selector to use more stable attributes",
            "Add wait condition for element visibility",
            "Check if element is in correct iframe/shadow DOM"
        ],
        'timeout': [
            "Increase timeout duration",
            "Add explicit wait conditions",
            "Check for performance issues"
        ],
        'network': [
            "Verify API endpoint availability",
            "Check network conditions",
            "Implement retry mechanism"
        ],
        'assertion': [
            "Review expected vs actual values",
            "Check test data setup",
            "Verify test assumptions"
        ]
    }
    
    def __init__(self):
        self.failure_history: List[TestResult] = []
    
    def analyze_failure(self, test_result: TestResult) -> FailureAnalysis:
        """Analyze a single test failure."""
        if not test_result.error_message:
            return None
            
        # Find matching error category
        error_category = self._categorize_error(test_result.error_message)
        pattern_matches = self._find_pattern_matches(test_result.error_message)
        
        # Calculate confidence based on pattern matches
        confidence = len(pattern_matches) / (len(self.ERROR_PATTERNS[error_category]) if error_category else 1)
        
        # Get suggested fix
        suggested_fix = self._get_suggested_fix(error_category) if error_category else None
        
        analysis = FailureAnalysis(
            error_type=test_result.error_type or 'unknown',
            error_category=error_category or 'unknown',
            suggested_fix=suggested_fix,
            confidence=confidence,
            pattern_matches=pattern_matches
        )
        
        # Add to history for pattern analysis
        self.failure_history.append(test_result)
        
        return analysis
    
    def get_failure_patterns(self) -> Dict[str, dict]:
        """Analyze patterns in failure history."""
        if not self.failure_history:
            return {}
            
        patterns = {
            'categories': Counter(),
            'most_failed_tests': Counter(),
            'retry_statistics': {
                'total_retries': sum(t.retry_count for t in self.failure_history),
                'success_after_retry': sum(1 for t in self.failure_history if t.status == 'passed' and t.retry_count > 0)
            }
        }
        
        for failure in self.failure_history:
            analysis = self.analyze_failure(failure)
            if analysis:
                patterns['categories'][analysis.error_category] += 1
            patterns['most_failed_tests'][failure.test_name] += 1
        
        # Calculate success rate after retries
        if patterns['retry_statistics']['total_retries'] > 0:
            patterns['retry_statistics']['retry_success_rate'] = (
                patterns['retry_statistics']['success_after_retry'] /
                patterns['retry_statistics']['total_retries']
            )
        
        return patterns
    
    def _categorize_error(self, error_message: str) -> Optional[str]:
        """Categorize an error message based on pattern matching."""
        for category, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return category
        return None
    
    def _find_pattern_matches(self, error_message: str) -> List[str]:
        """Find all patterns that match the error message."""
        matches = []
        for category, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    matches.append(pattern)
        return matches
    
    def _get_suggested_fix(self, error_category: str) -> Optional[str]:
        """Get a suggested fix for an error category."""
        if error_category in self.COMMON_FIXES:
            fixes = self.COMMON_FIXES[error_category]
            return fixes[0] if fixes else None
        return None