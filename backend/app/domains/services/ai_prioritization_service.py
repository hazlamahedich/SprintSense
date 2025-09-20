"""AI Prioritization Service for scoring work items based on project goals."""

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

import structlog
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, DatabaseError, ValidationError
from app.core.performance import monitor_performance
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import TeamMember, TeamRole
from app.domains.models.work_item import WorkItem, WorkItemStatus
from app.domains.schemas.ai_prioritization import (
    AIPrioritizationRequest,
    AIPrioritizationResponse,
    BusinessMetrics,
    MatchedGoal,
    ScoredWorkItem,
    ScoringMetadata,
)

logger = structlog.get_logger(__name__)

# Constants for scoring algorithm
SCORE_MIN = 0.0
SCORE_MAX = 10.0
PRIORITY_WEIGHT_MAX = 10.0
WORK_ITEM_PRIORITY_MAX = 10.0
PRIORITY_ADJUSTMENT_MAX = 0.5
MIN_TEXT_LENGTH = 10
ALGORITHM_VERSION = "1.0.0"

# Text processing constants
STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "should",
    "could",
    "can",
    "may",
    "might",
    "this",
    "that",
    "these",
    "those",
    "i",
    "me",
    "my",
    "mine",
    "you",
    "your",
    "yours",
    "he",
    "him",
    "his",
    "she",
    "her",
    "hers",
    "it",
    "its",
    "we",
    "us",
    "our",
    "ours",
    "they",
    "them",
    "their",
    "theirs",
}


