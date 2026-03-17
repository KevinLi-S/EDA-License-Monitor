from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({'type': 'initial', 'data': {'message': 'phase-1 websocket ready'}})
    try:
        while True:
            message = await websocket.receive_text()
            if message == 'ping':
                await websocket.send_text('pong')
            else:
                await websocket.send_json({'type': 'echo', 'data': {'message': message}})
    except WebSocketDisconnect:
        return
