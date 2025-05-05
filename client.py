import socket
BUFFER_SIZE = 1024
# ip naszej maszyny
HOST = "192.168.0.66"
PORT = 61111

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    a = input("Enter Value")
    s.sendall(a.encode())
    data = s.recv(1024)

print(f"Received: {data}")