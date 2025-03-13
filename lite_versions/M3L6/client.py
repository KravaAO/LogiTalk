from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')

        self.frame = CTkFrame(self, width=200, height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width=0)
        self.frame.place(x=0, y=0)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame, text='Ваше Ім`я')
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack()
        self.label_theme = CTkOptionMenu(self.frame, values=['Темна', 'Світла'], command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=20)
        self.theme = None
        self.btn = CTkButton(self, text='▶', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.menu_show_speed = 20

        self.chat_text = CTkTextbox(self, state='disable')
        self.chat_text.place(x=0, y=30)

        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення:')
        self.message_input.place(x=0, y=250)
        self.send_button = CTkButton(self, text='▶', width=40, height=30, command=self.send_message)
        self.send_button.place(x=200, y=250)

        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀')
        if self.is_show_menu:
            self.after(20, self.show_menu)

    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='▶')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    def change_theme(self, value):
        if value == 'Темна':
            set_appearance_mode('dark')
        else:
            set_appearance_mode('light')

    def adaptive_ui(self):
        self.chat_text.configure(width=self.winfo_width()-self.frame.winfo_width(), height=self.winfo_height()-self.message_input.winfo_height() - 30)
        self.chat_text.place(x=self.frame.winfo_width()-1)

        self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.send_button.winfo_width())
        self.message_input.place(x=self.frame.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())

        self.send_button.place(x=self.winfo_width()-self.send_button.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())

        self.after(20, self.adaptive_ui)

    def send_message(self):
        if self.message_input.get():
            self.add_message('Я:', self.message_input.get())
        self.message_input.delete(0, END)

    def add_message(self, name, message):
        self.chat_text.configure(state='normal')
        self.chat_text.insert(END, name + message + "\n")
        self.chat_text.configure(state='disable')


win = MainWindow()
win.mainloop()
