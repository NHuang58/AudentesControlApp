import cv2
import socket
import struct
import pickle

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '0.0.0.0' 
    port = 9999
    
    server_socket.bind((host_ip, port))
    server_socket.listen(5)
    print(f"Server listening on port {port}...")

    client_socket, addr = server_socket.accept()
    print(f"Client connected from: {addr}")

    cap = cv2.VideoCapture(0)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            client_socket.sendall(message)
            
    except ConnectionResetError:
        print("Client disconnected.")
    finally:
        cap.release()
        client_socket.close()

if __name__ == "__main__":
    start_server()