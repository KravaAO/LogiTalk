from socket import *

HOST = 'localhost'
PORT = 52345

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
server_socket.setblocking(False)

# Словник: ключ = сокет клієнта, значення = ім’я клієнта
clients = {}


def broadcast(message, exclude_conn=None):
    """
    Розсилка повідомлення 'message' усім клієнтам,
    крім того, чиє з'єднання = 'exclude_conn' (за потреби).
    """
    for conn in list(clients.keys()):
        if conn != exclude_conn:
            try:
                conn.send(message.encode())
            except:
                # Якщо помилка – закриваємо цього клієнта та видаляємо зі словника
                name = clients[conn]
                print(f'[SERVER] Помилка надсилання для {name}, закриваємо з’єднання.')
                conn.close()
                del clients[conn]


while True:
    # 1) Приймаємо нові підключення (якщо вони є)
    try:
        connection, address = server_socket.accept()
        connection.setblocking(False)
        print(f'[SERVER] Нове підключення: {address}')

        # Перше, що отримуємо від клієнта – його ім’я
        name_client = connection.recv(1024).decode().strip()
        if not name_client:
            print(f'[SERVER] Не вдалося отримати ім’я від {address}, закриваємо з’єднання.')
            connection.close()
            continue

        # Додаємо його у словник
        clients[connection] = name_client
        print(f"[SERVER] Користувач '{name_client}' підключився до чату.")

        # Вітаємо особисто
        connection.send(f'Вітаю, {name_client} у LogiTalk чаті!'.encode())

        # Сповіщаємо решту користувачів
        broadcast(f"Привітайте нового учасника чату: {name_client}", exclude_conn=connection)

    except BlockingIOError:
        pass  # Немає вхідних з'єднань у цей момент
    except Exception as e:
        print(f'[SERVER] Помилка при прийманні з’єднання: {e}')

    # 2) Читаємо вхідні повідомлення від підключених клієнтів
    for conn in list(clients.keys()):
        try:
            data = conn.recv(1024)
            if not data:
                # Якщо порожні дані, припускаємо розрив з’єднання
                raise ConnectionResetError

            message = data.decode().strip()
            if message:
                # --- Перевіряємо, чи це команда на перейменування ---
                if message.startswith('/rename '):
                    # Нове ім’я після '/rename '
                    new_name = message[8:].strip()  # зрізаємо '/rename '
                    old_name = clients[conn]

                    if new_name:
                        # Оновлюємо ім’я у словнику
                        clients[conn] = new_name
                        # Повідомимо всіх про зміну імені
                        broadcast(f"{old_name} змінив(-ла) ім'я на {new_name}")
                        print(f"[SERVER] {old_name} -> {new_name} (зміна імені)")
                    else:
                        # Якщо /rename без нового імені, можна відправити відмову чи проігнорувати
                        conn.send("Нове ім'я порожнє. Спробуйте ще раз.".encode())

                else:
                    # Якщо це не /rename — розсилаємо звичайне повідомлення
                    sender_name = clients[conn]
                    print(f"[SERVER] Від {sender_name}: {message}")
                    broadcast(f"{sender_name}: {message}", exclude_conn=conn)

        except BlockingIOError:
            # Немає нових даних – пропускаємо
            pass
        except:
            # Клієнт відключився або сталася помилка
            disconnected_name = clients[conn]
            print(f"[SERVER] Клієнт {disconnected_name} відключився.")
            broadcast(f"{disconnected_name} покинув(-ла) чат.")
            conn.close()
            del clients[conn]
