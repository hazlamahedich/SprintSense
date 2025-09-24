"""Warp-integrated LLM-powered test fixing module."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .analyzer import FailureAnalysis
from .runner import TestResult

@dataclass
class WarpLLMFixAttempt:
    """Represents a Warp LLM-powered fix attempt."""
    test_name: str
    error_category: str
    original_error: str
    original_code: str
    suggested_fix: str
    fix_explanation: str
    confidence: float
    changes_made: List[Dict[str, str]]
    success: bool = False

    def to_dict(self) -> dict:
        """Convert the fix attempt to a dictionary."""
        return {
            'test_name': self.test_name,
            'error_category': self.error_category,
            'original_error': self.original_error,
            'original_code': self.original_code,
            'suggested_fix': self.suggested_fix,
            'fix_explanation': self.fix_explanation,
            'confidence': self.confidence,
            'changes_made': self.changes_made,
            'success': self.success
        }

class WarpLLMFixer:
    """Uses Warp's built-in LLM to analyze and fix test failures intelligently."""

    def __init__(self, test_root: str):
        self.test_root = Path(test_root)
        self.fix_history: List[WarpLLMFixAttempt] = []

        # Load known fix patterns for context
        self.fix_patterns = {
            'selector': [
                "Consider using more stable selectors (data-testid, id)",
                "Add explicit wait conditions",
                "Check element visibility",
                "Handle iframes or shadow DOM"
            ],
            'timeout': [
                "Increase timeout duration",
                "Add explicit wait conditions",
                "Handle loading states",
                "Check for performance bottlenecks"
            ],
            'network': [
                "Implement retry logic",
                "Handle request timeouts",
                "Mock network requests",
                "Use test data fixtures"
            ],
            'assertion': [
                "Validate test assumptions",
                "Check data setup",
                "Use appropriate matchers",
                "Handle async state updates"
            ]
        }

    async def attempt_fix(self, test_result: TestResult, analysis: FailureAnalysis) -> Optional[WarpLLMFixAttempt]:
        """Attempt to fix a failing test using Warp's LLM."""
        if not test_result or not analysis:
            return None

        logger.info(f"Analyzing test failure with Warp LLM: {test_result.test_name}")

        try:
            # Find the test file and extract relevant code
            test_file = self._find_test_file(test_result.test_name)
            if not test_file:
                return None

            # Get the test code and surrounding context
            test_code, context = await self._extract_test_context(test_file, test_result.test_name)
            if not test_code:
                return None

            # Get fix suggestion from Warp LLM
            fix_attempt = await self._get_warp_llm_fix_suggestion(
                test_result,
                analysis,
                test_code,
                context
            )

            if fix_attempt and fix_attempt.suggested_fix:
                # Apply the suggested fix
                await self._apply_fix(test_file, fix_attempt)

                # Record the fix attempt
                self.fix_history.append(fix_attempt)
                return fix_attempt

        except Exception as e:
            logger.error(f"Error during Warp LLM fix attempt: {e}")

        return None

    async def _get_warp_llm_fix_suggestion(
        self,
        test_result: TestResult,
        analysis: FailureAnalysis,
        test_code: str,
        context: str
    ) -> Optional[WarpLLMFixAttempt]:
        """Get fix suggestion using Warp's built-in LLM through search_codebase."""

        # Prepare the query
        query = self._create_fix_query(
            test_result,
            analysis,
            test_code,
            context
        )

        try:
            # Create a temporary file with the query for search_codebase
            query_file = self.test_root / '.temp_fix_query.md'
            query_file.write_text(query)

            # Use search_codebase to get LLM response
            import warp_tools
            response = await warp_tools.search_codebase(
                query=query,
                codebase_path=str(self.test_root),
                path_filters=['*.spec.ts']
            )

            # Parse the response
            if response and isinstance(response, str):
                # Extract fix components
                fix_components = self._parse_warp_llm_response(response)

                return WarpLLMFixAttempt(
                    test_name=test_result.test_name,
                    error_category=analysis.error_category,
                    original_error=test_result.error_message or "",
                    original_code=test_code,
                    suggested_fix=fix_components['code'],
                    fix_explanation=fix_components['explanation'],
                    confidence=fix_components['confidence'],
                    changes_made=[]
                )

        except Exception as e:
            logger.error(f"Error getting Warp LLM suggestion: {e}")

        return None

    def _create_fix_query(
        self,
        test_result: TestResult,
        analysis: FailureAnalysis,
        test_code: str,
        context: str
    ) -> str:
        """Create a query for Warp's LLM."""

        # Get relevant fix patterns for context
        relevant_patterns = self.fix_patterns.get(analysis.error_category, [])

        query = f"""
As an expert test automation engineer, analyze this Playwright test failure and suggest specific fixes.

Test: {test_result.test_name}
Error Category: {analysis.error_category}
Error Message: {test_result.error_message}

Test Code:
```typescript
{test_code}
```

Relevant Context:
```typescript
{context}
```

Known fix patterns for this type of issue:
{chr(10).join(f"- {pattern}" for pattern in relevant_patterns)}

Please provide:
1. A specific code fix that addresses the root cause
2. An explanation of why this fix should work
3. A confidence score (0-1) for this fix
4. Any additional test improvements

Format your response exactly as:
---
CONFIDENCE: <score>
EXPLANATION: <explanation>
CODE:
```typescript
<fixed code>
```
IMPROVEMENTS:
- <additional improvement 1>
- <additional improvement 2>
---
"""
        return query

    def _parse_warp_llm_response(self, response: str) -> Dict[str, any]:
        """Parse Warp LLM's response into components."""
        components = {
            'confidence': 0.0,
            'explanation': "",
            'code': "",
            'improvements': []
        }

        try:
            # Extract section between ---
            if '---' in response:
                content = response.split('---')[1].strip()
                lines = content.split('\n')

                current_section = None
                current_content = []

                for line in lines:
                    line = line.strip()
                    if line.startswith('CONFIDENCE:'):
                        try:
                            components['confidence'] = float(line.split(':')[1].strip())
                        except ValueError:
                            pass
                    elif line.startswith('EXPLANATION:'):
                        current_section = 'explanation'
                        current_content = []
                    elif line.startswith('CODE:'):
                        current_section = 'code'
                        current_content = []
                    elif line.startswith('IMPROVEMENTS:'):
                        current_section = 'improvements'
                        current_content = []
                    elif line.startswith('```') and current_section == 'code':
                        continue
                    elif line and current_section:
                        current_content.append(line)

                    if current_section == 'explanation':
                        components['explanation'] = ' '.join(current_content)
                    elif current_section == 'code':
                        components['code'] = '\n'.join(current_content)
                    elif current_section == 'improvements':
                        components['improvements'] = [
                            imp.lstrip('- ') for imp in current_content if imp.startswith('-')
                        ]

        except Exception as e:
            logger.error(f"Error parsing Warp LLM response: {e}")

        return components

    async def _apply_fix(self, test_file: Path, fix_attempt: WarpLLMFixAttempt):
        """Apply the suggested fix to the test file."""
        try:
            content = test_file.read_text()

            # Replace the test code with the fix
            updated_content = content.replace(
                fix_attempt.original_code.strip(),
                fix_attempt.suggested_fix.strip()
            )

            if updated_content != content:
                # Backup original file
                backup_path = test_file.with_suffix('.bak')
                test_file.rename(backup_path)

                # Write updated content
                test_file.write_text(updated_content)

                fix_attempt.changes_made.append({
                    'file': str(test_file),
                    'change': 'Updated test code with Warp LLM suggestion',
                    'backup': str(backup_path)
                })

        except Exception as e:
            logger.error(f"Error applying fix: {e}")

    def _find_test_file(self, test_name: str) -> Optional[Path]:
        """Find the test file containing the specified test."""
        for test_file in self.test_root.rglob('*.spec.ts'):
            content = test_file.read_text()
            if f"test('{test_name}'" in content or f'test("{test_name}"' in content:
                return test_file
        return None

    async def _extract_test_context(self, test_file: Path, test_name: str) -> Tuple[str, str]:
        """Extract the test code and relevant context."""
        content = test_file.read_text()
        lines = content.split('\n')

        test_start = None
        test_end = None

        # Find the test boundaries
        for i, line in enumerate(lines):
            if f"test('{test_name}'" in line or f'test("{test_name}"' in line:
                test_start = i
                # Find the closing brace
                bracket_count = 0
                for j in range(i, len(lines)):
                    if '{' in lines[j]:
                        bracket_count += 1
                    if '}' in lines[j]:
                        bracket_count -= 1
                        if bracket_count == 0:
                            test_end = j + 1
                            break
                break

        if test_start is None or test_end is None:
            return "", ""

        # Get the test code
        test_code = '\n'.join(lines[test_start:test_end])

        # Get surrounding context (imports, beforeEach, etc.)
        context_start = max(0, test_start - 20)
        context_end = min(len(lines), test_end + 20)
        context = '\n'.join(lines[context_start:context_end])

        return test_code, context

    def get_fix_statistics(self) -> Dict[str, dict]:
        """Get statistics about Warp LLM fix attempts."""
        if not self.fix_history:
            return {}

        stats = {
            'total_fixes': len(self.fix_history),
            'successful_fixes': sum(1 for fix in self.fix_history if fix.success),
            'by_category': {},
            'confidence_metrics': {
                'average': sum(fix.confidence for fix in self.fix_history) / len(self.fix_history),
                'high_confidence': sum(1 for fix in self.fix_history if fix.confidence > 0.8),
                'medium_confidence': sum(1 for fix in self.fix_history if 0.5 <= fix.confidence <= 0.8),
                'low_confidence': sum(1 for fix in self.fix_history if fix.confidence < 0.5)
            }
        }

        # Track by category
        for fix in self.fix_history:
            if fix.error_category not in stats['by_category']:
                stats['by_category'][fix.error_category] = {
                    'total': 0,
                    'successful': 0,
                    'average_confidence': 0.0
                }

            cat_stats = stats['by_category'][fix.error_category]
            cat_stats['total'] += 1
            if fix.success:
                cat_stats['successful'] += 1
            cat_stats['average_confidence'] = (
                (cat_stats['average_confidence'] * (cat_stats['total'] - 1) + fix.confidence)
                / cat_stats['total']
            )

        return stats
