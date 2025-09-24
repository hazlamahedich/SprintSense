"""Auto-fix module for automatically fixing common test failures."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .analyzer import FailureAnalysis
from .runner import TestResult

logger = logging.getLogger(__name__)

@dataclass
class FixAttempt:
    """Represents an attempt to fix a test failure."""
    test_name: str
    error_category: str
    original_error: str
    fix_strategy: str
    changes_made: List[Dict[str, str]]
    success: bool = False

    def to_dict(self) -> dict:
        """Convert the fix attempt to a dictionary."""
        return {
            'test_name': self.test_name,
            'error_category': self.error_category,
            'original_error': self.original_error,
            'fix_strategy': self.fix_strategy,
            'changes_made': self.changes_made,
            'success': self.success
        }

class AutoFixer:
    """Implements automatic fixes for common test failures."""
    
    SELECTOR_FIXES = {
        'data-testid': r'data-testid=["\']([^"\']+)["\']',
        'id': r'id=["\']([^"\']+)["\']',
        'class': r'class=["\']([^"\']+)["\']',
        'aria-label': r'aria-label=["\']([^"\']+)["\']'
    }
    
    TIMEOUT_FIXES = {
        'networkidle': 'waitUntil: "networkidle"',
        'domcontentloaded': 'waitUntil: "domcontentloaded"',
        'load': 'waitUntil: "load"'
    }
    
    def __init__(self, test_root: str):
        self.test_root = Path(test_root)
        self.fix_history: List[FixAttempt] = []
    
    async def attempt_fix(self, test_result: TestResult, analysis: FailureAnalysis) -> Optional[FixAttempt]:
        """Attempt to fix a failing test based on its analysis."""
        if not test_result or not analysis:
            return None
            
        logger.info(f"Attempting to fix test: {test_result.test_name}")
        logger.info(f"Error category: {analysis.error_category}")
        
        fix_attempt = FixAttempt(
            test_name=test_result.test_name,
            error_category=analysis.error_category,
            original_error=test_result.error_message or "",
            fix_strategy="",
            changes_made=[]
        )
        
        try:
            if analysis.error_category == 'selector':
                await self._fix_selector_issue(test_result, fix_attempt)
            elif analysis.error_category == 'timeout':
                await self._fix_timeout_issue(test_result, fix_attempt)
            elif analysis.error_category == 'network':
                await self._fix_network_issue(test_result, fix_attempt)
            elif analysis.error_category == 'assertion':
                await self._fix_assertion_issue(test_result, fix_attempt)
            
            # Record the fix attempt
            self.fix_history.append(fix_attempt)
            return fix_attempt
            
        except Exception as e:
            logger.error(f"Error attempting fix: {e}")
            return None
    
    async def _fix_selector_issue(self, test_result: TestResult, fix_attempt: FixAttempt):
        """Fix selector-related issues."""
        # Find the test file
        test_file = self._find_test_file(test_result.test_name)
        if not test_file:
            return
            
        content = test_file.read_text()
        original_content = content
        
        # Extract problematic selector from error message
        selector_match = re.search(r'selector ["\'](.*?)["\']', test_result.error_message or "")
        if not selector_match:
            return
            
        problematic_selector = selector_match.group(1)
        fix_attempt.fix_strategy = f"Updating selector: {problematic_selector}"
        
        # Try different selector strategies
        for attr, pattern in self.SELECTOR_FIXES.items():
            # Look for elements with the attribute in the app code
            element_match = re.search(pattern, content)
            if element_match:
                new_selector = f'[{attr}="{element_match.group(1)}"]'
                content = content.replace(problematic_selector, new_selector)
                fix_attempt.changes_made.append({
                    'file': str(test_file),
                    'change': f"Updated selector from '{problematic_selector}' to '{new_selector}'"
                })
                break
        
        # Add wait condition if not present
        if 'await page.waitForSelector' not in content:
            content = self._add_wait_condition(content, problematic_selector)
            fix_attempt.changes_made.append({
                'file': str(test_file),
                'change': f"Added wait condition for selector: {problematic_selector}"
            })
        
        if content != original_content:
            test_file.write_text(content)
    
    async def _fix_timeout_issue(self, test_result: TestResult, fix_attempt: FixAttempt):
        """Fix timeout-related issues."""
        test_file = self._find_test_file(test_result.test_name)
        if not test_file:
            return
            
        content = test_file.read_text()
        original_content = content
        
        # Add appropriate wait conditions
        for strategy, wait_option in self.TIMEOUT_FIXES.items():
            if strategy not in content:
                content = content.replace(
                    'await page.goto(',
                    f'await page.goto({{ {wait_option} }},'
                )
                fix_attempt.changes_made.append({
                    'file': str(test_file),
                    'change': f"Added wait condition: {wait_option}"
                })
        
        # Increase timeout if needed
        if 'timeout' not in content:
            content = content.replace(
                'test(',
                'test({ timeout: 60000 },'
            )
            fix_attempt.changes_made.append({
                'file': str(test_file),
                'change': "Increased test timeout to 60000ms"
            })
        
        if content != original_content:
            test_file.write_text(content)
            fix_attempt.fix_strategy = "Added wait conditions and increased timeouts"
    
    async def _fix_network_issue(self, test_result: TestResult, fix_attempt: FixAttempt):
        """Fix network-related issues."""
        test_file = self._find_test_file(test_result.test_name)
        if not test_file:
            return
            
        content = test_file.read_text()
        original_content = content
        
        # Add network error handling
        if 'try {' not in content:
            content = self._add_network_retry(content)
            fix_attempt.changes_made.append({
                'file': str(test_file),
                'change': "Added network retry logic"
            })
        
        if content != original_content:
            test_file.write_text(content)
            fix_attempt.fix_strategy = "Added network error handling and retry logic"
    
    async def _fix_assertion_issue(self, test_result: TestResult, fix_attempt: FixAttempt):
        """Fix assertion-related issues."""
        test_file = self._find_test_file(test_result.test_name)
        if not test_file:
            return
            
        content = test_file.read_text()
        original_content = content
        
        # Extract expected and actual values
        assertion_match = re.search(
            r'Expected (.*) but got (.*)',
            test_result.error_message or ""
        )
        
        if assertion_match:
            expected, actual = assertion_match.groups()
            # Add more flexible assertion
            content = content.replace(
                f'expect({actual}).toBe({expected})',
                f'expect({actual}).toMatch({expected})'
            )
            fix_attempt.changes_made.append({
                'file': str(test_file),
                'change': f"Updated assertion to be more flexible: {actual} → {expected}"
            })
        
        if content != original_content:
            test_file.write_text(content)
            fix_attempt.fix_strategy = "Updated assertions to be more flexible"
    
    def _find_test_file(self, test_name: str) -> Optional[Path]:
        """Find the test file containing the specified test."""
        for test_file in self.test_root.rglob('*.spec.ts'):
            content = test_file.read_text()
            if f"test('{test_name}'" in content or f'test("{test_name}"' in content:
                return test_file
        return None
    
    def _add_wait_condition(self, content: str, selector: str) -> str:
        """Add a wait condition for a selector."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if selector in line and 'page.' in line:
                indent = len(line) - len(line.lstrip())
                wait_line = ' ' * indent + f'await page.waitForSelector("{selector}", {{ state: "visible" }});'
                lines.insert(i, wait_line)
                break
        return '\n'.join(lines)
    
    def _add_network_retry(self, content: str) -> str:
        """Add network retry logic to a test."""
        lines = content.split('\n')
        new_lines = []
        in_test = False
        
        for line in lines:
            if 'test(' in line:
                in_test = True
                new_lines.append(line)
                indent = len(line) - len(line.lstrip())
                new_lines.extend([
                    ' ' * (indent + 2) + 'const maxRetries = 3;',
                    ' ' * (indent + 2) + 'for (let attempt = 1; attempt <= maxRetries; attempt++) {',
                    ' ' * (indent + 4) + 'try {'
                ])
            elif in_test and '});' in line:
                indent = len(line) - len(line.lstrip())
                new_lines.extend([
                    ' ' * (indent + 4) + '} catch (error) {',
                    ' ' * (indent + 6) + 'if (attempt === maxRetries) throw error;',
                    ' ' * (indent + 6) + 'console.log(`Attempt ${attempt} failed, retrying...`);',
                    ' ' * (indent + 6) + 'await new Promise(r => setTimeout(r, 1000));',
                    ' ' * (indent + 4) + '}',
                    ' ' * (indent + 2) + '}',
                    line
                ])
                in_test = False
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def get_fix_statistics(self) -> Dict[str, dict]:
        """Get statistics about fix attempts."""
        if not self.fix_history:
            return {}
            
        stats = {
            'total_fixes': len(self.fix_history),
            'successful_fixes': sum(1 for fix in self.fix_history if fix.success),
            'by_category': {},
            'most_common_fixes': {}
        }
        
        for fix in self.fix_history:
            # Track by category
            if fix.error_category not in stats['by_category']:
                stats['by_category'][fix.error_category] = {
                    'total': 0,
                    'successful': 0
                }
            stats['by_category'][fix.error_category]['total'] += 1
            if fix.success:
                stats['by_category'][fix.error_category]['successful'] += 1
            
            # Track common fixes
            if fix.fix_strategy not in stats['most_common_fixes']:
                stats['most_common_fixes'][fix.fix_strategy] = 0
            stats['most_common_fixes'][fix.fix_strategy] += 1
        
        return stats