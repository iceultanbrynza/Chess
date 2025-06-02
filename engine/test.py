import asyncio
import websockets
import json

async def connect():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ4NTA3NzE5LCJpYXQiOjE3NDg1MDQxMTksImp0aSI6IjlhOGY4ZDA3ZjE1ZDQ2MDdiZTA4OGFlZjM0MjBiZTAyIiwidXNlcl9pZCI6M30.KYRjE3KJJbZWiltkchvqndP_9w0uqrmCl3J2DECc0H4"
    uri = f"ws://127.0.0.1:8000/ws/game/1/?token={token}"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "command": "new_move",
            "source": "e2",
            "target": "e4",
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        }))
        response = await websocket.recv()
        print(response)

asyncio.run(connect())