from socket import *
from PIL import Image
import io

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('localhost', 52345))
server_socket.listen(5)
server_socket.setblocking(0)

clients = []

while True:
    try:
        connection, address = server_socket.accept()
        print(connection)
        #connection.setblocking(0)
        name_client = connection.recv(1024).decode().strip()
        try:
            data = b""
            while True:
                packet = connection.recv(4096)

                if not packet:
                    break
                data += packet

            # Збереження отриманого зображення
            image = Image.open(io.BytesIO(data))
            image.show()  # Відкриває зображення у Pillow
            print(data)
        except Exception as e:
            print(e)

        if name_client:
            connection.send(f'Вітаю {name_client} в LogiTalk чаті!'.encode())
            clients.append([connection, name_client])
            for client in clients:
                if client[0] != connection:
                    client[0].send(f'Привітайте нового учасника чата {name_client}'.encode())
    except:
        pass

    for client in clients[:]:
        try:
            message = client[0].recv(1024).decode().strip()
            print(message)
            for c in clients:
                if client != c:
                    c[0].send(f'{client[1]}: {message}'.encode())

        except BlockingIOError:
            pass
        except:
            print(f'Клієнт {client[1]} відключився.')
            client[0].close()
            clients.remove(client)
