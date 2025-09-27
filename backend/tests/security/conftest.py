"""Test configuration for security tests."""

from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.stub import Stubber
from moto import mock_aws
from redis import Redis

# Ensure AWS region is set for boto3 clients
import os
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security.llm.rbac import Base

# Create in-memory test database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture
def db():
    """Create a fresh test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def redis():
    """Create a mock Redis client with pipeline behavior."""
    mock_redis = MagicMock(spec=Redis)
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.scan_iter.return_value = []
    mock_redis.incr.return_value = 1

    # Pipeline mock
    pipeline = MagicMock()
    pipeline.setex.return_value = pipeline
    pipeline.get.return_value = pipeline
    pipeline.incr.return_value = pipeline
    pipeline.execute.return_value = [True, True]
    mock_redis.pipeline.return_value = pipeline

    # Some tests call execute directly on redis mock
    mock_redis.execute = pipeline.execute

    yield mock_redis

@pytest.fixture(scope="function")
def aws_credentials():
    """Create mock AWS credentials for moto."""
    with patch.dict(
        "os.environ",
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1"
        }
    ):
        yield

@pytest.fixture
@mock_aws
def secrets_manager(aws_credentials):
    """Create a mocked AWS Secrets Manager client using mock_aws."""
    client = boto3.client("secretsmanager", region_name="us-east-1")
    client.create_secret(
        Name="sprintsense/llm/api-keys",
        SecretString='{"openai": "test-key", "anthropic": "test-key"}'
    )
    yield client

@pytest.fixture
@mock_aws
def comprehend(aws_credentials):
    """Create a mocked AWS Comprehend client using mock_aws and stub responses."""
    client = boto3.client("comprehend", region_name="us-east-1")
    with Stubber(client) as stubber:
        stubber.add_response(
            "detect_pii_entities",
            {
                "Entities": [
                    {
                        "Score": 0.99,
                        "Type": "EMAIL",
                        "BeginOffset": 0,
                        "EndOffset": 10
                    }
                ]
            },
            {"Text": "test@example.com", "LanguageCode": "en"}
        )
        yield client

@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    with patch("app.core.logging.logger") as mock:
        yield mock