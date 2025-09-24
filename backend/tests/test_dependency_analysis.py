from unittest.mock import MagicMock, patch

import pytest
import torch

from app.core.config import settings
from app.domains.ml.dependency_analysis import (
    DependencyAnalysisModel,
    DependencyAnalysisService,
)


@pytest.fixture
def model():
    return DependencyAnalysisModel(
        input_dim=768, hidden_dim=256, num_heads=8, num_layers=4
    )


@pytest.fixture
def service():
    return DependencyAnalysisService()


def test_model_initialization(model):
    """Test model structure and parameters"""
    assert isinstance(model.transformer, torch.nn.TransformerEncoder)
    assert isinstance(model.dependency_classifier, torch.nn.Sequential)
    assert isinstance(model.critical_path_predictor, torch.nn.Sequential)


def test_model_forward_pass(model):
    """Test model forward pass with dummy data"""
    batch_size = 4
    seq_len = 10
    input_dim = 768

    # Create dummy inputs
    embeddings = torch.randn(batch_size, seq_len, input_dim)
    attention_mask = torch.ones(batch_size, seq_len).bool()

    # Forward pass
    dep_logits, critical_probs = model(embeddings, attention_mask)

    # Check output shapes
    assert dep_logits.shape == (batch_size, seq_len, 3)  # 3 dependency classes
    assert critical_probs.shape == (batch_size, seq_len, 1)  # Critical path probability


@pytest.mark.asyncio
async def test_service_analyze_dependencies(service):
    """Test dependency analysis service"""
    work_items = [
        {"id": "1", "title": "Task 1", "description": "Description 1"},
        {"id": "2", "title": "Task 2", "description": "Description 2"},
        {"id": "3", "title": "Task 3", "description": "Description 3"},
    ]

    # Mock embeddings
    mock_embeddings = torch.randn(3, 768)  # 3 items, 768 dimensions

    # Mock service methods
    with (
        patch.object(service, "_get_embeddings", return_value=mock_embeddings),
        patch.object(
            service, "_create_attention_mask", return_value=torch.ones(3).bool()
        ),
        patch.object(
            service,
            "_process_predictions",
            return_value=[{"id": "1-2", "source": "1", "target": "2"}],
        ),
    ):

        result = await service.analyze_dependencies(work_items)

        assert len(result) > 0
        assert isinstance(result[0], dict)
        assert "id" in result[0]
        assert "source" in result[0]
        assert "target" in result[0]


def test_service_load_model(service, monkeypatch):
    """Test model loading with error handling"""
    # Force a model path so torch.load is called
    monkeypatch.setattr(
        service.settings, "DEPENDENCY_MODEL_PATH", "/tmp/nonexistent.pt", raising=False
    )
    with patch("torch.load", side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            service._load_model()
        assert "Test error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_service_error_handling(service):
    """Test error handling in analyze_dependencies"""
    work_items = [{"id": "1", "title": "Task 1"}]

    # Mock service to raise exception
    with patch.object(service, "_get_embeddings", side_effect=Exception("Test error")):
        with pytest.raises(Exception) as exc_info:
            await service.analyze_dependencies(work_items)
        assert "Test error" in str(exc_info.value)


def test_get_embeddings(service):
    """Test work item embedding generation"""
    work_items = [
        {"id": "1", "title": "Task 1", "description": "Description 1"},
        {"id": "2", "title": "Task 2", "description": "Description 2"},
    ]

    embeddings = service._get_embeddings(work_items)
    assert isinstance(embeddings, torch.Tensor)
    assert embeddings.shape[0] == len(work_items)  # Batch size matches number of items
    assert embeddings.shape[1] == 768  # Expected embedding dimension
