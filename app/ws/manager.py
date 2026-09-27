import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)
        logger.debug("WebSocket connected; active=%d", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)
        logger.debug("WebSocket disconnected; active=%d", len(self._connections))

    async def send_json(self, websocket: WebSocket, payload: dict[str, object]) -> None:
        await websocket.send_json(payload)

    async def broadcast_json(self, payload: dict[str, object]) -> None:
        for websocket in tuple(self._connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                logger.debug("Removing unavailable WebSocket", exc_info=True)
                self.disconnect(websocket)