class TextProcessor:
    """Text processing utilities for AI prioritization."""

    @staticmethod
    def strip_html(text: str) -> str:
        """Strip HTML tags from text."""
        import html

        # First decode HTML entities
        text = html.unescape(text)
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        return text

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for processing."""
        if not text:
            return ""

        # Strip HTML
        text = TextProcessor.strip_html(text)

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        return text

    @staticmethod
    def extract_keywords(text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        if not text or len(text.strip()) < MIN_TEXT_LENGTH:
            return set()

        normalized_text = TextProcessor.normalize_text(text)

        # Extract words (alphanumeric + underscore, min 2 chars)
        words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]{1,}\b", normalized_text)

        # Filter stop words and apply stemming (basic form)
        keywords = set()
        for word in words:
            word_lower = word.lower()
            if word_lower not in STOP_WORDS and len(word_lower) >= 2:
                # Basic stemming - remove common suffixes
                stemmed = TextProcessor.simple_stem(word_lower)
                keywords.add(stemmed)

        return keywords

    @staticmethod
    def simple_stem(word: str) -> str:
        """Simple stemming algorithm."""
        # Remove common English suffixes
        suffixes = ["ing", "ed", "er", "est", "ly", "s", "es"]

        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[: -len(suffix)]

        return word


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise CircuitBreakerError("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        return (
            self.last_failure_time is not None
            and datetime.utcnow() - self.last_failure_time
            > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class AIPrioritizationService:
    """Service for AI-powered work item prioritization."""

    def __init__(self, db: AsyncSession, redis_client=None) -> None:
        """Initialize AI prioritization service."""
        self.db = db
        self.redis_client = redis_client
        self.text_processor = TextProcessor()
        self.circuit_breaker = CircuitBreaker()

    @monitor_performance("ai_prioritization_scoring")
    async def score_work_items(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        request: AIPrioritizationRequest,
    ) -> AIPrioritizationResponse:
        """
        Score work items based on alignment with project goals.

        Args:
            team_id: Team UUID
            user_id: User UUID (for authorization)
            request: Prioritization request data

        Returns:
            AIPrioritizationResponse with scored items

        Raises:
            AuthorizationError: If user is not a team member
            ValidationError: If request data is invalid
            DatabaseError: If database operation fails
        """
        start_time = datetime.utcnow()

        logger.info(
            "Starting AI prioritization scoring",
            team_id=str(team_id),
            user_id=str(user_id),
            mode=request.mode,
            work_item_count=(
                len(request.work_item_ids) if request.work_item_ids else None
            ),
        )

        # Verify user is team member
        if not await self._is_team_member(team_id, user_id):
            raise AuthorizationError(
                message="You must be a team member to access AI prioritization",
                error_code="NOT_TEAM_MEMBER",
                details={"team_id": str(team_id), "user_id": str(user_id)},
                recovery_action="Please join the team or contact the team owner",
            )

        try:
            # Get project goals with caching
            goals = await self._get_cached_project_goals(team_id)

            if not goals:
                logger.warning(
                    "No project goals found for team",
                    team_id=str(team_id),
                )
                return AIPrioritizationResponse(
                    scored_items=[],
                    total_items=0,
                    generation_time_ms=0,
                    business_metrics=BusinessMetrics(
                        accuracy_score=0.0,
                        coverage_percentage=0.0,
                        algorithm_version=ALGORITHM_VERSION,
                    ),
                    warning="no_goals_configured",
                )

            # Get work items to score
            work_items = await self._get_work_items_for_scoring(
                team_id, request.work_item_ids
            )

            if not work_items:
                logger.warning(
                    "No work items found for scoring",
                    team_id=str(team_id),
                )
                return AIPrioritizationResponse(
                    scored_items=[],
                    total_items=0,
                    generation_time_ms=0,
                    business_metrics=BusinessMetrics(
                        accuracy_score=0.0,
                        coverage_percentage=0.0,
                        algorithm_version=ALGORITHM_VERSION,
                    ),
                )

            # Score work items
            scored_items = await self._score_work_items_against_goals(
                work_items, goals, request.include_metadata, request.mode
            )

            # Calculate business metrics
            business_metrics = self._calculate_business_metrics(scored_items, goals)

            # Calculate generation time
            generation_time_ms = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            logger.info(
                "AI prioritization scoring completed successfully",
                team_id=str(team_id),
                user_id=str(user_id),
                scored_items_count=len(scored_items),
                generation_time_ms=generation_time_ms,
            )

            return AIPrioritizationResponse(
                scored_items=scored_items,
                total_items=len(scored_items),
                generation_time_ms=generation_time_ms,
                business_metrics=business_metrics,
            )

        except Exception as e:
            logger.error(
                "Error during AI prioritization scoring",
                error=str(e),
                error_type=type(e).__name__,
                team_id=str(team_id),
                user_id=str(user_id),
            )

            if isinstance(e, (AuthorizationError, ValidationError)):
                raise e

            raise DatabaseError(
                message="An error occurred during AI prioritization scoring",
                error_code="AI_SCORING_ERROR",
                details={"original_error": str(e)},
                recovery_action="Please try again or contact support",
            )

    async def _get_cached_project_goals(self, team_id: uuid.UUID) -> List[ProjectGoal]:
        """Get project goals with Redis caching."""
        cache_key = f"ai_priority:goals:{team_id}"

        # Try to get from cache first
        if self.redis_client:
            try:
                cached_data = await self.circuit_breaker.call(
                    self.redis_client.get, cache_key
                )
                if cached_data:
                    # Parse cached data and reconstruct ProjectGoal objects
                    cached_goals = json.loads(cached_data)
                    return [
                        self._dict_to_project_goal(goal_data)
                        for goal_data in cached_goals
                    ]
            except Exception as e:
                logger.warning(
                    "Failed to retrieve goals from cache, falling back to database",
                    team_id=str(team_id),
                    error=str(e),
                )

        # Fetch from database
        query = (
            select(ProjectGoal)
            .where(ProjectGoal.team_id == team_id)
            .order_by(desc(ProjectGoal.priority_weight), ProjectGoal.created_at)
        )

        result = await self.db.execute(query)
        goals = result.scalars().all()

        # Cache the results
        if self.redis_client and goals:
            try:
                cache_data = [self._project_goal_to_dict(goal) for goal in goals]
                await self.circuit_breaker.call(
                    self.redis_client.setex,
                    cache_key,
                    3600,  # 1 hour TTL
                    json.dumps(cache_data, default=str),
                )
            except Exception as e:
                logger.warning(
                    "Failed to cache project goals",
                    team_id=str(team_id),
                    error=str(e),
                )

        return goals

    def _project_goal_to_dict(self, goal: ProjectGoal) -> Dict:
        """Convert ProjectGoal to dictionary for caching."""
        return {
            "id": str(goal.id),
            "team_id": str(goal.team_id),
            "description": goal.description,
            "priority_weight": goal.priority_weight,
            "success_metrics": goal.success_metrics,
            "keywords": list(self.text_processor.extract_keywords(goal.description)),
        }

    def _dict_to_project_goal(self, goal_data: Dict) -> ProjectGoal:
        """Convert dictionary back to ProjectGoal object."""
        goal = ProjectGoal()
        goal.id = uuid.UUID(goal_data["id"])
        goal.team_id = uuid.UUID(goal_data["team_id"])
        goal.description = goal_data["description"]
        goal.priority_weight = goal_data["priority_weight"]
        goal.success_metrics = goal_data["success_metrics"]
        return goal

    async def _get_work_items_for_scoring(
        self, team_id: uuid.UUID, work_item_ids: Optional[List[uuid.UUID]] = None
    ) -> List[WorkItem]:
        """Get work items for scoring."""
        query = (
            select(WorkItem)
            .where(
                and_(
                    WorkItem.team_id == team_id,
                    WorkItem.status != WorkItemStatus.ARCHIVED,
                )
            )
            .order_by(desc(WorkItem.priority), WorkItem.created_at)
        )

        if work_item_ids:
            query = query.where(WorkItem.id.in_(work_item_ids))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def _score_work_items_against_goals(
        self,
        work_items: List[WorkItem],
        goals: List[ProjectGoal],
        include_metadata: bool,
        mode: str,
    ) -> List[ScoredWorkItem]:
        """Score work items against project goals."""
        scored_items = []

        # Preprocess goals for efficient scoring
        goal_keywords = {}
        for goal in goals:
            goal_keywords[goal.id] = self.text_processor.extract_keywords(
                goal.description
            )

        for work_item in work_items:
            try:
                scored_item = await self._score_single_work_item(
                    work_item, goals, goal_keywords, include_metadata, mode
                )
                scored_items.append(scored_item)
            except Exception as e:
                logger.warning(
                    "Failed to score work item, skipping",
                    work_item_id=str(work_item.id),
                    error=str(e),
                )
                # Continue with other items

        # Sort by AI score (highest first), then by suggested rank
        scored_items.sort(key=lambda x: (-x.ai_score, x.suggested_rank))

        # Update suggested ranks after sorting
        for i, item in enumerate(scored_items):
            item.suggested_rank = i + 1

        return scored_items

    async def _score_single_work_item(
        self,
        work_item: WorkItem,
        goals: List[ProjectGoal],
        goal_keywords: Dict[uuid.UUID, Set[str]],
        include_metadata: bool,
        mode: str,
    ) -> ScoredWorkItem:
        """Score a single work item against goals."""
        # Extract keywords from work item
        work_item_text = f"{work_item.title} {work_item.description or ''}"
        work_item_keywords = self.text_processor.extract_keywords(work_item_text)

        base_score = 0.0
        matched_goals = []
        total_keywords_matched = 0

        # Score against each goal
        for goal in goals:
            keywords = goal_keywords[goal.id]
            if not keywords:  # Empty goal keywords
                continue

            # Calculate keyword matches
            matches = work_item_keywords.intersection(keywords)
            match_count = len(matches)

            if match_count > 0:
                # Calculate goal score with bounds checking (QA Review fix)
                goal_score = min(
                    SCORE_MAX, (match_count / len(keywords)) * goal.priority_weight
                )
                base_score += goal_score
                total_keywords_matched += match_count

                if include_metadata:
                    matched_goals.append(
                        MatchedGoal(
                            goal_id=goal.id,
                            goal_title=(
                                goal.description[:100] + "..."
                                if len(goal.description) > 100
                                else goal.description
                            ),
                            match_strength=goal_score,
                            matched_keywords=list(matches),
                        )
                    )

        # Apply priority adjustment (QA Review fix: bounded)
        priority_adjustment = min(
            PRIORITY_ADJUSTMENT_MAX,
            (work_item.priority / WORK_ITEM_PRIORITY_MAX) * PRIORITY_ADJUSTMENT_MAX,
        )

        # Calculate final score with bounds checking
        final_score = min(SCORE_MAX, base_score + priority_adjustment)

        # Generate confidence level
        confidence_level = self._calculate_confidence_level(
            final_score, len(matched_goals)
        )

        # Generate explanation
        explanation = self._generate_explanation(work_item, matched_goals, final_score)

        # Create scoring metadata
        scoring_metadata = None
        if include_metadata:
            scoring_metadata = ScoringMetadata(
                matched_goals=matched_goals,
                base_score=base_score,
                priority_adjustment=priority_adjustment,
                clustering_similarity=self._calculate_clustering_similarity(
                    work_item_keywords, goal_keywords
                ),
            )

        return ScoredWorkItem(
            work_item_id=work_item.id,
            title=work_item.title,
            current_priority=work_item.priority,
            ai_score=final_score,
            suggested_rank=1,  # Will be updated after sorting
            confidence_level=confidence_level,
            explanation=explanation,
            scoring_metadata=scoring_metadata,
        )

    def _calculate_confidence_level(
        self, score: float, matched_goals_count: int
    ) -> str:
        """Calculate confidence level for the score."""
        if score >= 7.0 and matched_goals_count >= 2:
            return "high"
        elif score >= 4.0 and matched_goals_count >= 1:
            return "medium"
        else:
            return "low"

    def _generate_explanation(
        self, work_item: WorkItem, matched_goals: List[MatchedGoal], score: float
    ) -> str:
        """Generate human-readable explanation for the score."""
        if not matched_goals:
            return f"Score {score:.1f}/10: No strong alignment with current project goals detected."

        if len(matched_goals) == 1:
            goal = matched_goals[0]
            return f"Score {score:.1f}/10: Aligns with '{goal.goal_title}' through keywords: {', '.join(goal.matched_keywords[:3])}."

        goal_count = len(matched_goals)
        top_keywords = []
        for goal in matched_goals[:2]:  # Top 2 goals
            top_keywords.extend(goal.matched_keywords[:2])

        return f"Score {score:.1f}/10: Strong alignment with {goal_count} goals through keywords: {', '.join(set(top_keywords[:4]))}."

    def _calculate_clustering_similarity(
        self, work_item_keywords: Set[str], goal_keywords: Dict[uuid.UUID, Set[str]]
    ) -> float:
        """Calculate clustering similarity for Story 3.4 epic clustering feature."""
        if not work_item_keywords:
            return 0.0

        # Calculate average similarity with all goals
        similarities = []
        for keywords in goal_keywords.values():
            if keywords:
                intersection = len(work_item_keywords.intersection(keywords))
                union = len(work_item_keywords.union(keywords))
                jaccard_similarity = intersection / union if union > 0 else 0.0
                similarities.append(jaccard_similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _calculate_business_metrics(
        self, scored_items: List[ScoredWorkItem], goals: List[ProjectGoal]
    ) -> BusinessMetrics:
        """Calculate business metrics for A/B testing framework."""
        if not scored_items:
            return BusinessMetrics(
                accuracy_score=0.0,
                coverage_percentage=0.0,
                algorithm_version=ALGORITHM_VERSION,
            )

        # Calculate coverage percentage (items with non-zero scores)
        items_with_scores = sum(1 for item in scored_items if item.ai_score > 0)
        coverage_percentage = (items_with_scores / len(scored_items)) * 100

        # Calculate accuracy score (average confidence level as numeric)
        confidence_scores = []
        for item in scored_items:
            if item.confidence_level == "high":
                confidence_scores.append(1.0)
            elif item.confidence_level == "medium":
                confidence_scores.append(0.6)
            else:
                confidence_scores.append(0.3)

        accuracy_score = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        return BusinessMetrics(
            accuracy_score=accuracy_score,
            coverage_percentage=coverage_percentage,
            algorithm_version=ALGORITHM_VERSION,
        )

    async def _is_team_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is a team member."""
        query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    def _generate_cache_key(
        self, team_id: uuid.UUID, work_item_ids: Optional[List[uuid.UUID]]
    ) -> str:
        """Generate cache key for scoring results."""
        if work_item_ids:
            # Create hash of work item IDs for deterministic cache key
            ids_str = ",".join(sorted(str(id) for id in work_item_ids))
            ids_hash = hashlib.md5(ids_str.encode()).hexdigest()[:8]
            return f"ai_priority:scores:{team_id}:{ids_hash}"
        else:
            return f"ai_priority:scores:{team_id}:all"
