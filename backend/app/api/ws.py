from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websockets import ws_manager

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/feed/{group_id}")
async def websocket_feed_endpoint(websocket: WebSocket, group_id: str):
    """
    Ендпоінт для підключення фронтенду до кімнати (групи).
    """
    await ws_manager.connect(websocket, group_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, group_id)
