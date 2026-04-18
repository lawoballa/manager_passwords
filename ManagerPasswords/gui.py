import customtkinter as ctk
import pyperclip
import database
import random
import string
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SecureVault - Авторизация")
        self.geometry("500x450")
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.label_title = ctk.CTkLabel(self, text="🔐 SecureVault", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, pady=30)
        
        self.entry_user = ctk.CTkEntry(self, placeholder_text="Логин", width=350, height=45)
        self.entry_user.grid(row=1, column=0, padx=20, pady=10)
        
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Мастер-пароль", show="*", width=350, height=45)
        self.entry_pass.grid(row=2, column=0, padx=20, pady=10)
        self.entry_pass.bind("<Return>", lambda event: self.login())
        
        self.btn_login = ctk.CTkButton(self, text="Войти в систему", command=self.login, height=45, width=350)
        self.btn_login.grid(row=3, column=0, padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="#FF5555", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=4, column=0, pady=5)
        
        self.hint_label = ctk.CTkLabel(self, text="Дефолтный вход: admin / admin123", 
                                       text_color="gray", font=ctk.CTkFont(size=10))
        self.hint_label.grid(row=5, column=0, pady=10)

    def login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get()
        
        if not user or not pwd:
            self.status_label.configure(text="⚠ Введите логин и пароль")
            return

        auth = database.authenticate(user, pwd)
        
        if auth:
            self.destroy()
            if auth['role'] == 'admin':
                AdminPanel(auth['id'], user).mainloop()
            else:
                UserPanel(auth['id'], user).mainloop()
        else:
            self.status_label.configure(text="❌ Неверный логин или пароль")

