from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import socket
import json 
import time

# UDP Configuration for Dynamic Control Center and Audio Control Center
DYNAMIC_CENTER_IP = "192.168.1.76"
DYNAMIC_CENTER_PORT_SEND = 33002
DYNAMIC_CENTER_PORT_RECV = 33001
AUDIO_CONTROL_PORT_SEND = 33003

# open a UDP socket once
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send a UDP message to dynamic control center
def udp_send(message: str, target_ip: str, target_port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('ascii'), (target_ip, target_port))
    sock.close()

# send a JSON-encoded UDP message to audio control center
def udp_send_json(data: dict, target_ip: str, target_port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    json_message = json.dumps(data)  
    sock.sendto(json_message.encode('ascii'), (target_ip, target_port))
    sock.close()

# listen for UDP messages on the given port and print received data.
async def udp_receive_loop(listen_port: int, duration: int = 20):
    sock.bind(("0.0.0.0", listen_port))  
    sock.setblocking(False)  
    print(f"Listening for UDP messages on port {listen_port} for {duration} seconds...")
    start_time = time.time()  

    try:
        while time.time() - start_time < duration:
            try:
                data, addr = sock.recvfrom(1024)  
                message = data.decode("ascii")
                print(f"Received from {addr}: {message}")
            except BlockingIOError:
                # No data received, wait briefly before checking again
                await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping UDP listener due to manual interruption...")
    finally:
        print("UDP listener stopped.")
        sock.close()


if __name__ == "__main__":
    udp_send("SetShake:1001,30,60,100", DYNAMIC_CENTER_IP, DYNAMIC_CENTER_PORT_SEND)
    time.sleep(3)
    udp_send_json({"Source":"Game01","Command":"AI01O02<!"}, DYNAMIC_CENTER_IP, AUDIO_CONTROL_PORT_SEND)
    time.sleep(3)
    asyncio.run(udp_receive_loop(DYNAMIC_CENTER_PORT_RECV, duration=20))

