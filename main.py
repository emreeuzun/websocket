import asyncio
import websockets
import json
import os

# Panel verilerini saklamak için bir sözlük (dict)
panel_data = {}


async def handle_connection(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)

            # ESP32'den gelen veri mi, yoksa istemciden gelen sorgu mu kontrol et
            if "panel_id" in data and "sicaklik" in data:
                # ESP32 veri gönderiyor, kaydet
                panel_id = data["panel_id"]
                panel_data[panel_id] = {
                    "sicaklik": data["sicaklik"],
                    "nem": data["nem"],
                    "voltaj": data["voltaj"],
                    "akim": data["akim"]
                }
                print(f"📥 Veri alındı: {panel_id} -> {panel_data[panel_id]}")

            elif "panel_id" in data:
                # Mobil uygulama veri istiyor
                panel_id = data["panel_id"]
                if panel_id in panel_data:
                    await websocket.send(json.dumps(panel_data[panel_id]))
                    print(f"📤 Veri gönderildi: {panel_id} -> {panel_data[panel_id]}")
                else:
                    await websocket.send(json.dumps({"error": "Geçersiz panel ID!"}))
                    print(f"⚠️ Hata: Geçersiz panel ID - {panel_id}")

    except websockets.exceptions.ConnectionClosed:
        print("🔌 Bağlantı kesildi.")


async def start_server():
    port = int(os.environ.get("PORT", 8765))  # Bulut ortamında portu dinamik al
    server = await websockets.serve(handle_connection, "0.0.0.0", port)
    print(f"🚀 WebSocket sunucusu {port} portunda çalışıyor!")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_server())
