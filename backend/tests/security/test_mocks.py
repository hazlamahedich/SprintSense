"""Tests for mocked AWS services."""

import boto3
from moto import mock_aws

@mock_aws
def test_secrets_manager():
    """Test Secrets Manager mocking."""
    client = boto3.client('secretsmanager')

    # Create test secret
    resp = client.create_secret(
        Name='test/secret',
        SecretString='{"key": "value"}'
    )
    assert 'ARN' in resp

    # Get secret value
    resp = client.get_secret_value(SecretId='test/secret')
    assert resp['SecretString'] == '{"key": "value"}'