class UserPanel(ctk.CTk):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.title(f"SecureVault - Пользователь: {username}")
        self.geometry("1200x700")
        self.resizable(False, False)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.nav_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)
        
        self.lbl_user = ctk.CTkLabel(self.nav_frame, text=f"👤 {username}", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_user.pack(pady=30)
        
        self.btn_passwords = ctk.CTkButton(self.nav_frame, text="📂 Мои пароли", command=self.show_passwords, 
                                           anchor="w", height=45)
        self.btn_passwords.pack(pady=8, padx=15, fill="x")
        
        self.btn_add = ctk.CTkButton(self.nav_frame, text="➕ Добавить", command=self.show_add_form, 
                                     anchor="w", height=45)
        self.btn_add.pack(pady=8, padx=15, fill="x")
        
        self.btn_gen = ctk.CTkButton(self.nav_frame, text="🎲 Генератор", command=self.show_generator, 
                                     anchor="w", height=45)
        self.btn_gen.pack(pady=8, padx=15, fill="x")
        
        self.btn_logout = ctk.CTkButton(self.nav_frame, text="🚪 Выход", command=self.logout, 
                                        fg_color="#D32F2F", anchor="w", height=45)
        self.btn_logout.pack(pady=60, padx=15, fill="x")
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.show_passwords()

    def logout(self):
        """Выход на экран авторизации"""
        self.destroy()
        LoginWindow().mainloop()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass

    def show_passwords(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header_frame, text="Ваши сохраненные учетные данные", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄", width=45, height=35, 
                      command=self.show_passwords).pack(side="right")

        data = database.get_user_passwords(self.user_id)
        
        if not data:
            ctk.CTkLabel(self.content_frame, text="📭 Записей пока нет. Добавьте первый пароль!", 
                         text_color="gray", font=ctk.CTkFont(size=16)).pack(pady=80)
            return

        cols_frame = ctk.CTkFrame(self.content_frame, fg_color="#2B2B2B")
        cols_frame.pack(fill="x", padx=30, pady=(10, 0))
        ctk.CTkLabel(cols_frame, text="Сервис", width=180, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(cols_frame, text="Логин", width=180, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(cols_frame, text="Пароль", width=250, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(cols_frame, text="Действия", width=200, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=10, pady=10)

        for entry in data:
            row = ctk.CTkFrame(self.content_frame)
            row.pack(fill="x", padx=30, pady=3)
            
            ctk.CTkLabel(row, text=entry['service'], width=180, anchor="w", 
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=entry['login'], width=180, anchor="w", 
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
            
            pwd_frame = ctk.CTkFrame(row, fg_color="transparent")
            pwd_frame.pack(side="left", padx=10)
            
            pwd_text = entry['password'] if entry['password'] else "N/A"
            pwd_label = ctk.CTkLabel(pwd_frame, text="*" * len(pwd_text), width=180, 
                                     anchor="w", text_color="#4CAF50", font=ctk.CTkFont(size=12))
            pwd_label.pack(side="left")
            
            def toggle_password(label, password):
                def _toggle():
                    if label.cget("text")[0] == "*":
                        label.configure(text=password)
                    else:
                        label.configure(text="*" * len(password))
                return _toggle
            
            eye_btn = ctk.CTkButton(pwd_frame, text="👁️", width=35, height=28,
                                    command=toggle_password(pwd_label, pwd_text))
            eye_btn.pack(side="left", padx=5)
            
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="left", padx=10)
            
            ctk.CTkButton(btn_frame, text="Копировать", width=85, height=28, 
                          command=lambda p=entry['password']: self.copy_to_clipboard(p)).pack(side="left", padx=3)
            
            ctk.CTkButton(btn_frame, text="Удалить", width=85, height=28, fg_color="#D32F2F",
                          command=lambda eid=entry['id']: self.delete_entry(eid)).pack(side="left", padx=3)

    def copy_to_clipboard(self, text):
        if text:
            pyperclip.copy(text)
            messagebox.showinfo("Буфер обмена", "Пароль скопирован!")
        else:
            messagebox.showwarning("Ошибка", "Пустой пароль")

    def delete_entry(self, entry_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            database.delete_password_entry(entry_id)
            self.show_passwords()

    def show_add_form(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="➕ Добавить новую запись", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        ctk.CTkLabel(form_frame, text="Название сервиса", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(20, 5))
        self.e_service = ctk.CTkEntry(form_frame, placeholder_text="например, Google", 
                                      width=600, height=45, font=ctk.CTkFont(size=13))
        self.e_service.pack(pady=5, padx=20)
        
        ctk.CTkLabel(form_frame, text="Логин / Email", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(15, 5))
        self.e_login = ctk.CTkEntry(form_frame, placeholder_text="ваш@email.com", 
                                    width=600, height=45, font=ctk.CTkFont(size=13))
        self.e_login.pack(pady=5, padx=20)
        
        ctk.CTkLabel(form_frame, text="Пароль", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(15, 5))
        self.e_pass = ctk.CTkEntry(form_frame, placeholder_text="********", 
                                   width=600, height=45, font=ctk.CTkFont(size=13))
        self.e_pass.pack(pady=5, padx=20)
        
        ctk.CTkLabel(form_frame, text="URL сайта (опционально)", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(15, 5))
        self.e_url = ctk.CTkEntry(form_frame, placeholder_text="https://...", 
                                  width=600, height=45, font=ctk.CTkFont(size=13))
        self.e_url.pack(pady=5, padx=20)
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text="💾 Сохранить", command=self.save_entry, 
                      width=180, height=45, font=ctk.CTkFont(size=14)).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="❌ Отмена", command=self.show_passwords, 
                      fg_color="gray", width=180, height=45, font=ctk.CTkFont(size=14)).pack(side="left", padx=15)

    def save_entry(self):
        service = self.e_service.get().strip()
        login = self.e_login.get().strip()
        password = self.e_pass.get()
        url = self.e_url.get().strip()
        
        if not service or not login or not password:
            messagebox.showerror("Ошибка", "Поля Сервис, Логин и Пароль обязательны!")
            return
            
        database.add_password_entry(self.user_id, service, login, password, url)
        messagebox.showinfo("Успех", "Запись успешно сохранена!")
        self.show_passwords()

    def show_generator(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="🎲 Генератор надежных паролей", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        
        gen_frame = ctk.CTkFrame(self.content_frame)
        gen_frame.pack(pady=20, padx=50)
        
        length_label = ctk.CTkLabel(gen_frame, text="Длина пароля: 16 символов", 
                                    font=ctk.CTkFont(size=14))
        length_label.pack(pady=15)
        
        length_slider = ctk.CTkSlider(gen_frame, from_=8, to=64, number_of_steps=56, width=500,
                                      command=lambda v: length_label.configure(text=f"Длина пароля: {int(v)} символов"))
        length_slider.pack(pady=15)
        length_slider.set(16)
        
        use_special = ctk.CTkCheckBox(gen_frame, text="Использовать спецсимволы (!@#$%)", 
                                      font=ctk.CTkFont(size=13))
        use_special.pack(pady=15)
        use_special.select()
        
        gen_result = ctk.CTkEntry(gen_frame, placeholder_text="Здесь появится пароль", 
                                  width=500, height=55, font=ctk.CTkFont(size=16))
        gen_result.pack(pady=25)
        
        def generate():
            length = int(length_slider.get())
            chars = string.ascii_letters + string.digits
            if use_special.get():
                chars += "!@#$%^&*"
            pwd = ''.join(random.choice(chars) for _ in range(length))
            gen_result.delete(0, 'end')
            gen_result.insert(0, pwd)
        
        btn_frame = ctk.CTkFrame(gen_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="🔄 Сгенерировать", command=generate, 
                      width=180, height=45, font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="📋 Копировать", 
                      command=lambda: self.copy_to_clipboard(gen_result.get()), 
                      width=180, height=45, font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        
        ctk.CTkButton(gen_frame, text="← Назад к паролям", command=self.show_passwords, 
                      fg_color="gray", width=200, height=40).pack(pady=20)

class AdminPanel(ctk.CTk):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.title(f"SecureVault - Администратор: {username}")
        self.geometry("1200x700")
        self.resizable(False, False)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.nav_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)
        
        self.lbl_user = ctk.CTkLabel(self.nav_frame, text=f"👑 {username}", 
                                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700")
        self.lbl_user.pack(pady=30)
        
        self.btn_users = ctk.CTkButton(self.nav_frame, text="👥 Пользователи", command=self.show_users, 
                                       anchor="w", height=45)
        self.btn_users.pack(pady=8, padx=15, fill="x")
        
        self.btn_logs = ctk.CTkButton(self.nav_frame, text="📜 Журнал логов", command=self.show_logs, 
                                      anchor="w", height=45)
        self.btn_logs.pack(pady=8, padx=15, fill="x")
        
        self.btn_create = ctk.CTkButton(self.nav_frame, text="➕ Создать юзера", 
                                        command=self.show_create_user, anchor="w", height=45)
        self.btn_create.pack(pady=8, padx=15, fill="x")
        
        self.btn_logout = ctk.CTkButton(self.nav_frame, text="🚪 Выход", command=self.logout, 
                                        fg_color="#D32F2F", anchor="w", height=45)
        self.btn_logout.pack(pady=60, padx=15, fill="x")
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.show_users()

    def logout(self):
        """Выход на экран авторизации"""
        self.destroy()
        LoginWindow().mainloop()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass

    def show_users(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="👥 Управление пользователями", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=30, padx=30, anchor="w")
        
        users = database.get_all_users()
        if not users:
            ctk.CTkLabel(self.content_frame, text="Нет пользователей", 
                         font=ctk.CTkFont(size=16)).pack()
            return

        header = ctk.CTkFrame(self.content_frame, fg_color="#2B2B2B")
        header.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(header, text="ID", width=80, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(header, text="Логин", width=300, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(header, text="Роль", width=200, anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).pack(side="left", padx=15, pady=10)
        
        for u in users:
            row = ctk.CTkFrame(self.content_frame)
            row.pack(fill="x", padx=30, pady=3)
            ctk.CTkLabel(row, text=str(u[0]), width=80, anchor="w", 
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=u[1], width=300, anchor="w", 
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=15)
            role_color = "#FFD700" if u[2] == 'admin' else "#4CAF50"
            ctk.CTkLabel(row, text=u[2], width=200, anchor="w", 
                         text_color=role_color, font=ctk.CTkFont(size=12)).pack(side="left", padx=15)

    def show_logs(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="📜 Журнал событий системы", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=30, padx=30, anchor="w")
        
        logs = database.get_logs()
        if not logs:
            ctk.CTkLabel(self.content_frame, text="Записей в журнале нет", 
                         font=ctk.CTkFont(size=16)).pack()
            return

        for log in logs:
            row = ctk.CTkFrame(self.content_frame, fg_color="#1F1F1F")
            row.pack(fill="x", padx=30, pady=2)
            ctk.CTkLabel(row, text=f"[{log[2]}]", width=200, anchor="w", 
                         text_color="gray", font=ctk.CTkFont(size=11)).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=f"User ID: {log[0]}", width=150, anchor="w", 
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=log[1], anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=15)

    def show_create_user(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="➕ Создание нового пользователя", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=30)
        
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(pady=20, padx=50)
        
        ctk.CTkLabel(form_frame, text="Логин", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(20, 5))
        new_user = ctk.CTkEntry(form_frame, placeholder_text="Придумайте логин", 
                                width=500, height=45, font=ctk.CTkFont(size=13))
        new_user.pack(pady=5, padx=20)
        
        ctk.CTkLabel(form_frame, text="Пароль", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(15, 5))
        new_pass = ctk.CTkEntry(form_frame, placeholder_text="********", show="*", 
                                width=500, height=45, font=ctk.CTkFont(size=13))
        new_pass.pack(pady=5, padx=20)
        
        role_var = ctk.StringVar(value="user")
        ctk.CTkLabel(form_frame, text="Роль:", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=20, pady=(15, 5))
        role_menu = ctk.CTkOptionMenu(form_frame, values=["user", "admin"], 
                                      variable=role_var, width=500, height=45, 
                                      font=ctk.CTkFont(size=13))
        role_menu.pack(pady=10, padx=20)
        
        def create_action():
            username = new_user.get().strip()
            password = new_pass.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
                
            if database.create_user(username, password, role):
                messagebox.showinfo("Успех", f"Пользователь {username} создан!")
                self.show_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать (возможно логин занят)")
        
        ctk.CTkButton(form_frame, text="Создать пользователя", command=create_action, 
                      width=250, height=45, font=ctk.CTkFont(size=14)).pack(pady=30)
        ctk.CTkButton(form_frame, text="← Назад", command=self.show_users, 
                      fg_color="gray", width=250, height=45, font=ctk.CTkFont(size=14)).pack(pady=5)