import customtkinter as ctk
import pyperclip
import database
import random
import string
from tkinter import messagebox
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Категории по умолчанию
DEFAULT_CATEGORIES = ["Без категории", "Соцсети", "Банки", "Работа", "Почта", "Игры", "Покупки", "VPN"]

def check_password_strength(password):
    """Оценка надежности пароля."""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
        score += 1
    
    if score <= 2:
        return "Слабый", "#FF4444"
    elif score <= 4:
        return "Средний", "#FFA500"
    else:
        return "Сильный", "#00FF00"

def get_strength_color(password):
    """Получить цвет для индикатора надежности."""
    _, color = check_password_strength(password)
    return color

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
        self.geometry("1300x750")
        self.resizable(False, False)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.nav_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)
        
        self.lbl_user = ctk.CTkLabel(self.nav_frame, text=f"👤 {username}", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_user.pack(pady=30)
        
        self.btn_passwords = ctk.CTkButton(self.nav_frame, text="📂 Все пароли", command=self.show_passwords, 
                                           anchor="w", height=45)
        self.btn_passwords.pack(pady=8, padx=15, fill="x")
        
        self.btn_add = ctk.CTkButton(self.nav_frame, text="➕ Добавить", command=self.show_add_form, 
                                     anchor="w", height=45)
        self.btn_add.pack(pady=8, padx=15, fill="x")
        
        self.btn_categories = ctk.CTkButton(self.nav_frame, text="⁕ Категории", command=self.show_categories, 
                                           anchor="w", height=45)
        self.btn_categories.pack(pady=8, padx=15, fill="x")
        
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
        self.destroy()
        LoginWindow().mainloop()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass

    def show_passwords(self, category=None):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        if category:
            ctk.CTkLabel(header_frame, text=f"🏷️ {category}", 
                         font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        else:
            ctk.CTkLabel(header_frame, text="📂 Все сохраненные пароли", 
                         font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        
        ctk.CTkButton(header_frame, text="🔄", width=45, height=35, 
                      command=lambda: self.show_passwords(category)).pack(side="right")

        if category:
            data = database.get_passwords_by_category(self.user_id, category)
        else:
            data = database.get_user_passwords(self.user_id)
        
        if not data:
            ctk.CTkLabel(self.content_frame, text="📭 Записей пока нет. Добавьте первый пароль!", 
                         text_color="gray", font=ctk.CTkFont(size=16)).pack(pady=80)
            return

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=5)
        
        table_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        table_frame.pack(fill="x")
        
        table_frame.grid_columnconfigure(0, weight=2, minsize=150)
        table_frame.grid_columnconfigure(1, weight=2, minsize=150)
        table_frame.grid_columnconfigure(2, weight=2, minsize=150)
        table_frame.grid_columnconfigure(3, weight=1, minsize=100)
        table_frame.grid_columnconfigure(4, weight=3, minsize=250)
        
        # Заголовки
        header_row = ctk.CTkFrame(table_frame, fg_color="#2B2B2B", height=40)
        header_row.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 5))
        header_row.grid_propagate(False)
        
        ctk.CTkLabel(header_row, text="Сервис", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Логин", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=1, padx=130, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Пароль", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=2, padx=30, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Надежность", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=3, padx=120, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Действия", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=4, padx=0, pady=10, sticky="w")
        
        # Данные
        for i, entry in enumerate(data):
            row_idx = i + 1
            
            ctk.CTkLabel(table_frame, text=entry['service'], anchor="w", 
                         font=ctk.CTkFont(size=12)).grid(row=row_idx, column=0, padx=15, pady=5, sticky="w")
            
            ctk.CTkLabel(table_frame, text=entry['login'], anchor="w", 
                         font=ctk.CTkFont(size=12)).grid(row=row_idx, column=1, padx=15, pady=5, sticky="w")
            
            pwd_text = entry['password'] if entry['password'] else "N/A"
            pwd_container = ctk.CTkFrame(table_frame, fg_color="transparent")
            pwd_container.grid(row=row_idx, column=2, padx=15, pady=5, sticky="w")
            
            pwd_label = ctk.CTkLabel(pwd_container, text="*" * len(pwd_text), 
                                     anchor="w", text_color="#4CAF50", font=ctk.CTkFont(size=12))
            pwd_label.pack(side="left")
            
            def toggle_password(label, password):
                def _toggle():
                    if label.cget("text")[0] == "*":
                        label.configure(text=password)
                    else:
                        label.configure(text="*" * len(password))
                return _toggle
            
            eye_btn = ctk.CTkButton(pwd_container, text="👁️", width=30, height=25,
                                    command=toggle_password(pwd_label, pwd_text))
            eye_btn.pack(side="left", padx=5)
            
            strength_text, strength_color = check_password_strength(pwd_text if pwd_text != "Ошибка расшифровки" else "")
            strength_container = ctk.CTkFrame(table_frame, fg_color="transparent")
            strength_container.grid(row=row_idx, column=3, padx=15, pady=5, sticky="w")
            
            indicator = ctk.CTkLabel(strength_container, text="●", text_color=strength_color, 
                                     font=ctk.CTkFont(size=16))
            indicator.pack(side="left", padx=(0, 5))
            
            ctk.CTkLabel(strength_container, text=strength_text, text_color=strength_color, 
                         font=ctk.CTkFont(size=12)).pack(side="left")
            
            actions_container = ctk.CTkFrame(table_frame, fg_color="transparent")
            actions_container.grid(row=row_idx, column=4, padx=15, pady=5, sticky="w")
            
            ctk.CTkButton(actions_container, text="📋 Копировать", width=80, height=28, 
                          command=lambda p=entry['password']: self.copy_to_clipboard(p)).pack(side="left", padx=2)
            
            ctk.CTkButton(actions_container, text="✏️", width=35, height=28, 
                          command=lambda e=entry: self.edit_entry(e)).pack(side="left", padx=2)
            
            ctk.CTkButton(actions_container, text="🗑️", width=35, height=28, fg_color="#D32F2F",
                          command=lambda eid=entry['id']: self.delete_entry(eid)).pack(side="left", padx=2)

    def copy_to_clipboard(self, text):
        if text and text != "Ошибка расшифровки":
            pyperclip.copy(text)
            messagebox.showinfo("Буфер обмена", "Пароль скопирован!")
        else:
            messagebox.showwarning("Ошибка", "Некорректный пароль")

    def delete_entry(self, entry_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту запись?"):
            database.delete_password_entry(entry_id)
            self.show_passwords()

    def edit_entry(self, entry):
        """Редактирование записи."""
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="✏️ Редактировать запись", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(pady=10, padx=50, fill="both", expand=True)
        
        ctk.CTkLabel(form_frame, text="Название сервиса", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(10, 2))
        e_service = ctk.CTkEntry(form_frame, width=600, height=35, font=ctk.CTkFont(size=13))
        e_service.pack(pady=2, padx=20)
        e_service.insert(0, entry['service'])
        
        ctk.CTkLabel(form_frame, text="Логин / Email", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        e_login = ctk.CTkEntry(form_frame, width=600, height=35, font=ctk.CTkFont(size=13))
        e_login.pack(pady=2, padx=20)
        e_login.insert(0, entry['login'])
        
        ctk.CTkLabel(form_frame, text="Пароль", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        e_pass = ctk.CTkEntry(form_frame, width=600, height=35, font=ctk.CTkFont(size=13))
        e_pass.pack(pady=2, padx=20)
        e_pass.insert(0, entry['password'] if entry['password'] != "Ошибка расшифровки" else "")
        
        strength_label = ctk.CTkLabel(form_frame, text="Надежность: ", font=ctk.CTkFont(size=12))
        strength_label.pack(anchor="w", padx=20, pady=2)
        
        def update_strength(*args):
            pwd = e_pass.get()
            if pwd:
                text, color = check_password_strength(pwd)
                strength_label.configure(text=f"Надежность: {text}", text_color=color)
            else:
                strength_label.configure(text="Надежность: ", text_color="gray")
        
        e_pass.bind("<KeyRelease>", update_strength)
        
        ctk.CTkLabel(form_frame, text="URL сайта (опционально)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        e_url = ctk.CTkEntry(form_frame, width=600, height=35, font=ctk.CTkFont(size=13))
        e_url.pack(pady=2, padx=20)
        e_url.insert(0, entry['url'] if entry['url'] else "")
        
        ctk.CTkLabel(form_frame, text="Категория", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        categories = database.get_categories(self.user_id)
        if not categories:
            categories = DEFAULT_CATEGORIES
        else:
            categories = sorted(set(categories + DEFAULT_CATEGORIES))
        
        e_category = ctk.CTkOptionMenu(form_frame, values=categories, width=600, height=35, 
                                       font=ctk.CTkFont(size=13))
        e_category.pack(pady=2, padx=20)
        e_category.set(entry['category'] if entry['category'] else "Без категории")
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def save_edit():
            service = e_service.get().strip()
            login = e_login.get().strip()
            password = e_pass.get()
            url = e_url.get().strip()
            category = e_category.get()
            
            if not service or not login or not password:
                messagebox.showerror("Ошибка", "Поля Сервис, Логин и Пароль обязательны!")
                return
            
            database.update_password_entry(entry['id'], service, login, password, url, category)
            database.log_action(self.user_id, f"Обновлен пароль для {service}")
            messagebox.showinfo("Успех", "Запись обновлена!")
            self.show_passwords()
        
        ctk.CTkButton(btn_frame, text="💾 Сохранить", command=save_edit, 
                      width=160, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Отмена", command=self.show_passwords, 
                      fg_color="gray", width=160, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=10)

    def show_categories(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header_frame, text="🏷️ Категории", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        
        categories = database.get_categories(self.user_id)
        if not categories:
            ctk.CTkLabel(self.content_frame, text="Нет категорий. Добавьте пароли с категориями!", 
                         text_color="gray", font=ctk.CTkFont(size=16)).pack(pady=80)
            return
        
        cat_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cat_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        for i, category in enumerate(categories):
            data = database.get_passwords_by_category(self.user_id, category)
            count = len(data)
            
            btn = ctk.CTkButton(cat_frame, text=f"📁 {category}\n({count} шт.)", 
                               width=200, height=80, font=ctk.CTkFont(size=14),
                               command=lambda c=category: self.show_passwords(c))
            btn.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="ew")
        
        cat_frame.grid_columnconfigure(0, weight=1)
        cat_frame.grid_columnconfigure(1, weight=1)
        cat_frame.grid_columnconfigure(2, weight=1)

    def show_add_form(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="➕ Добавить новую запись", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(pady=10, padx=50, fill="both", expand=True)
        
        ctk.CTkLabel(form_frame, text="Название сервиса", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(10, 2))
        self.e_service = ctk.CTkEntry(form_frame, placeholder_text="например, Google", 
                                      width=600, height=35, font=ctk.CTkFont(size=13))
        self.e_service.pack(pady=2, padx=20)
        
        ctk.CTkLabel(form_frame, text="Логин / Email", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        self.e_login = ctk.CTkEntry(form_frame, placeholder_text="ваш@email.com", 
                                    width=600, height=35, font=ctk.CTkFont(size=13))
        self.e_login.pack(pady=2, padx=20)
        
        ctk.CTkLabel(form_frame, text="Пароль", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        self.e_pass = ctk.CTkEntry(form_frame, placeholder_text="********", 
                                   width=600, height=35, font=ctk.CTkFont(size=13))
        self.e_pass.pack(pady=2, padx=20)
        
        strength_label = ctk.CTkLabel(form_frame, text="Надежность: ", font=ctk.CTkFont(size=12))
        strength_label.pack(anchor="w", padx=20, pady=2)
        
        def update_strength(*args):
            pwd = self.e_pass.get()
            if pwd:
                text, color = check_password_strength(pwd)
                strength_label.configure(text=f"Надежность: {text}", text_color=color)
            else:
                strength_label.configure(text="Надежность: ", text_color="gray")
        
        self.e_pass.bind("<KeyRelease>", update_strength)
        
        ctk.CTkLabel(form_frame, text="URL сайта (опционально)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        self.e_url = ctk.CTkEntry(form_frame, placeholder_text="https://...", 
                                  width=600, height=35, font=ctk.CTkFont(size=13))
        self.e_url.pack(pady=2, padx=20)
        
        ctk.CTkLabel(form_frame, text="Категория", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        categories = database.get_categories(self.user_id)
        if not categories:
            categories = DEFAULT_CATEGORIES
        else:
            categories = sorted(set(categories + DEFAULT_CATEGORIES))
        
        self.e_category = ctk.CTkOptionMenu(form_frame, values=categories, width=600, height=35, 
                                            font=ctk.CTkFont(size=13))
        self.e_category.pack(pady=2, padx=20)
        self.e_category.set("Без категории")
        
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 Сохранить", command=self.save_entry, 
                      width=160, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Отмена", command=self.show_passwords, 
                      fg_color="gray", width=160, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=10)

    def save_entry(self):
        service = self.e_service.get().strip()
        login = self.e_login.get().strip()
        password = self.e_pass.get()
        url = self.e_url.get().strip()
        category = self.e_category.get()
        
        if not service or not login or not password:
            messagebox.showerror("Ошибка", "Поля Сервис, Логин и Пароль обязательны!")
            return
            
        database.add_password_entry(self.user_id, service, login, password, url, category)
        messagebox.showinfo("Успех", "Запись успешно сохранена!")
        self.show_passwords()

    def show_generator(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="🎲 Генератор надежных паролей", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        
        gen_frame = ctk.CTkFrame(self.content_frame)
        gen_frame.pack(pady=10, padx=50)
        
        length_label = ctk.CTkLabel(gen_frame, text="Длина пароля: 16 символов", 
                                    font=ctk.CTkFont(size=13))
        length_label.pack(pady=10)
        
        length_slider = ctk.CTkSlider(gen_frame, from_=8, to=64, number_of_steps=56, width=500,
                                      command=lambda v: length_label.configure(text=f"Длина пароля: {int(v)} символов"))
        length_slider.pack(pady=10)
        length_slider.set(16)
        
        use_special = ctk.CTkCheckBox(gen_frame, text="Использовать спецсимволы (!@#$%)", 
                                      font=ctk.CTkFont(size=12))
        use_special.pack(pady=10)
        use_special.select()
        
        gen_result = ctk.CTkEntry(gen_frame, placeholder_text="Здесь появится пароль", 
                                  width=500, height=45, font=ctk.CTkFont(size=15))
        gen_result.pack(pady=15)
        
        gen_strength_label = ctk.CTkLabel(gen_frame, text="", font=ctk.CTkFont(size=12))
        gen_strength_label.pack(pady=5)
        
        def generate():
            length = int(length_slider.get())
            chars = string.ascii_letters + string.digits
            if use_special.get():
                chars += "!@#$%^&*"
            pwd = ''.join(random.choice(chars) for _ in range(length))
            gen_result.delete(0, 'end')
            gen_result.insert(0, pwd)
            
            text, color = check_password_strength(pwd)
            gen_strength_label.configure(text=f"Надежность: {text}", text_color=color)
        
        btn_frame = ctk.CTkFrame(gen_frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(btn_frame, text="🔄 Сгенерировать", command=generate, 
                      width=150, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="📋 Копировать", 
                      command=lambda: self.copy_to_clipboard(gen_result.get()), 
                      width=150, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="➕ Добавить", 
                      command=lambda: self.add_generated_password(gen_result.get()), 
                      width=150, height=35, font=ctk.CTkFont(size=13)).pack(side="left", padx=8)
        
        ctk.CTkButton(gen_frame, text="← Назад к паролям", command=self.show_passwords, 
                      fg_color="gray", width=160, height=35, font=ctk.CTkFont(size=13)).pack(pady=15)
        
        generate()

    def add_generated_password(self, password):
        if not password:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте пароль!")
            return
        
        self.show_add_form()
        self.e_pass.delete(0, 'end')
        self.e_pass.insert(0, password)
        text, color = check_password_strength(password)
        for child in self.content_frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkLabel) and "Надежность:" in subchild.cget("text"):
                        subchild.configure(text=f"Надежность: {text}", text_color=color)

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
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header_frame, text="👥 Управление пользователями", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄", width=45, height=35, 
                      command=self.show_users).pack(side="right")
        
        users = database.get_all_users()
        if not users:
            ctk.CTkLabel(self.content_frame, text="Нет пользователей", 
                         font=ctk.CTkFont(size=16)).pack(pady=80)
            return

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=5)
        
        table_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        table_frame.pack(fill="x")
        
        # Настройка колонок
        table_frame.grid_columnconfigure(0, weight=1, minsize=80)
        table_frame.grid_columnconfigure(1, weight=2, minsize=200)
        table_frame.grid_columnconfigure(2, weight=1, minsize=150)
        table_frame.grid_columnconfigure(3, weight=2, minsize=250)
        
        # Заголовки
        header_row = ctk.CTkFrame(table_frame, fg_color="#2B2B2B", height=40)
        header_row.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        header_row.grid_propagate(False)
        
        ctk.CTkLabel(header_row, text="ID", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Логин", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=1, padx=120, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Роль", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=2, padx=130, pady=10, sticky="w")
        ctk.CTkLabel(header_row, text="Действия", anchor="w", 
                     font=ctk.CTkFont(weight="bold", size=13)).grid(row=0, column=3, padx=90, pady=10, sticky="w")
        
        # Данные
        for i, u in enumerate(users):
            row_idx = i + 1
            
            ctk.CTkLabel(table_frame, text=str(u[0]), anchor="w", 
                         font=ctk.CTkFont(size=12)).grid(row=row_idx, column=0, padx=20, pady=5, sticky="w")
            
            ctk.CTkLabel(table_frame, text=u[1], anchor="w", 
                         font=ctk.CTkFont(size=12)).grid(row=row_idx, column=1, padx=80, pady=5, sticky="w")
            
            role_color = "#FFD700" if u[2] == 'admin' else "#4CAF50"
            ctk.CTkLabel(table_frame, text=u[2], anchor="w", text_color=role_color, 
                         font=ctk.CTkFont(size=12)).grid(row=row_idx, column=2, padx=170, pady=5, sticky="w")
            
            if u[2] != 'admin':
                ctk.CTkButton(table_frame, text="🗑️ Удалить", width=100, height=28, fg_color="#D32F2F",
                              command=lambda uid=u[0], uname=u[1]: self.delete_user(uid, uname)).grid(row=row_idx, column=3, padx=20, pady=5, sticky="w")
            else:
                ctk.CTkLabel(table_frame, text="🔒 Администратор", anchor="w", 
                             text_color="#FFD700", font=ctk.CTkFont(size=12)).grid(row=row_idx, column=3, padx=20, pady=5, sticky="w")

    def delete_user(self, user_id, username):
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя '{username}'?\nВсе его пароли и логи будут также удалены!"):
            success, message = database.delete_user(user_id)
            if success:
                messagebox.showinfo("Успех", message)
                database.log_action(self.user_id, f"Удален пользователь {username} (ID: {user_id})")
                self.show_users()
            else:
                messagebox.showerror("Ошибка", message)

    def show_logs(self):
        self.clear_content()
        
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(header_frame, text="📜 Журнал событий системы", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        
        # Кнопки справа
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="🗑️ Очистить журнал", width=150, height=35, fg_color="#D32F2F",
                      command=self.clear_logs).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Обновить", width=120, height=35,
                      command=self.show_logs).pack(side="left", padx=5)
        
        logs = database.get_logs()
        if not logs:
            ctk.CTkLabel(self.content_frame, text="Записей в журнале нет", 
                         font=ctk.CTkFont(size=16)).pack(pady=80)
            return

        scroll_frame = ctk.CTkScrollableFrame(self.content_frame, height=500)
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        for log in logs:
            row = ctk.CTkFrame(scroll_frame, fg_color="#1F1F1F")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"[{log[2]}]", width=200, anchor="w", 
                         text_color="gray", font=ctk.CTkFont(size=11)).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=f"User ID: {log[0]}", width=150, anchor="w", 
                         font=ctk.CTkFont(size=11)).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=log[1], anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=15)

    def clear_logs(self):
        """Очистка журнала событий."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить весь журнал событий?\nЭто действие нельзя отменить!"):
            if database.clear_logs():
                messagebox.showinfo("Успех", "Журнал событий очищен!")
                database.log_action(self.user_id, "Журнал событий очищен администратором")
                self.show_logs()
            else:
                messagebox.showerror("Ошибка", "Не удалось очистить журнал!")

    def show_create_user(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="➕ Создание нового пользователя", 
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(pady=10, padx=50)
        
        ctk.CTkLabel(form_frame, text="Логин", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(10, 2))
        new_user = ctk.CTkEntry(form_frame, placeholder_text="Придумайте логин", 
                                width=500, height=35, font=ctk.CTkFont(size=13))
        new_user.pack(pady=2, padx=20)
        
        ctk.CTkLabel(form_frame, text="Пароль", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        new_pass = ctk.CTkEntry(form_frame, placeholder_text="********", show="*", 
                                width=500, height=35, font=ctk.CTkFont(size=13))
        new_pass.pack(pady=2, padx=20)
        
        role_var = ctk.StringVar(value="user")
        ctk.CTkLabel(form_frame, text="Роль:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(8, 2))
        role_menu = ctk.CTkOptionMenu(form_frame, values=["user", "admin"], 
                                      variable=role_var, width=500, height=35, 
                                      font=ctk.CTkFont(size=13))
        role_menu.pack(pady=2, padx=20)
        
        def create_action():
            username = new_user.get().strip()
            password = new_pass.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
                
            if database.create_user(username, password, role):
                messagebox.showinfo("Успех", f"Пользователь {username} создан!")
                database.log_action(self.user_id, f"Создан пользователь {username} (роль: {role})")
                self.show_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать (возможно логин занят)")
        
        ctk.CTkButton(form_frame, text="Создать пользователя", command=create_action, 
                      width=200, height=35, font=ctk.CTkFont(size=13)).pack(pady=20)
        ctk.CTkButton(form_frame, text="← Назад", command=self.show_users, 
                      fg_color="gray", width=200, height=35, font=ctk.CTkFont(size=13)).pack(pady=5)