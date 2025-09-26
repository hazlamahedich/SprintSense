"""End-to-end tests for sprint balance analysis feature."""

import asyncio
import json
import pytest
from uuid import uuid4

from fastapi import WebSocket
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.domains.sprint.schemas import (
    TeamMemberCapacity,
    WorkItemAssignment,
    BalanceMetrics,
)

@pytest.mark.asyncio
async def test_sprint_balance_flow(client: AsyncClient, websocket_client: WebSocket):
    """Test complete sprint balance analysis flow."""
    # Setup test data
    sprint_id = str(uuid4())
    team_id = str(uuid4())

    # Create test users
    user1_id = str(uuid4())
    user2_id = str(uuid4())

    team_capacity = [
        TeamMemberCapacity(
            user_id=user1_id,
            availability=1.0,
            skills=["python", "react"],
            time_zone="UTC"
        ),
        TeamMemberCapacity(
            user_id=user2_id,
            availability=0.5,
            skills=["python", "typescript"],
            time_zone="UTC-8"
        )
    ]

    work_items = [
        WorkItemAssignment(
            work_item_id=str(uuid4()),
            story_points=5,
            required_skills=["python", "react"],
            assigned_to=user1_id,
            estimated_hours=8.0
        ),
        WorkItemAssignment(
            work_item_id=str(uuid4()),
            story_points=3,
            required_skills=["python", "typescript"],
            assigned_to=user2_id,
            estimated_hours=5.0
        )
    ]

    # Test REST API
    response = await client.post(
        f"/api/sprints/{sprint_id}/balance",
        json={
            "team_capacity": [tc.model_dump() for tc in team_capacity],
            "work_items": [wi.model_dump() for wi in work_items]
        }
    )
    assert response.status_code == 200

    data = response.json()
    metrics = BalanceMetrics.model_validate(data)

    assert 0 <= metrics.overall_balance_score <= 1
    assert 0 <= metrics.team_utilization <= 1
    assert 0 <= metrics.skill_coverage <= 1
    assert len(metrics.workload_distribution) == 2
    assert metrics.calculated_at is not None

    # Test WebSocket updates
    async with websocket_client.connect(
        f"/ws/sprints/{sprint_id}/balance",
        extra_headers={"Authorization": f"Bearer {test_token}"}
    ) as ws:
        # Receive initial data
        data = await ws.receive_json()
        assert data["type"] == "initial_balance"
        assert "overall_balance_score" in data["data"]

        # Test refresh request
        await ws.send_json({"type": "refresh"})
        data = await ws.receive_json()
        assert data["type"] == "balance_update"

        # Add work item and verify update
        new_item = WorkItemAssignment(
            work_item_id=str(uuid4()),
            story_points=3,
            required_skills=["python"],
            assigned_to=user1_id,
            estimated_hours=4.0
        )

        response = await client.post(
            f"/api/sprints/{sprint_id}/work-items",
            json=new_item.model_dump()
        )
        assert response.status_code == 200

        # Verify WebSocket update
        data = await ws.receive_json()
        assert data["type"] == "balance_update"
        updated_metrics = BalanceMetrics.model_validate(data["data"])
        assert len(updated_metrics.workload_distribution) == 2
        assert updated_metrics.workload_distribution[user1_id] > metrics.workload_distribution[user1_id]

@pytest.mark.asyncio
async def test_sprint_balance_validation(client: AsyncClient):
    """Test input validation for sprint balance analysis."""
    sprint_id = str(uuid4())

    # Test invalid availability
    invalid_capacity = TeamMemberCapacity(
        user_id=str(uuid4()),
        availability=1.5,  # Invalid: > 1.0
        skills=["python"],
        time_zone="UTC"
    )

    response = await client.post(
        f"/api/sprints/{sprint_id}/balance",
        json={
            "team_capacity": [invalid_capacity.model_dump()],
            "work_items": []
        }
    )
    assert response.status_code == 422

    # Test invalid story points/hours ratio
    invalid_item = WorkItemAssignment(
        work_item_id=str(uuid4()),
        story_points=1,
        required_skills=["python"],
        assigned_to=None,
        estimated_hours=20.0  # Invalid: > 16h per point
    )

    response = await client.post(
        f"/api/sprints/{sprint_id}/balance",
        json={
            "team_capacity": [
                TeamMemberCapacity(
                    user_id=str(uuid4()),
                    availability=1.0,
                    skills=["python"],
                    time_zone="UTC"
                ).model_dump()
            ],
            "work_items": [invalid_item.model_dump()]
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_sprint_balance_performance(client: AsyncClient):
    """Test performance requirements for sprint balance analysis."""
    sprint_id = str(uuid4())

    # Generate large dataset
    team_capacity = [
        TeamMemberCapacity(
            user_id=str(uuid4()),
            availability=1.0,
            skills=["python", "react", "typescript"][i % 3:],
            time_zone="UTC"
        )
        for i in range(50)  # 50 team members
    ]

    work_items = [
        WorkItemAssignment(
            work_item_id=str(uuid4()),
            story_points=i % 5 + 1,
            required_skills=["python", "react", "typescript"][i % 3:],
            assigned_to=team_capacity[i % 50].user_id,
            estimated_hours=float(i % 5 + 1) * 4
        )
        for i in range(200)  # 200 work items
    ]

    # Measure response time
    start = asyncio.get_event_loop().time()

    response = await client.post(
        f"/api/sprints/{sprint_id}/balance",
        json={
            "team_capacity": [tc.model_dump() for tc in team_capacity],
            "work_items": [wi.model_dump() for wi in work_items]
        }
    )

    duration = asyncio.get_event_loop().time() - start

    assert response.status_code == 200
    assert duration < 1.0  # Must complete in < 1s

    # Test concurrent requests
    async def make_request():
        return await client.post(
            f"/api/sprints/{sprint_id}/balance",
            json={
                "team_capacity": [tc.model_dump() for tc in team_capacity],
                "work_items": [wi.model_dump() for wi in work_items]
            }
        )

    start = asyncio.get_event_loop().time()
    responses = await asyncio.gather(*[make_request() for _ in range(10)])
    duration = asyncio.get_event_loop().time() - start

    assert all(r.status_code == 200 for r in responses)
    assert duration < 2.0  # 10 concurrent requests in < 2s
