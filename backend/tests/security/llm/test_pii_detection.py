"""Tests for PII detection and redaction."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.core.security.llm.pii_detection import PIIDetector, PIIDetectionMiddleware

@pytest.fixture
def mock_comprehend():
    """Create a mock AWS Comprehend client."""
    with patch('boto3.client') as mock:
        with patch.dict('os.environ', {
            'AWS_ACCESS_KEY_ID': 'test',
            'AWS_SECRET_ACCESS_KEY': 'test',
            'AWS_DEFAULT_REGION': 'us-east-1'
        }):
            comprehend = MagicMock()
            mock.return_value = comprehend
            yield comprehend

@pytest.fixture
def pii_detector(mock_comprehend):
    """Create a PIIDetector instance with mocked AWS client."""
    return PIIDetector()

@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    app = FastAPI()
    app.add_middleware(PIIDetectionMiddleware)

    from pydantic import BaseModel

    class CompletionRequest(BaseModel):
        text: str

    @app.post("/api/v1/llm/complete")
    async def test_endpoint(request: CompletionRequest):
        return JSONResponse({"result": request.text})

    return TestClient(app)

class TestPIIDetector:
    """Test the PIIDetector class."""

    def test_detect_email(self, pii_detector):
        """Test email detection."""
        text = "Contact me at user@example.com"
        pii = pii_detector.detect_pii(text)

        assert len(pii) == 1
        assert pii[0][0] == "email"
        assert pii[0][1] == "user@example.com"

    def test_detect_phone(self, pii_detector):
        """Test phone number detection."""
        text = "Call me at +1234567890"
        pii = pii_detector.detect_pii(text)

        assert len(pii) == 1
        assert pii[0][0] == "phone"
        assert pii[0][1] == "+1234567890"

    def test_detect_ssn(self, pii_detector):
        """Test SSN detection."""
        text = "SSN: 123-45-6789"
        pii = pii_detector.detect_pii(text)

        assert len(pii) == 1
        assert pii[0][0] == "ssn"
        assert pii[0][1] == "123-45-6789"

    def test_detect_credit_card(self, pii_detector):
        """Test credit card number detection."""
        text = "Card: 4111-1111-1111-1111"
        pii = pii_detector.detect_pii(text)

        assert len(pii) == 1
        assert pii[0][0] == "credit_card"
        assert pii[0][1] == "4111-1111-1111-1111"

    def test_detect_multiple_pii(self, pii_detector):
        """Test detection of multiple PII types."""
        text = "Contact: user@example.com, phone: +1234567890"
        pii = pii_detector.detect_pii(text)

        assert len(pii) == 2
        types = {p[0] for p in pii}
        assert types == {"email", "phone"}

    def test_redact_pii(self, pii_detector):
        """Test PII redaction."""
        text = "Email: user@example.com, SSN: 123-45-6789"
        redacted, types = pii_detector.redact_pii(text, '*')

        assert "user@example.com" not in redacted
        assert "123-45-6789" not in redacted
        assert "***@******" in redacted or "*************" in redacted
        assert set(types) == {"email", "ssn"}

    def test_get_pii_stats(self, pii_detector):
        """Test PII statistics generation."""
        text = """
        Email: user1@example.com
        Alt Email: user2@example.com
        Phone: +1234567890
        """
        stats = pii_detector.get_pii_stats(text)

        assert stats["email"] == 2
        assert stats["phone"] == 1

    def test_aws_comprehend_integration(self, pii_detector, mock_comprehend):
        """Test AWS Comprehend integration."""
        mock_comprehend.detect_pii_entities.return_value = {
            'Entities': [
                {
                    'Type': 'NAME',
                    'BeginOffset': 0,
                    'EndOffset': 10,
                }
            ]
        }

        text = "John Smith is a user"
        pii = pii_detector.detect_pii(text)

        assert mock_comprehend.detect_pii_entities.called
        assert len(pii) == 1
        assert pii[0][0] == "NAME"

    def test_aws_comprehend_fallback(self, pii_detector, mock_comprehend):
        """Test fallback to regex when AWS fails."""
        mock_comprehend.detect_pii_entities.side_effect = Exception("AWS Error")

        text = "Email: user@example.com"
        pii = pii_detector.detect_pii(text)

        assert len(pii) == 1  # Still detects email via regex
        assert pii[0][0] == "email"

class TestPIIDetectionMiddleware:
    """Test the PII detection middleware."""

    def test_middleware_redacts_pii(self, test_app):
        """Test that middleware redacts PII from requests."""
        response = test_app.post(
            "/api/v1/llm/complete",
            json={"text": "My email is user@example.com"}
        )

        assert response.status_code == 200
        assert "user@example.com" not in response.text
        assert "********" in response.text or "*****" in response.text

    def test_middleware_ignores_non_llm_paths(self, test_app):
        """Test that middleware only processes LLM endpoints."""
        @test_app.app.post("/api/v1/other")
        async def other_endpoint():
            return JSONResponse({"text": "user@example.com"})

        response = test_app.post(
            "/api/v1/other",
            json={"text": "user@example.com"}
        )

        assert response.status_code == 200
        assert "user@example.com" in response.text

    def test_middleware_handles_no_pii(self, test_app):
        """Test middleware behavior with no PII."""
        text = "This is a safe text"
        response = test_app.post(
            "/api/v1/llm/complete",
            json={"text": text}
        )

        assert response.status_code == 200
        assert text in response.text

    def test_middleware_error_handling(self, test_app):
        """Test middleware error handling."""
        with patch('app.core.security.llm.pii_detection.PIIDetector.redact_pii') as mock:
            mock.side_effect = Exception("PII Detection Error")

            response = test_app.post(
                "/api/v1/llm/complete",
                json={"text": "test"}
            )

            assert response.status_code != 500  # Should not propagate errors