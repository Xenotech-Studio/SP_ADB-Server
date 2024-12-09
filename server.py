from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import socket
import json 
import time
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# UDP Configuration for Dynamic Control Center and Audio Control Center
DYNAMIC_CENTER_IP = "192.168.1.76"
DYNAMIC_CENTER_PORT_SEND = 33002
DYNAMIC_CENTER_PORT_RECV = 33001
AUDIO_CONTROL_PORT_SEND = 33003

# open a UDP socket once
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def open_socket():
    global sock
    if sock == None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Opened new socket")
    return sock

# # send a UDP message to dynamic control center
def udp_send(message: str, target_ip: str, target_port: int):
    sock = open_socket()
    sock.sendto(message.encode('ascii'), (target_ip, target_port))

# # send a JSON-encoded UDP message to audio control center
def udp_send_audio(data: str, target_ip: str, target_port: int):
    sock = open_socket()
    sock.sendto(data.encode('ascii'), (target_ip, target_port))

# # listen for UDP messages on the given port and print received data.
# async def udp_receive_loop(listen_port: int, duration: int = 20):
#     sock.bind(("0.0.0.0", listen_port))  
#     sock.setblocking(False)  
#     print(f"Listening for UDP messages on port {listen_port} for {duration} seconds...")
#     start_time = time.time()  

#     try:
#         while time.time() - start_time < duration:
#             try:
#                 data, addr = sock.recvfrom(1024)  
#                 message = data.decode("ascii")
#                 print(f"Received from {addr}: {message}")
#             except BlockingIOError:
#                 # No data received, wait briefly before checking again
#                 await asyncio.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\nStopping UDP listener due to manual interruption...")
#     finally:
#         print("UDP listener stopped.")
#         sock.close()


@app.post("/api/send")
async def send_command(data: Optional[str] = None):
    udp_send(data, DYNAMIC_CENTER_IP, DYNAMIC_CENTER_PORT_SEND)
    print(f"Sent to Dynamic Control Center: {data}")
    return {"status": "success"}

@app.post("/api/send_audio")
async def send_audio(data: Optional[str] = None):
    udp_send_audio(data, DYNAMIC_CENTER_IP, AUDIO_CONTROL_PORT_SEND)
    print(f"Sent to Audio Control Center: {data}")
    return {"status": "success"}

# @app.websocket("/ws/receive")
# async def websocket_recv(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         await udp_receive_loop(DYNAMIC_CENTER_PORT_RECV)
#     except WebSocketDisconnect:
#         print("UI disconnected from recv endpoint")








# ------------------------------ SOCKET ------------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/api/channels")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message from {websocket.client}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {websocket.client} disconnected.")

@app.get("/api/channels_test")
async def test():
    return {"message": "test success"}