"""Integration tests for AI Prioritization API endpoints."""

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.project_goal import ProjectGoal
from app.domains.models.user import User
from app.domains.models.work_item import WorkItem, WorkItemStatus, WorkItemType
from app.domains.schemas.ai_prioritization import (
    AIPrioritizationRequest,
    AIPrioritizationResponse,
)


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="testuser@example.com",
        username="testuser",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_team(db_session: AsyncSession, test_user: User):
    """Create a test team with the user as a member."""
    team = Team(
        id=uuid.uuid4(),
        name="Test Team",
        description="A test team for AI prioritization",
        created_by=test_user.id,
    )
    db_session.add(team)
    await db_session.flush()

    # Add user as team member
    team_member = TeamMember(
        user_id=test_user.id,
        team_id=team.id,
        role=TeamRole.MEMBER,
    )
    db_session.add(team_member)
    await db_session.commit()

    return team


@pytest.fixture
async def test_project_goals(db_session: AsyncSession, test_team: Team):
    """Create test project goals for the team."""
    goals = [
        ProjectGoal(
            id=uuid.uuid4(),
            team_id=test_team.id,
            description="Improve user experience and performance",
            priority_weight=8,
            success_metrics="Reduce load time by 50%",
            created_at=datetime.utcnow(),
        ),
        ProjectGoal(
            id=uuid.uuid4(),
            team_id=test_team.id,
            description="Enhance system security and authentication",
            priority_weight=6,
            success_metrics="Zero security incidents",
            created_at=datetime.utcnow(),
        ),
    ]

    for goal in goals:
        db_session.add(goal)

    await db_session.commit()
    return goals


@pytest.fixture
async def test_work_items(db_session: AsyncSession, test_team: Team):
    """Create test work items for the team."""
    items = [
        WorkItem(
            id=uuid.uuid4(),
            team_id=test_team.id,
            title="Optimize database queries for better performance",
            description="Improve query performance and user experience",
            priority=5.0,
            status=WorkItemStatus.BACKLOG,
            type=WorkItemType.STORY,
            created_at=datetime.utcnow(),
        ),
        WorkItem(
            id=uuid.uuid4(),
            team_id=test_team.id,
            title="Implement two-factor authentication",
            description="Add security layer for user authentication",
            priority=3.0,
            status=WorkItemStatus.BACKLOG,
            type=WorkItemType.STORY,
            created_at=datetime.utcnow(),
        ),
        WorkItem(
            id=uuid.uuid4(),
            team_id=test_team.id,
            title="Update user interface design",
            description="Modernize UI components and improve user experience",
            priority=7.0,
            status=WorkItemStatus.IN_PROGRESS,
            type=WorkItemType.STORY,
            created_at=datetime.utcnow(),
        ),
    ]

    for item in items:
        db_session.add(item)

    await db_session.commit()
    return items


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for caching tests."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # Default to cache miss
    mock_redis.setex.return_value = True
    return mock_redis


