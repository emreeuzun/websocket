import asyncio
import websockets
import json
import os

connected_clients = set()
sensor_data = {}

async def application(scope, receive, send):
    if scope['type'] == 'websocket':
        websocket = websockets.WebSocketCommonProtocol(scope, receive, send)
        connected_clients.add(websocket)
        print(f"Yeni WebSocket bağlantısı: {websocket.remote_address}") # Bağlantı logu
        try:
            async for message in websocket:
                print(f"Alınan mesaj: {message}") # Alınan mesajın logu
                try:
                    request = json.loads(message)
                    print(f"JSON olarak çözülen mesaj: {request}") # Çözülen JSON'ın logu
                    panel_id = request.get("panel_id")
                    print(f"Alınan panel_id: {panel_id}") # Alınan panel_id'nin logu

                    if panel_id:
                        sensor_data[panel_id] = {
                            "sicaklik": request["sicaklik"],
                            "nem": request["nem"],
                            "voltaj": request["voltaj"],
                            "akim": request["akim"],
                        }
                        print(f"Güncellenen sensor_data: {sensor_data}") # Güncellenen verinin logu

                    if panel_id in sensor_data:
                        response = json.dumps(sensor_data[panel_id])
                        print(f"Gönderilen yanıt: {response}") # Gönderilen yanıtın logu
                        await websocket.send(response)
                    else:
                        response = json.dumps({"error": "Geçersiz panel ID!"})
                        print(f"Hata yanıtı gönderildi: {response}") # Hata yanıtının logu
                        await websocket.send(response)
                except json.JSONDecodeError as e:
                    print(f"JSON çözme hatası: {e}") # JSON çözme hatasının logu
                    response = json.dumps({"error": "Geçersiz JSON formatı!"})
                    await websocket.send(response)
        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket bağlantısı kapandı: {websocket.remote_address}") # Bağlantı kapanma logu
            pass
        finally:
            connected_clients.remove(websocket)
            print(f"WebSocket bağlantısı istemcilerden kaldırıldı: {websocket.remote_address}") # İstemci kaldırma logu
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