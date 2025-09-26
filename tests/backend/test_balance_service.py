import pytest
from uuid import UUID, uuid4
from app.domains.sprint.balance_service import (
    SprintBalanceService,
    TeamMemberCapacity,
    WorkItemAssignment,
    BalanceMetrics
)

@pytest.fixture
def balance_service():
    return SprintBalanceService()

@pytest.fixture
def team_capacity():
    return [
        TeamMemberCapacity(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            availability=1.0,
            skills=["python", "react"],
            time_zone="UTC-8"
        ),
        TeamMemberCapacity(
            user_id=UUID("87654321-8765-4321-8765-432187654321"),
            availability=0.5,  # Part-time
            skills=["python", "typescript"],
            time_zone="UTC-5"
        )
    ]

@pytest.fixture
def work_items():
    return [
        WorkItemAssignment(
            work_item_id=uuid4(),
            story_points=5,
            required_skills=["python", "react"],
            assigned_to=UUID("12345678-1234-5678-1234-567812345678"),
            estimated_hours=8.0
        ),
        WorkItemAssignment(
            work_item_id=uuid4(),
            story_points=3,
            required_skills=["python", "typescript"],
            assigned_to=UUID("87654321-8765-4321-8765-432187654321"),
            estimated_hours=5.0
        )
    ]

async def test_analyze_sprint_balance(balance_service, team_capacity, work_items):
    sprint_id = uuid4()
    metrics = await balance_service.analyze_sprint_balance(
        sprint_id=sprint_id,
        team_capacity=team_capacity,
        work_items=work_items
    )

    assert isinstance(metrics, BalanceMetrics)
    assert 0 <= metrics.overall_balance_score <= 1
    assert 0 <= metrics.team_utilization <= 1
    assert 0 <= metrics.skill_coverage <= 1
    assert len(metrics.workload_distribution) == len(team_capacity)
    assert isinstance(metrics.bottlenecks, list)
    assert isinstance(metrics.recommendations, list)

def test_calculate_workload_distribution(balance_service, team_capacity, work_items):
    workload = balance_service._calculate_workload_distribution(team_capacity, work_items)

    assert len(workload) == len(team_capacity)
    assert workload[UUID("12345678-1234-5678-1234-567812345678")] == 40.0  # 8h * 5sp
    assert workload[UUID("87654321-8765-4321-8765-432187654321")] == 30.0  # (5h * 3sp) / 0.5 availability

def test_calculate_balance_score(balance_service):
    # Perfect balance
    assert balance_service._calculate_balance_score({
        uuid4(): 10.0,
        uuid4(): 10.0
    }) == 1.0

    # Some imbalance
    score = balance_service._calculate_balance_score({
        uuid4(): 10.0,
        uuid4(): 15.0
    })
    assert 0.6 <= score <= 0.8

    # Empty workload
    assert balance_service._calculate_balance_score({}) == 1.0

def test_calculate_team_utilization(balance_service):
    # Full utilization
    assert balance_service._calculate_team_utilization({
        uuid4(): 40.0,
        uuid4(): 40.0
    }) == 1.0

    # Half utilization
    assert balance_service._calculate_team_utilization({
        uuid4(): 20.0,
        uuid4(): 20.0
    }) == 0.5

    # Empty team
    assert balance_service._calculate_team_utilization({}) == 0.0

def test_analyze_skill_coverage(balance_service, team_capacity, work_items):
    coverage = balance_service._analyze_skill_coverage(team_capacity, work_items)

    # All required skills are covered
    assert coverage == 1.0

    # Add a work item with uncovered skill
    work_items.append(
        WorkItemAssignment(
            work_item_id=uuid4(),
            story_points=2,
            required_skills=["java"],  # Not covered by team
            assigned_to=None,
            estimated_hours=4.0
        )
    )

    coverage = balance_service._analyze_skill_coverage(team_capacity, work_items)
    assert coverage < 1.0  # Coverage should be reduced

def test_identify_bottlenecks(balance_service):
    user_id = uuid4()
    workload = {
        user_id: 50.0,  # Overloaded
        uuid4(): 20.0   # Normal load
    }

    bottlenecks = balance_service._identify_bottlenecks(workload, 1.0)
    assert len(bottlenecks) == 1
    assert str(user_id) in bottlenecks[0]

    # Test skill coverage bottleneck
    bottlenecks = balance_service._identify_bottlenecks({}, 0.7)
    assert len(bottlenecks) == 1
    assert "skill coverage" in bottlenecks[0].lower()

def test_generate_recommendations(balance_service):
    # Test balanced workload
    recommendations = balance_service._generate_recommendations(
        workload={uuid4(): 30.0, uuid4(): 30.0},
        skill_coverage=1.0,
        bottlenecks=[]
    )
    assert len(recommendations) == 1
    assert "good" in recommendations[0].lower()

    # Test imbalanced workload
    user1, user2 = uuid4(), uuid4()
    recommendations = balance_service._generate_recommendations(
        workload={user1: 50.0, user2: 20.0},
        skill_coverage=0.7,
        bottlenecks=[f"High workload for team member {user1}"]
    )
    assert len(recommendations) >= 2
    assert any("redistributing" in r.lower() for r in recommendations)
    assert any("skills" in r.lower() for r in recommendations)