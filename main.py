import asyncio
import websockets
import json
import os  # Ortam değişkenlerini okumak için

connected_clients = set()
sensor_data = {}

async def application(scope, receive, send):
    if scope['type'] == 'websocket':
        websocket = websockets.WebSocketCommonProtocol(scope, receive, send)
        connected_clients.add(websocket)
        try:
            async for message in websocket:
                request = json.loads(message)
                panel_id = request.get("panel_id")

                # Gelen veriyi panel_id'ye göre güncelle
                if panel_id:
                    sensor_data[panel_id] = {
                        "sicaklik": request["sicaklik"],
                        "nem": request["nem"],
                        "voltaj": request["voltaj"],
                        "akim": request["akim"],
                    }

                if panel_id in sensor_data:
                    response = json.dumps(sensor_data[panel_id])
                else:
                    response = json.dumps({"error": "Geçersiz panel ID!"})

                await websocket.send(response)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            connected_clients.remove(websocket)
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
                "body": b"WebSocket server is running!".encode(),
            }
        )

async def main():
    port = int(os.environ.get("PORT", 8765))  # Heroku'dan gelen PORT'u kullan veya varsayılanı al
    async with websockets.serve(application, "", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())