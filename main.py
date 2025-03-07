from customtkinter import *
from PIL import Image
from socket import *


def change_appearance_mode(value):
    if value == 'Light':
        set_appearance_mode('light')
    else:
        set_appearance_mode('dark')


class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('300x300')
        self.title('Реєстрація')

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

            print("З'єднання встановлено, ім'я відправлено!")
        except:
            print('Немає запущеного сервера')

        self.destroy()
        window = MainWindow(name, sock)
        window.mainloop()


class MainWindow(CTk):
    def __init__(self, name, sock):
        super().__init__()

        self.load_avatar_button = None
        self.save_avatar_button = None
        self.avatar_label = None
        self.sett = None
        self.save_name_button = None
        self.entry_name = None
        self.name_label = None

        self.name = name
        self.sock = sock

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

        # текстова коробка (чат) – робимо її лише для читання
        self.chat_box = CTkTextbox(self)
        self.chat_box.configure(width=450, height=320)
        self.chat_box.place(x=30, y=30)
        # встановимо відразу лише для читання
        self.chat_box.configure(state='disabled')

        # entry для введення повідомлень
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
            # знищимо зайві віджети, якщо вони відкрити
            if self.name_label:
                self.name_label.destroy()
            if self.entry_name:
                self.entry_name.destroy()
            if self.save_name_button:
                self.save_name_button.destroy()
            if self.sett:
                self.sett.destroy()
            if self.avatar_label:
                self.avatar_label.destroy()
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
            # коли меню повністю відкрите – додаємо віджети
            if not self.avatar_label:
                if not self.name_label:
                    self.name_label = CTkLabel(self.menu_frame, text='name')
                    self.name_label.pack(pady=10)

                    self.entry_name = CTkEntry(self.menu_frame, placeholder_text=self.name)
                    self.entry_name.pack()

                    self.save_name_button = CTkButton(self.menu_frame, text='Save name', command=self.rename_user)
                    self.save_name_button.pack(pady=10)

                    self.sett = CTkComboBox(self.menu_frame, values=['Dark', 'Light'], command=change_appearance_mode)
                    self.sett.pack(side='bottom', pady=30)

            self.chat_box.place(x=self.menu_frame.winfo_width())
            self.chat_box.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                    height=self.winfo_height() - 100)
            self.is_animate = False

    def close_menu(self):
        if self.menu_frame.winfo_width() > 30:
            self.menu_frame.configure(width=self.menu_frame.winfo_width() - self.menu_open_speed)
            self.menu_button.configure(width=self.menu_frame.winfo_width())
            self.after(20, self.close_menu)
            self.is_animate = True
        else:
            self.chat_box.place(x=self.menu_frame.winfo_width())
            self.chat_box.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                    height=self.winfo_height() - 100)
            self.is_animate = False

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height() - self.menu_button.winfo_height())
        self.entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())
        self.entry.place(x=self.menu_frame.winfo_width(), y=self.winfo_height() - 50)

        if not self.is_animate:
            self.chat_box.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                    height=self.winfo_height() - 100)
        self.send_button.place(x=self.entry.winfo_x() + self.entry.winfo_width(), y=self.entry.winfo_y())

        self.after(30, self.adaptive_ui)

    def add_message(self, text, sender=False):
        # Робимо чат знову доступним для вставки:
        self.chat_box.configure(state='normal')
        # Якщо відправник – додаємо "Я:", інакше просто повідомлення
        prefix = "Я: " if sender else ""
        self.chat_box.insert(END, prefix + text + "\n")
        # Блокуємо поле, щоб не можна було редагувати:
        self.chat_box.configure(state='disabled')
        # Автоматичний скрол до останнього рядка:
        self.chat_box.see(END)

    def send_message(self):
        text = self.entry.get()
        if text:
            try:
                self.sock.send(text.encode())
            except:
                print("Помилка надсилання даних. Перевірте з'єднання з сервером!")
            # Додаємо повідомлення у вікно чату від відправника
            self.add_message(text, sender=True)
            self.entry.delete(0, END)

    def catch_message(self):
        try:
            m = self.sock.recv(1024).decode()
            if m:
                self.add_message(m, sender=False)
        except:
            pass

        self.after(200, self.catch_message)

    def rename_user(self):
        new_name = self.entry_name.get()  # наприклад, беремо з поля вводу
        if new_name:
            command = f"/rename {new_name}"
            self.sock.send(command.encode())
        else:
            print("Ім'я порожнє!")


registration_window = RegisterWindow()
registration_window.mainloop()
