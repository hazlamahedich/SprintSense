"""Test reporter module for generating comprehensive test reports."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import jinja2
from jinja2 import Template

from .analyzer import FailureAnalysis
from .runner import TestResult

logger = logging.getLogger(__name__)

class TestReporter:
    """Generates comprehensive HTML reports for test results."""

    REPORT_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>E2E Test Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .summary {
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            .status-passed { color: #28a745; }
            .status-failed { color: #dc3545; }
            .status-skipped { color: #ffc107; }
            .test-result {
                margin: 10px 0;
                padding: 15px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            .artifacts {
                margin-top: 10px;
                padding: 10px;
                background-color: #f8f9fa;
            }
            .analysis {
                margin-top: 20px;
                padding: 20px;
                background-color: #e9ecef;
                border-radius: 5px;
            }
            .chart {
                margin: 20px 0;
                height: 300px;
            }
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>E2E Test Report</h1>

            <div class="summary">
                <h2>Summary</h2>
                <p>
                    <strong>Total Tests:</strong> {{ summary.total_tests }}<br>
                    <strong>Passed:</strong> <span class="status-passed">{{ summary.passed_tests }}</span><br>
                    <strong>Failed:</strong> <span class="status-failed">{{ summary.failed_tests }}</span><br>
                    <strong>Skipped:</strong> <span class="status-skipped">{{ summary.skipped_tests }}</span><br>
                    <strong>Duration:</strong> {{ summary.duration }}<br>
                    <strong>Timestamp:</strong> {{ summary.timestamp }}
                </p>
            </div>

            {% if failure_patterns %}
            <div class="analysis">
                <h2>Failure Analysis</h2>
                <div id="categoryChart" class="chart"></div>
                <div id="retryChart" class="chart"></div>

                <h3>Most Common Issues</h3>
                <ul>
                {% for category, count in failure_patterns.categories.most_common() %}
                    <li><strong>{{ category }}:</strong> {{ count }} occurrences</li>
                {% endfor %}
                </ul>

                <h3>Retry Statistics</h3>
                <p>
                    <strong>Total Retries:</strong> {{ failure_patterns.retry_statistics.total_retries }}<br>
                    <strong>Success After Retry:</strong> {{ failure_patterns.retry_statistics.success_after_retry }}<br>
                    <strong>Retry Success Rate:</strong> {{ "%.2f"|format(failure_patterns.retry_statistics.retry_success_rate * 100) }}%
                </p>
            </div>
            {% endif %}

            <h2>Test Results</h2>
            {% for result in results %}
            <div class="test-result">
                <h3>{{ result.test_name }}</h3>
                <p class="status-{{ result.status.lower() }}">
                    <strong>Status:</strong> {{ result.status }}<br>
                    <strong>Duration:</strong> {{ "%.2f"|format(result.duration) }}s<br>
                    <strong>Retries:</strong> {{ result.retry_count }}
                </p>

                {% if result.error_message %}
                <div class="error">
                    <strong>Error:</strong><br>
                    <pre>{{ result.error_message }}</pre>
                </div>
                {% endif %}

                {% if result.artifacts %}
                <div class="artifacts">
                    <h4>Artifacts</h4>
                    <ul>
                    {% for type, path in result.artifacts.items() %}
                        <li><a href="{{ path }}" target="_blank">{{ type }}</a></li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}

                {% if analyses.get(result.test_name) %}
                <div class="analysis">
                    <h4>Analysis</h4>
                    {% with analysis = analyses.get(result.test_name) %}
                    <p>
                        <strong>Error Category:</strong> {{ analysis.error_category }}<br>
                        <strong>Confidence:</strong> {{ "%.2f"|format(analysis.confidence * 100) }}%<br>
                        {% if analysis.suggested_fix %}
                        <strong>Suggested Fix:</strong> {{ analysis.suggested_fix }}
                        {% endif %}
                    </p>
                    {% endwith %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        {% if failure_patterns %}
        <script>
            // Create category distribution chart
            var categoryData = {{ failure_patterns.categories | tojson }};
            var categoryChart = {
                type: 'pie',
                values: Object.values(categoryData),
                labels: Object.keys(categoryData),
                title: 'Error Categories Distribution'
            };
            Plotly.newPlot('categoryChart', [categoryChart]);

            // Create retry success chart
            var retryStats = {{ failure_patterns.retry_statistics | tojson }};
            var retryChart = {
                type: 'bar',
                x: ['Total Retries', 'Successful Retries'],
                y: [retryStats.total_retries, retryStats.success_after_retry],
                title: 'Retry Statistics'
            };
            Plotly.newPlot('retryChart', [retryChart]);
        </script>
        {% endif %}
    </body>
    </html>
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path('test-reports')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        self.jinja_env = jinja2.Environment()
        self.template = self.jinja_env.from_string(self.REPORT_TEMPLATE)

    def generate_report(
        self,
        test_results: List[TestResult],
        analyses: Dict[str, FailureAnalysis],
        failure_patterns: Optional[dict] = None
    ) -> str:
        """Generate HTML report from test results and analyses."""

        # Calculate summary statistics
        summary = {
            'total_tests': len(test_results),
            'passed_tests': sum(1 for r in test_results if r.status == 'passed'),
            'failed_tests': sum(1 for r in test_results if r.status == 'failed'),
            'skipped_tests': sum(1 for r in test_results if r.status == 'skipped'),
            'duration': sum(r.duration for r in test_results),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Generate HTML report
        html_content = self.template.render(
            summary=summary,
            results=test_results,
            analyses=analyses,
            failure_patterns=failure_patterns
        )

        # Save HTML report
        report_path = self.output_dir / 'report.html'
        report_path.write_text(html_content)

        # Save JSON data for potential further processing
        data = {
            'summary': summary,
            'results': [r.to_dict() for r in test_results],
            'analyses': {k: v.to_dict() for k, v in analyses.items()} if analyses else {},
            'failure_patterns': failure_patterns
        }

        json_path = self.output_dir / 'report.json'
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Report generated at {report_path}")
        logger.info(f"JSON data saved at {json_path}")

        return str(report_path)

    def save_artifacts(self, artifacts: Dict[str, str]):
        """Save test artifacts to the report directory."""
        artifacts_dir = self.output_dir / 'artifacts'
        artifacts_dir.mkdir(exist_ok=True)

        for name, content in artifacts.items():
            artifact_path = artifacts_dir / name
            if isinstance(content, (str, bytes)):
                artifact_path.write_bytes(content.encode() if isinstance(content, str) else content)
            elif isinstance(content, Path):
                import shutil
                shutil.copy(str(content), str(artifact_path))

        return artifacts_dir