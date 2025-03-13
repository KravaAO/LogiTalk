import socket
import threading
import pickle
import struct

SERVER_HOST = 'localhost'
SERVER_PORT = 5000

# Зберігаємо дані про клієнтів: {client_socket: {"name": str, "avatar": bytes}}
clients_data = {}


def send_pickle(sock, data):
    """
    Серіалізуємо об'єкт (pickle) та відправляємо:
    1) 4 байти (довжина),
    2) самі дані.
    """
    packet = pickle.dumps(data)
    packet_len = len(packet)
    sock.sendall(struct.pack('>I', packet_len))
    sock.sendall(packet)


def recv_pickle(sock):
    """
    Зчитуємо 4 байти, отримуємо довжину.
    Потім зчитуємо сам pickle.
    Повертаємо Python-об'єкт або None, якщо отримати не вдалося.
    """
    raw_len = sock.recv(4)
    if not raw_len:
        return None
    data_len = struct.unpack('>I', raw_len)[0]

    data = b''
    while len(data) < data_len:
        chunk = sock.recv(data_len - len(data))
        if not chunk:
            return None
        data += chunk

    return pickle.loads(data)


def broadcast_message(sender_socket, msg_dict):
    """Надсилає msg_dict усім клієнтам, крім відправника."""
    for client_socket in list(clients_data.keys()):
        if client_socket != sender_socket:
            try:
                send_pickle(client_socket, msg_dict)
            except:
                client_socket.close()
                del clients_data[client_socket]


def handle_client(client_socket):
    """Обробка підключень від одного клієнта."""
    while True:
        try:
            data = recv_pickle(client_socket)
            if data is None:
                # Клієнт відключився
                break

            if data["type"] == "registration":
                # Новий клієнт надіслав своє ім’я та аватар
                clients_data[client_socket] = {
                    "name": data["name"],
                    "avatar": data["avatar"]
                }
                print(f"Користувач '{data['name']}' підключився.")

            elif data["type"] == "chat":
                broadcast_message(client_socket, data)

        except Exception as e:
            print("Помилка при обробці повідомлення:", e)
            break

    if client_socket in clients_data:
        name = clients_data[client_socket]["name"]
        del clients_data[client_socket]
        print(f"Користувач '{name}' відключився.")
    else:
        print("Користувач 'Невідомий' відключився.")

    client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Сервер запущено на {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Новий клієнт підключився: {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
        thread.start()


start_server()
