"""WebSocket endpoint for sprint balance updates."""

from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.auth import get_current_user_ws
from app.core.websocket_manager import manager
from app.domains.schemas.team import TeamResponse
from app.domains.sprint.balance_service import balance_service

router = APIRouter()


@router.websocket("/ws/sprints/{sprint_id}/balance")
async def balance_websocket(
    websocket: WebSocket,
    sprint_id: UUID,
    current_user: TeamResponse = Depends(get_current_user_ws),
):
    """WebSocket endpoint for real-time sprint balance updates.

    Args:
        websocket: WebSocket connection
        sprint_id: Sprint ID to monitor
        current_user: Current authenticated user
    """
    team_id = str(current_user.team_id)

    # Accept connection
    await manager.connect(websocket, team_id)

    try:
        # Send initial balance data
        team_capacity = await balance_service.get_team_capacity(sprint_id)
        work_items = await balance_service.get_sprint_work_items(sprint_id)

        initial_balance = await balance_service.analyze_sprint_balance(
            sprint_id=sprint_id, team_capacity=team_capacity, work_items=work_items
        )

        await websocket.send_json(
            {"type": "initial_balance", "data": initial_balance.model_dump()}
        )

        # Listen for updates
        while True:
            try:
                # Wait for messages
                data = await websocket.receive_json()

                # Handle message types
                message_type = data.get("type")
                if message_type == "refresh":
                    # Force refresh balance analysis
                    team_capacity = await balance_service.get_team_capacity(sprint_id)
                    work_items = await balance_service.get_sprint_work_items(sprint_id)

                    balance = await balance_service.analyze_sprint_balance(
                        sprint_id=sprint_id,
                        team_capacity=team_capacity,
                        work_items=work_items,
                    )

                    await websocket.send_json(
                        {"type": "balance_update", "data": balance.model_dump()}
                    )

            except WebSocketDisconnect:
                await manager.disconnect(websocket, team_id)
                break

            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "data": {"message": str(e)}}
                )

    except Exception:
        await manager.disconnect(websocket, team_id)
        raise
