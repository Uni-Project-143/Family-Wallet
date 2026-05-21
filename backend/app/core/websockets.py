from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Зберігаємо підключення по групах: { "group_id": [WebSocket, WebSocket, ...] }
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_id: str):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)

    def disconnect(self, websocket: WebSocket, group_id: str):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
            # Очищаємо пам'ять, якщо в групі більше нікого немає
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]

    async def broadcast_to_group(self, group_id: str, message: dict):
        if group_id in self.active_connections:
            # Відправляємо JSON повідомлення всім клієнтам у цій групі
            for connection in self.active_connections[group_id]:
                await connection.send_json(message)

# Створюємо єдиний екземпляр менеджера для всього додатку
ws_manager = ConnectionManager()