class TestAIPrioritizationAPI:
    """Integration tests for AI Prioritization API."""

    @pytest.mark.asyncio
    async def test_score_work_items_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_project_goals: list[ProjectGoal],
        test_work_items: list[WorkItem],
        mock_redis_client,
        auth_headers,
    ):
        """Test successful work item scoring via API."""
        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert "total_items" in data
            assert "scored_items" in data
            assert "generation_time_ms" in data
            assert "business_metrics" in data

            # Validate response structure
            assert isinstance(data["total_items"], int)
            assert data["total_items"] == len(test_work_items)
            assert len(data["scored_items"]) == data["total_items"]

            # Check each scored item
            for item in data["scored_items"]:
                assert "work_item_id" in item
                assert "title" in item
                assert "current_priority" in item
                assert "ai_score" in item
                assert "suggested_rank" in item
                assert "confidence_level" in item
                assert "explanation" in item

                # Validate ranges and types
                assert 0.0 <= item["ai_score"] <= 10.0
                assert item["suggested_rank"] > 0
                assert item["confidence_level"] in ["high", "medium", "low"]
                assert len(item["explanation"]) > 0

    @pytest.mark.asyncio
    async def test_score_work_items_specific_ids(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_project_goals: list[ProjectGoal],
        test_work_items: list[WorkItem],
        mock_redis_client,
        auth_headers,
    ):
        """Test scoring specific work item IDs."""
        specific_ids = [str(test_work_items[0].id), str(test_work_items[1].id)]

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": specific_ids,
                "include_metadata": False,
                "mode": "full",
            }

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["total_items"] == 2

            # Check that only requested items are returned
            returned_ids = [item["work_item_id"] for item in data["scored_items"]]
            assert set(returned_ids) == set(specific_ids)

    @pytest.mark.asyncio
    async def test_score_work_items_no_metadata(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_project_goals: list[ProjectGoal],
        test_work_items: list[WorkItem],
        mock_redis_client,
        auth_headers,
    ):
        """Test scoring without metadata."""
        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": False,
                "mode": "fast",
            }

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()

            # Check that metadata fields are minimal or absent
            for item in data["scored_items"]:
                # In fast mode without metadata, explanation might be shorter
                assert "work_item_id" in item
                assert "ai_score" in item
                assert "suggested_rank" in item

    @pytest.mark.asyncio
    async def test_score_work_items_unauthorized_user(
        self,
        client: AsyncClient,
        test_team: Team,
        mock_redis_client,
    ):
        """Test scoring with unauthorized user (not a team member)."""
        # Create headers for a different user who is not a team member
        unauthorized_headers = {"Authorization": "Bearer fake-token-different-user"}

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            with patch("app.core.auth.get_current_user") as mock_get_user:
                # Mock a user who is not a team member
                mock_get_user.return_value = User(
                    id=uuid.uuid4(),
                    email="unauthorized@example.com",
                    username="unauthorized",
                    is_active=True,
                )

                request_data = {
                    "work_item_ids": None,
                    "include_metadata": True,
                    "mode": "full",
                }

                response = await client.post(
                    f"/api/v1/{test_team.id}/ai-prioritization/score",
                    json=request_data,
                    headers=unauthorized_headers,
                )

                assert response.status_code == status.HTTP_403_FORBIDDEN

                data = response.json()
                assert "error" in data
                assert "You must be a team member" in data["error"]

    @pytest.mark.asyncio
    async def test_score_work_items_nonexistent_team(
        self,
        client: AsyncClient,
        test_user: User,
        mock_redis_client,
        auth_headers,
    ):
        """Test scoring for a non-existent team."""
        fake_team_id = uuid.uuid4()

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            response = await client.post(
                f"/api/v1/{fake_team_id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_score_work_items_no_goals_configured(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_work_items: list[WorkItem],
        mock_redis_client,
        auth_headers,
        db_session: AsyncSession,
    ):
        """Test scoring when no project goals are configured."""
        # Remove all project goals
        await db_session.execute(
            "DELETE FROM project_goals WHERE team_id = :team_id",
            {"team_id": test_team.id},
        )
        await db_session.commit()

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["total_items"] == 0
            assert data["warning"] == "no_goals_configured"

    @pytest.mark.asyncio
    async def test_score_work_items_invalid_request(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        mock_redis_client,
        auth_headers,
    ):
        """Test scoring with invalid request data."""
        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            # Invalid mode
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "invalid_mode",
            }

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_score_work_items_database_error(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        mock_redis_client,
        auth_headers,
    ):
        """Test handling of database errors."""
        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            with patch(
                "app.domains.services.ai_prioritization_service.AIPrioritizationService.score_work_items"
            ) as mock_score:
                # Mock database error
                mock_score.side_effect = DatabaseError("Database connection failed")

                request_data = {
                    "work_item_ids": None,
                    "include_metadata": True,
                    "mode": "full",
                }

                response = await client.post(
                    f"/api/v1/{test_team.id}/ai-prioritization/score",
                    json=request_data,
                    headers=auth_headers,
                )

                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

                data = response.json()
                assert "error" in data
                assert "database error occurred" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_score_work_items_redis_caching(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_project_goals: list[ProjectGoal],
        test_work_items: list[WorkItem],
        mock_redis_client,
        auth_headers,
    ):
        """Test Redis caching behavior."""
        # First request - cache miss
        mock_redis_client.get.return_value = None

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            response1 = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response1.status_code == status.HTTP_200_OK

            # Verify cache was attempted to be set
            mock_redis_client.setex.assert_called()

            # Second request - simulate cache hit
            cached_goals = json.dumps(
                [
                    {
                        "id": str(test_project_goals[0].id),
                        "team_id": str(test_project_goals[0].team_id),
                        "description": test_project_goals[0].description,
                        "priority_weight": test_project_goals[0].priority_weight,
                        "success_metrics": test_project_goals[0].success_metrics,
                        "keywords": ["improve", "user", "experience", "performance"],
                    }
                ],
                default=str,
            )

            mock_redis_client.get.return_value = cached_goals

            response2 = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response2.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_score_work_items_performance(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_project_goals: list[ProjectGoal],
        test_work_items: list[WorkItem],
        mock_redis_client,
        auth_headers,
    ):
        """Test API response time meets performance requirements."""
        import time

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            start_time = time.time()

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            assert response.status_code == status.HTTP_200_OK

            # Check that response time meets requirement (<500ms)
            assert (
                response_time_ms < 500
            ), f"Response time {response_time_ms:.2f}ms exceeds 500ms requirement"

            data = response.json()

            # Verify generation_time_ms is reported
            assert "generation_time_ms" in data
            assert isinstance(data["generation_time_ms"], (int, float))
            assert data["generation_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_score_work_items_empty_team_id(
        self,
        client: AsyncClient,
        mock_redis_client,
        auth_headers,
    ):
        """Test scoring with invalid team ID format."""
        invalid_team_id = "not-a-uuid"

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            response = await client.post(
                f"/api/v1/{invalid_team_id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            # Should return 422 for invalid UUID format
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_score_work_items_large_dataset(
        self,
        client: AsyncClient,
        test_user: User,
        test_team: Team,
        test_project_goals: list[ProjectGoal],
        mock_redis_client,
        auth_headers,
        db_session: AsyncSession,
    ):
        """Test scoring with a larger dataset to verify scalability."""
        # Create many work items to test performance
        large_work_items = []
        for i in range(20):  # Create 20 work items
            item = WorkItem(
                id=uuid.uuid4(),
                team_id=test_team.id,
                title=f"Work Item {i+1}",
                description=f"Description for work item {i+1} with various keywords",
                priority=float(i % 10),
                status=WorkItemStatus.BACKLOG,
                type=WorkItemType.STORY,
                created_at=datetime.utcnow(),
            )
            large_work_items.append(item)
            db_session.add(item)

        await db_session.commit()

        with patch(
            "app.domains.routers.ai_prioritization.get_redis_client",
            return_value=mock_redis_client,
        ):
            request_data = {
                "work_item_ids": None,
                "include_metadata": True,
                "mode": "full",
            }

            response = await client.post(
                f"/api/v1/{test_team.id}/ai-prioritization/score",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["total_items"] == 20
            assert len(data["scored_items"]) == 20

            # Verify all items are properly ranked
            ranks = [item["suggested_rank"] for item in data["scored_items"]]
            assert len(set(ranks)) == len(ranks)  # All ranks should be unique
            assert min(ranks) == 1
            assert max(ranks) == 20
