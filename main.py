from flask import Flask, request
from flask_socketio import SocketIO, emit
import eventlet
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Panel verilerini tutacak sözlük
panels = {}

@socketio.on('connect')
def handle_connect():
    print("Bir cihaz bağlandı!")

@socketio.on('panel_data')
def handle_panel_data(data):
    panel_id = data.get("panel_id")
    if panel_id:
        panels[panel_id] = data
        print(f"Panel {panel_id} verileri güncellendi: {data}")
        emit("update", data, broadcast=True)  # Tüm istemcilere gönder

@socketio.on('get_data')
def send_panel_data(data):
    panel_id = data.get("panel_id")
    if panel_id in panels:
        emit("panel_data", panels[panel_id])

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
