"""WebSocket connection manager for real-time updates."""

import asyncio
from typing import Dict, List, Optional, Set
import json
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""

    type: str
    data: dict


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        """Initialize connection manager."""
        # Map team IDs to sets of connected clients
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Lock for connection management
        self.connection_lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, team_id: str):
        """Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            team_id: Team ID for the connection
        """
        await websocket.accept()
        async with self.connection_lock:
            if team_id not in self.active_connections:
                self.active_connections[team_id] = set()
            self.active_connections[team_id].add(websocket)
            logger.info(
                "WebSocket connected",
                team_id=team_id,
                total_connections=len(self.active_connections[team_id]),
            )

    async def disconnect(self, websocket: WebSocket, team_id: str):
        """Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            team_id: Team ID for the connection
        """
        async with self.connection_lock:
            if team_id in self.active_connections:
                self.active_connections[team_id].discard(websocket)
                if not self.active_connections[team_id]:
                    del self.active_connections[team_id]
                logger.info(
                    "WebSocket disconnected",
                    team_id=team_id,
                    remaining_connections=len(
                        self.active_connections.get(team_id, set())
                    ),
                )

    async def broadcast_team_message(self, team_id: str, message: WebSocketMessage):
        """Broadcast a message to all connected clients for a team.

        Args:
            team_id: Team ID to broadcast to
            message: Message to broadcast
        """
        if team_id not in self.active_connections:
            return

        # Get a copy of connections to avoid modification during iteration
        connections = self.active_connections[team_id].copy()
        if not connections:
            return

        # Convert message to JSON
        message_json = message.model_dump_json()

        # Send to all connections
        for websocket in connections:
            try:
                await websocket.send_text(message_json)
            except WebSocketDisconnect:
                await self.disconnect(websocket, team_id)
            except Exception as e:
                logger.error(
                    "Error sending WebSocket message",
                    team_id=team_id,
                    error=str(e),
                    error_type=type(e).__name__,
                )

    async def broadcast_sprint_update(
        self, sprint_id: UUID, team_id: str, event_type: str, data: dict
    ):
        """Broadcast a sprint update event.

        Args:
            sprint_id: Sprint ID that was updated
            team_id: Team ID to broadcast to
            event_type: Type of update event
            data: Event data
        """
        message = WebSocketMessage(
            type=event_type,
            data={
                "sprint_id": str(sprint_id),
                **data,
            },
        )
        await self.broadcast_team_message(team_id, message)


# Global WebSocket manager
manager = ConnectionManager()
