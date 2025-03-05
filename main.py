from customtkinter import *
from PIL import Image
from socket import *
import io
from random import *

class MessageBubble(CTkFrame):
    def __init__(self, master, avatar_path, text, is_sender=False):
        super().__init__(master, corner_radius=10, fg_color="transparent")  # Прозорий фон

        # Завантаження аватарки
        img = Image.open(avatar_path)
        self.avatar = CTkImage(light_image=img, size=(40, 40))

        # Колір повідомлення
        msg_bg = "#3a7ebf" if is_sender else "#2a2d2e"

        # Розміщення: відправник праворуч, отримувач ліворуч
        side = RIGHT if is_sender else LEFT
        align = "e" if is_sender else "w"

        # Аватарка
        avatar_label = CTkLabel(self, image=self.avatar, text="", bg_color="transparent")
        avatar_label.pack(side=side, padx=5)

        # Контейнер для тексту
        text_frame = CTkFrame(self, fg_color=msg_bg, corner_radius=15)
        text_frame.pack(side=side, padx=5, pady=2, fill=X)

        # Текстове повідомлення
        text_label = CTkLabel(text_frame, text=text, font=("Arial", 14), text_color="white", wraplength=250,
                              justify=LEFT, compound='top')
        text_label.pack(padx=8, pady=5)


def change_appearance_mode(value):
    if value == 'Light':
        set_appearance_mode('light')
    else:
        set_appearance_mode('dark')


class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()

        self.image_path = 'profile.png'

        self.geometry('300x300')
        self.title('Реєстрація')

        self.image_ctk = CTkImage(light_image=Image.open(self.image_path), size=(100, 100))
        self.image_label = CTkLabel(self, text='')
        self.image_label.pack(pady=20)

        self.load_image_button = CTkButton(self, text='Обрати зображення', command=self.load_image)
        self.load_image_button.pack()

        self.name_entry = CTkEntry(self, placeholder_text="Введіть ім'я:")
        self.name_entry.pack(pady=15)

        self.reg_button = CTkButton(self, text='Зареєструватися', command=self.open_main_window)
        self.reg_button.pack()

    def open_main_window(self):
        name = self.name_entry.get()
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect(('localhost', 52345))
            sock.setblocking(False)
            sock.send(name.encode())

            image = Image.open(self.image_path)

            # Конвертація зображення в байти
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')

            # Відправлення даних через сокет
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 52345))
            client_socket.sendall(image_bytes.getvalue())

            print("Зображення відправлено!")
        except:
            print('Немає запущеного сервера')

        self.destroy()
        window = MainWindow(self.image_path, name, sock)
        window.mainloop()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.image_ctk = CTkImage(light_image=Image.open(self.image_path), size=(100, 100))
            self.image_label.configure(image=self.image_ctk)


class MainWindow(CTk):
    def __init__(self, avatar_path, name, sock):
        super().__init__()

        self.load_avatar_button = None
        self.save_avatar_button = None
        self.avatar_label = None
        self.sett = None
        self.save_name_button = None
        self.entry_name = None
        self.name_label = None
        self.avatar_path = avatar_path
        self.name = name
        self.sock = sock
        self.avatar_image = CTkImage(light_image=Image.open(self.avatar_path), size=(60, 60))

        self.geometry('500x400')
        self.title('LogTalk')

        self.title_label = CTkLabel(self, text='LogiTalk')
        self.title_label.pack()

        self.menu_button = CTkButton(self, text='m', width=30, command=self.toggle_open_menu)
        self.menu_button.place(x=0, y=0)

        # menu frame
        self.menu_frame = CTkFrame(self, width=30)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.configure(width=30)
        self.menu_frame.place(x=0, y=30)
        self.is_open_menu = False
        self.menu_open_speed = 20

        # message_frame
        self.chat_frame = CTkScrollableFrame(self)

        self.chat_frame.configure(width=450, height=320)
        self.chat_frame.place(x=30, y=30)

        # entry
        self.entry = CTkEntry(self, placeholder_text='Введіть повідомлення', height=40, width=420)
        self.entry.place(x=30, y=350)

        self.send_button = CTkButton(self, text='>', width=30, height=40, command=self.send_message)
        self.send_button.place(x=0, y=350)
        self.is_animate = False

        self.catch_message()
        self.adaptive_ui()

    def toggle_open_menu(self):
        if self.is_open_menu:
            self.is_open_menu = False
            self.close_menu()
            self.name_label.destroy()
            self.entry_name.destroy()
            self.save_name_button.destroy()
            self.sett.destroy()
            self.avatar_label.destroy()
            self.load_avatar_button.destroy()
            self.avatar_label = None
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
                if not self.avatar_image:
                    self.avatar_label = CTkLabel(self.menu_frame, text='Avatar')
                else:
                    self.avatar_label = CTkLabel(self.menu_frame, text='', image=self.avatar_image)
                self.avatar_label.pack(pady=10)

                self.load_avatar_button = CTkButton(self.menu_frame, text='Load image', command=self.load_avatar)
                self.load_avatar_button.pack(pady=5)

                self.name_label = CTkLabel(self.menu_frame, text='name')
                self.name_label.pack(pady=10)

                self.entry_name = CTkEntry(self.menu_frame, placeholder_text=self.name)
                self.entry_name.pack()

                self.save_name_button = CTkButton(self.menu_frame, text='Save name')
                self.save_name_button.pack(pady=10)

                self.sett = CTkComboBox(self.menu_frame, values=['Dark', 'Light'], command=change_appearance_mode)
                self.sett.pack(side='bottom', pady=30)
            self.chat_frame.place(x=self.menu_frame.winfo_width())
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
            self.chat_frame.place(x=self.menu_frame.winfo_width())
            self.chat_frame.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                      height=self.winfo_height() - 100)
            self.is_animate = False

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height() - self.menu_button.winfo_height())
        self.entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())
        self.entry.place(x=self.menu_frame.winfo_width(), y=self.winfo_height() - 50)
        if not self.is_animate:
            self.chat_frame.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                      height=self.winfo_height() - 100)
        self.send_button.place(x=self.entry.winfo_x() + self.entry.winfo_width(), y=self.entry.winfo_y())

        self.after(30, self.adaptive_ui)

    def add_message(self, avatar_path, text, is_sender=False):
        msg = MessageBubble(self.chat_frame, avatar_path, text, is_sender=is_sender)
        msg.pack(anchor="e" if is_sender else "w", padx=10, pady=5)
        self.update_idletasks()

    def send_message(self):
        text = self.entry.get()
        if text:
            self.sock.send(text.encode())
            self.add_message(self.avatar_path, text, is_sender=True)
            self.entry.delete(0, END)

    def load_avatar(self):
        self.avatar_path = filedialog.askopenfilename()
        if self.avatar_path:
            self.avatar_image = CTkImage(Image.open(self.avatar_path), size=(60, 60))
            image_ctk = CTkImage(light_image=Image.open(self.avatar_path), size=(60, 60))
            self.avatar_label.configure(image=image_ctk, text='')

    def catch_message(self):
        try:
            m = self.sock.recv(1024).decode()
            if m:
                print(m)
                self.add_message(choice(['gamer.png', 'man.png']), m, is_sender=False)
        except:
            pass

        self.after(200, self.catch_message)


registration_window = RegisterWindow()
registration_window.mainloop()

