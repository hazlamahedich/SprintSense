"""Scheduler for automatic LLM API key rotation."""

import asyncio
from datetime import datetime
from typing import Dict, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from redis import Redis

from app.core.config import settings
from app.core.logging import logger
from app.core.security.llm.key_rotation import LLMKeyRotationManager

class LLMKeyRotationScheduler:
    """Scheduler for automatic LLM API key rotation."""

    def __init__(self, redis_client: Redis):
        """Initialize the key rotation scheduler.

        Args:
            redis_client: Redis client for key caching
        """
        self.key_manager = LLMKeyRotationManager(redis_client)
        self.scheduler = AsyncIOScheduler()
        self.providers = settings.LLM_PROVIDERS

    async def start(self) -> None:
        """Start the key rotation scheduler."""
        # Schedule daily check at midnight
        self.scheduler.add_job(
            self._check_and_rotate_keys,
            CronTrigger(hour=0, minute=0),
            id='key_rotation_check',
            replace_existing=True
        )

        # Also schedule monitoring job
        self.scheduler.add_job(
            self._monitor_key_status,
            CronTrigger(hour='*/6'),  # Every 6 hours
            id='key_status_monitor',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Started LLM key rotation scheduler")

    async def stop(self) -> None:
        """Stop the key rotation scheduler."""
        self.scheduler.shutdown()
        logger.info("Stopped LLM key rotation scheduler")

    async def _check_and_rotate_keys(self) -> None:
        """Check and rotate keys for all providers if needed."""
        for provider in self.providers:
            try:
                if self.key_manager.check_rotation_needed(provider):
                    # In a real implementation, this would integrate with the
                    # provider's API to generate new keys. For now, we'll
                    # just log that rotation is needed.
                    logger.warning(
                        f"Key rotation needed for {provider}. "
                        "Manual rotation required."
                    )

                    # You could also send notifications here
                    await self._notify_rotation_needed(provider)
            except Exception as e:
                logger.error(
                    f"Error checking rotation for {provider}: {str(e)}"
                )

    async def _monitor_key_status(self) -> None:
        """Monitor key status and log metrics."""
        status_report: Dict[str, List[str]] = {
            "needs_rotation": [],
            "active": [],
            "errors": []
        }

        for provider in self.providers:
            try:
                if self.key_manager.check_rotation_needed(provider):
                    status_report["needs_rotation"].append(provider)
                else:
                    status_report["active"].append(provider)
            except Exception as e:
                logger.error(f"Error monitoring {provider}: {str(e)}")
                status_report["errors"].append(provider)

        # Log status report
        logger.info(
            "LLM Key Status Report\n"
            f"Time: {datetime.now().isoformat()}\n"
            f"Active Keys: {', '.join(status_report['active'])}\n"
            f"Needs Rotation: {', '.join(status_report['needs_rotation'])}\n"
            f"Errors: {', '.join(status_report['errors'])}"
        )

    async def _notify_rotation_needed(self, provider: str) -> None:
        """Send notification that key rotation is needed.

        In a real implementation, this would integrate with your notification
        system (email, Slack, etc.)

        Args:
            provider: The LLM provider requiring key rotation
        """
        # Example notification logging
        logger.warning(
            f"NOTIFICATION: API key rotation required for {provider}\n"
            "Please generate new API key and use the admin interface "
            "to perform the rotation."
        )
        # In practice, you would send actual notifications here