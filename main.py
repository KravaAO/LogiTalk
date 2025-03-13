import io
import struct
import pickle
import threading

from customtkinter import *
from PIL import Image
from socket import socket, AF_INET, SOCK_STREAM
from tkinter import filedialog, messagebox


########################
# Допоміжні функції для pickle-обміну
########################

def send_pickle(sock, obj):
    """
    Серіалізуємо об'єкт (pickle) + відправляємо:
     1) 4 байти (довжина),
     2) самі дані.
    """
    data = pickle.dumps(obj)
    sock.sendall(struct.pack('>I', len(data)))  # '>I' = big-endian unsigned int
    sock.sendall(data)


def recv_pickle(sock):
    """
    Приймаємо (4 байти довжини) + (відповідну кількість байтів),
    далі розпаковуємо через pickle.loads.
    Повертає Python-об'єкт або None, якщо з’єднання перерване.
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


########################
# Клас повідомлення
########################

class MessageBubble(CTkFrame):
    """
    Простий віджет для відображення одного повідомлення у чаті:
      - Аватар відправника (CTkImage)
      - Текст
      - За бажанням - зображення (CTkImage)
    """
    def __init__(self, master,
                 avatar_ctk_image: CTkImage,
                 text: str,
                 is_sender: bool = False,
                 msg_image: CTkImage = None):
        super().__init__(master, corner_radius=10, fg_color="transparent")  # Прозорий фон

        # Колір фону повідомлення
        msg_bg = "#3a7ebf" if is_sender else "#2a2d2e"
        side = RIGHT if is_sender else LEFT  # розміщення: відправник справа

        if avatar_ctk_image is not None:
            avatar_label = CTkLabel(self, image=avatar_ctk_image, text="", bg_color="transparent")
            avatar_label.pack(side=side, padx=5)

        text_frame = CTkFrame(self, fg_color=msg_bg, corner_radius=15)
        text_frame.pack(side=side, padx=5, pady=2, fill=X)

        if text or (msg_image is None):
            text_label = CTkLabel(text_frame,
                                  text=text,
                                  font=("Arial", 14),
                                  text_color="white",
                                  wraplength=250,
                                  justify=LEFT)
            text_label.pack(padx=8, pady=5)

        if msg_image is not None:
            img_label = CTkLabel(text_frame, image=msg_image, text="")
            img_label.pack(padx=8, pady=5)


########################
# Налаштування appearance
########################

def change_appearance_mode(value):
    if value == 'Light':
        set_appearance_mode('light')
    else:
        set_appearance_mode('dark')


########################
# Вікно реєстрації
########################

class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('300x300')
        self.title('Реєстрація')

        self.image_path = 'profile.png'
        self.avatar_bytes = None

        self.image_ctk = CTkImage(light_image=Image.open(self.image_path), size=(100, 100))
        self.image_label = CTkLabel(self, text='', image=self.image_ctk)
        self.image_label.pack(pady=20)

        self.load_image_button = CTkButton(self, text='Обрати зображення', command=self.load_image)
        self.load_image_button.pack()

        self.name_entry = CTkEntry(self, placeholder_text="Введіть ім'я:")
        self.name_entry.pack(pady=15)

        self.reg_button = CTkButton(self, text='Зареєструватися', command=self.open_main_window)
        self.reg_button.pack()

        self.server_host = 'localhost'
        self.server_port = 5000

    def load_image(self):
        """Вибір аватара (байтів)."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            try:
                with open(self.image_path, 'rb') as f:
                    self.avatar_bytes = f.read()

                pil_img = Image.open(self.image_path)
                pil_img.thumbnail((100, 100))
                self.image_ctk = CTkImage(light_image=pil_img, size=pil_img.size)
                self.image_label.configure(image=self.image_ctk)
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити зображення:\n{e}")

    def open_main_window(self):
        """Підключаємось до сервера, надсилаємо registration і відкриваємо вікно чату."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Помилка", "Введіть ім'я!")
            return

        if not self.avatar_bytes:
            try:
                with open(self.image_path, 'rb') as f:
                    self.avatar_bytes = f.read()
            except:
                messagebox.showerror("Помилка", "Аватар не вибрано.")
                return

        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((self.server_host, self.server_port))
        except Exception as e:
            messagebox.showerror("Помилка", f"Неможливо підключитись до сервера:\n{e}")
            return

        registration_data = {
            "type": "registration",
            "name": name,
            "avatar": self.avatar_bytes
        }
        try:
            send_pickle(sock, registration_data)
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка відправки даних:\n{e}")
            return

        self.destroy()
        window = MainWindow(avatar_bytes=self.avatar_bytes, name=name, sock=sock)
        window.mainloop()


########################
# Головне вікно чату
########################

class MainWindow(CTk):
    def __init__(self, avatar_bytes, name, sock):
        super().__init__()
        self.title('LogTalk')
        self.geometry('600x450')

        # Зберігаємо дані
        self.my_avatar_bytes = avatar_bytes
        self.name = name
        self.sock = sock

        # Щоб коректно завершувати отримання повідомлень
        self.running = True
        self.chat_image_bytes = None

        self.title_label = CTkLabel(self, text='LogiTalk')
        self.title_label.pack()

        self.menu_button = CTkButton(self, text='m', width=30, command=self.toggle_open_menu)
        self.menu_button.place(x=0, y=0)

        self.menu_frame = CTkFrame(self, width=30)
        self.menu_frame.place(x=0, y=30)
        self.is_open_menu = False
        self.menu_open_speed = 20

        # Головний фрейм чату
        self.chat_frame = CTkScrollableFrame(self, width=500, height=320)
        self.chat_frame.place(x=30, y=30)

        # Поле введення
        self.entry = CTkEntry(self, placeholder_text='Введіть повідомлення', height=40, width=420)
        self.entry.place(x=30, y=390)

        # Кнопки
        self.load_img_button = CTkButton(self, text='📎', font=('Arial', 20),
                                         height=40, width=30, command=self.load_image)
        self.load_img_button.place(x=400, y=390)
        self.send_button = CTkButton(self, text='>', width=30, height=40, command=self.send_message)
        self.send_button.place(x=0, y=390)

        # Елементи меню
        self.avatar_label = None
        self.load_avatar_button = None
        self.name_label = None
        self.entry_name = None
        self.save_name_button = None
        self.sett = None

        self.is_animate = False

        # Запуск потоку
        self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listen_thread.start()

        # При закритті вікна – коректно зупинити
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.after(30, self.adaptive_ui)

    ########################
    # Робота з меню
    ########################
    def toggle_open_menu(self):
        """ бічне меню."""
        if self.is_open_menu:
            self.is_open_menu = False
            self.close_menu()

            if self.avatar_label:
                self.avatar_label.destroy()
            if self.load_avatar_button:
                self.load_avatar_button.destroy()
            if self.name_label:
                self.name_label.destroy()
            if self.entry_name:
                self.entry_name.destroy()
            if self.save_name_button:
                self.save_name_button.destroy()
            if self.sett:
                self.sett.destroy()
            self.avatar_label = None
            self.load_avatar_button = None
            self.name_label = None
            self.entry_name = None
            self.save_name_button = None
            self.sett = None

        else:
            self.is_open_menu = True
            self.open_menu()

    def open_menu(self):
        if self.menu_frame.winfo_width() < 200:
            self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.menu_open_speed)
            self.menu_button.configure(width=self.menu_frame.winfo_width())
            self.is_animate = True
            self.after(20, self.open_menu)
        else:
            if not self.avatar_label:
                # Аватар
                if self.my_avatar_bytes:
                    pil_img = Image.open(io.BytesIO(self.my_avatar_bytes))
                    pil_img.thumbnail((60, 60))
                    ctk_img = CTkImage(light_image=pil_img, size=pil_img.size)
                    self.avatar_label = CTkLabel(self.menu_frame, text='', image=ctk_img)
                    self.avatar_label._img_ref = ctk_img  # зберігаємо посилання
                else:
                    self.avatar_label = CTkLabel(self.menu_frame, text='Avatar')
                self.avatar_label.pack(pady=10)

                self.load_avatar_button = CTkButton(self.menu_frame, text='Load image', command=self.load_avatar)
                self.load_avatar_button.pack(pady=5)

                self.name_label = CTkLabel(self.menu_frame, text='Name')
                self.name_label.pack(pady=10)

                self.entry_name = CTkEntry(self.menu_frame, placeholder_text=self.name)
                self.entry_name.pack()

                self.save_name_button = CTkButton(self.menu_frame, text='Save name',
                                                  command=self.save_name)
                self.save_name_button.pack(pady=10)
                self.sett = CTkComboBox(self.menu_frame, values=['Dark', 'Light'], command=change_appearance_mode)
                self.sett.pack(side='bottom', pady=30)

            self.chat_frame.place(x=self.menu_frame.winfo_width(), y=30)
            self.chat_frame.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                      height=self.winfo_height() - 100)
            self.is_animate = False

    def close_menu(self):
        if self.menu_frame.winfo_width() > 30:
            self.menu_frame.configure(width=self.menu_frame.winfo_width() - self.menu_open_speed)
            self.menu_button.configure(width=self.menu_frame.winfo_width())
            self.after(20, self.close_menu)
            self.is_animate = True
        else:
            self.chat_frame.place(x=self.menu_frame.winfo_width(), y=30)
            self.chat_frame.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                      height=self.winfo_height() - 100)
            self.is_animate = False

    def load_avatar(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.my_avatar_bytes = f.read()
                pil_img = Image.open(io.BytesIO(self.my_avatar_bytes))
                pil_img.thumbnail((60, 60))
                ctk_img = CTkImage(light_image=pil_img, size=pil_img.size)
                self.avatar_label.configure(image=ctk_img, text='')
                self.avatar_label._img_ref = ctk_img
            except Exception as e:
                messagebox.showerror("Error", f"Cannot load avatar:\n{e}")

    def save_name(self):
        """Змінити своє локальне ім'я (на сервер це не надсилаємо)."""
        new_name = self.entry_name.get().strip()
        if new_name:
            self.name = new_name

    ########################
    # Основна логіка чату
    ########################
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height() - self.menu_button.winfo_height())
        self.entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() -
                                   self.load_img_button.winfo_width() -
                                   self.send_button.winfo_width() - 15)
        self.entry.place(x=self.menu_frame.winfo_width(), y=self.winfo_height() - 50)

        if not self.is_animate:
            self.chat_frame.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                      height=self.winfo_height() - 100)
            self.chat_frame.place(x=self.menu_frame.winfo_width(), y=30)

        self.send_button.place(x=self.winfo_width() - self.send_button.winfo_width() - 5,
                               y=self.entry.winfo_y())

        self.load_img_button.place(x=self.send_button.winfo_x() - self.load_img_button.winfo_width() - 5,
                                   y=self.entry.winfo_y())

        self.after(30, self.adaptive_ui)

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                with open(path, 'rb') as f:
                    self.chat_image_bytes = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot load image:\n{e}")
                self.chat_image_bytes = None

    def send_message(self):
        text = self.entry.get().strip()
        self.entry.delete(0, END)

        if not text and not self.chat_image_bytes:
            return

        msg_dict = {
            "type": "chat",
            "sender_name": self.name,
            "sender_avatar": self.my_avatar_bytes,
            "message_text": text,
            "image_bytes": self.chat_image_bytes
        }
        try:
            send_pickle(self.sock, msg_dict)
        except Exception as e:
            messagebox.showerror("Помилка", f"Неможливо відправити повідомлення:\n{e}")
            return

        self.add_message(avatar_bytes=self.my_avatar_bytes, text=text, is_sender=True,
                         image_bytes=self.chat_image_bytes)

        self.chat_image_bytes = None

    def listen_for_messages(self):
        while self.running:
            try:
                msg = recv_pickle(self.sock)
                if msg is None:
                    break  # З’єднання закрите
                if msg["type"] == "chat":
                    self.add_message(avatar_bytes=msg["sender_avatar"],
                                     text=msg["message_text"],
                                     is_sender=(msg["sender_name"] == self.name),
                                     image_bytes=msg["image_bytes"])
            except:
                break

        self.running = False
        self.after(0, self.destroy)

    def add_message(self, avatar_bytes, text, is_sender=False, image_bytes=None):
        """
        Створює віджет MessageBubble і додає у chat_frame.
        `avatar_bytes` – байти аватарки відправника,
        `text` – текст повідомлення,
        `image_bytes` – прикріплене зображення, якщо є.
        """
        avatar_ctk = None
        if avatar_bytes:
            try:
                pil_ava = Image.open(io.BytesIO(avatar_bytes))
                pil_ava.thumbnail((40, 40))
                avatar_ctk = CTkImage(light_image=pil_ava, size=pil_ava.size)
            except:
                pass

        msg_ctk_image = None
        if image_bytes:
            try:
                pil_msg = Image.open(io.BytesIO(image_bytes))
                pil_msg.thumbnail((200, 200))
                msg_ctk_image = CTkImage(light_image=pil_msg, size=pil_msg.size)
            except:
                pass

        bubble = MessageBubble(master=self.chat_frame,
                              avatar_ctk_image=avatar_ctk,
                              text=text,
                              is_sender=is_sender,
                              msg_image=msg_ctk_image)
        bubble.pack(anchor="e" if is_sender else "w", padx=10, pady=5)

        # примусово "проскролити"
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def on_close(self):
        """Зупиняємо цикл та закриваємо сокет."""
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        self.destroy()


set_appearance_mode('dark')
set_default_color_theme('blue')

registration_window = RegisterWindow()
registration_window.mainloop()
