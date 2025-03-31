import asyncio
import websockets
import json
import os

connected_clients = set()
sensor_data = {}

async def application(scope, receive, send):
    if scope['type'] == 'websocket':
        await send({"type": "websocket.accept"})
        try:
            while True:
                message = await receive()
                if message['type'] == 'websocket.receive':
                    try:
                        request = json.loads(message['bytes'].decode())
                        panel_id = request.get("panel_id")

                        if panel_id:
                            sensor_data[panel_id] = {
                                "sicaklik": request["sicaklik"],
                                "nem": request["nem"],
                                "voltaj": request["voltaj"],
                                "akim": request["akim"],
                            }

                        if panel_id in sensor_data:
                            response = json.dumps(sensor_data[panel_id])
                            await send({"type": "websocket.send", "bytes": response.encode()})
                        else:
                            response = json.dumps({"error": "Geçersiz panel ID!"})
                            await send({"type": "websocket.send", "bytes": response.encode()})
                    except json.JSONDecodeError as e:
                        response = json.dumps({"error": "Geçersiz JSON formatı!"})
                        await send({"type": "websocket.send", "bytes": response.encode()})
                elif message['type'] == 'websocket.disconnect':
                    break
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            connected_clients.discard(scope['asgi']['websocket']) # İstemciyi scope üzerinden kaldır
    elif scope['type'] == 'http':
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"text/plain"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"WebSocket server is running!",
            }
        )

async def main():
    port = int(os.environ.get("PORT", 8765))
    async with websockets.serve(application, "", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())