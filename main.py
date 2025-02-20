from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('500x300')

        self.name = None
        self.font = ('Arial', 14, 'bold')
        self.label_title = CTkLabel(self, text='LogiTalk')
        self.label_title.pack()

        self.btn = CTkButton(self, text="☰", command=self.toggle_frame, font=self.font, width=20)
        self.btn.place(x=0, y=0)

        self.width_frame = 0
        self.is_show_menu = False
        self.frame = None
        self.text_box = CTkTextbox(self)
        self.text_box.pack(side='right', fill='both', expand=True)

        self.frame_message = CTkFrame(self, fg_color='yellow')
        self.frame_message.pack_propagate(False)
        self.frame_message.configure(width=500, height=30)
        self.frame_message.place(x=0, y=270)

        self.entry_message = CTkEntry(self.frame_message)

        self.entry_message.pack(side='left', fill='x', expand=True)

        self.btn_send = CTkButton(self.frame_message, text='⮞', width=30, command=self.send_message)
        self.btn_send.pack(side='right')

        self.update_pos_frame_message()

    def update_pos_frame_message(self):
        self.frame_message.place(y=self.winfo_height() - 30)
        self.frame_message.configure(width=self.winfo_width() - self.width_frame)
        self.after(5, self.update_pos_frame_message)

    def toggle_frame(self):
        if not self.is_show_menu:
            self.show_frame()
        else:
            self.hide_frame()

    def show_frame(self):
        if self.frame is None:
            self.frame = CTkFrame(self, fg_color='light blue')
            self.frame.pack(side='left', fill='y')
            self.frame.pack_propagate(False)

        self.width_frame = 0
        self.is_show_menu = True
        self.animate_frame_open()

    def hide_frame(self):
        self.width_frame = 200
        self.is_show_menu = False
        self.animate_frame_close()

    def animate_frame_open(self):
        if self.width_frame < 200:
            self.width_frame += 20
            self.frame.configure(width=self.width_frame)
            self.frame_message.place(x=self.width_frame)

            self.btn.configure(width=self.width_frame)
            self.frame_message.configure(width=self.winfo_width() - self.width_frame)
            self.after(10, self.animate_frame_open)
        else:
            self.label_name = CTkLabel(self.frame, text="Ім'я", font=self.font, text_color='black')
            self.label_name.pack(pady=10)
            self.entry_1 = CTkEntry(self.frame)
            self.entry_1.pack()

            self.btn_save = CTkButton(self.frame, text='Зберегти')
            self.btn_save.pack(pady=5)

    def animate_frame_close(self):
        if self.width_frame > 0:
            self.width_frame -= 20
            self.frame.configure(width=self.width_frame)
            self.btn.configure(width=self.width_frame)
            # зміни фрейма ентрі
            self.frame_message.place(x=self.width_frame)
            self.frame_message.configure(width=self.winfo_width() - self.width_frame)
            self.after(10, self.animate_frame_close)
        else:
            self.frame.pack_forget()
            self.frame.destroy()
            self.frame = None

    def send_message(self):
        msg = self.entry_message.get()
        if msg.strip():
            self.append_chat_message("Я", msg)
            self.entry_message.delete(0, "end")

    def append_chat_message(self, sender, message):
        self.text_box.configure(state="normal")
        self.text_box.insert("end", f"{sender}: {message}\n")
        self.text_box.configure(state="disabled")
        self.text_box.see("end")


window = MainWindow()
window.mainloop()
