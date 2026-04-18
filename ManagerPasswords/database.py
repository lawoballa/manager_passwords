import sqlite3
from datetime import datetime
import security

DB_NAME = "vault.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Инициализация БД и создание таблиц."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash BLOB,
            role TEXT DEFAULT 'user'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            login TEXT,
            password_enc BLOB,
            url TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            timestamp TEXT
        )
    """)
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed = security.hash_password("admin123")
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ("admin", hashed, "admin"))
        conn.commit()
        
    conn.close()
    log_action(1, "Система инициализирована. Создан админ.")

def authenticate(username, password):
    """Проверка логина и пароля."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and security.check_password(password, user[1]):
        return {"id": user[0], "role": user[2]}
    return None

def add_password_entry(user_id, service, login, password, url):
    """Добавление записи о пароле."""
    conn = get_connection()
    cursor = conn.cursor()
    key = security.load_key()
    enc_pwd = security.encrypt_data(password, key)
    
    cursor.execute("INSERT INTO passwords (user_id, service, login, password_enc, url) VALUES (?, ?, ?, ?, ?)",
                   (user_id, service, login, enc_pwd, url))
    
    log_action(user_id, f"Добавлен пароль для {service}")
    conn.commit()
    conn.close()

def get_user_passwords(user_id):
    """Получение всех паролей пользователя."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, service, login, password_enc, url FROM passwords WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    key = security.load_key()
    result = []
    for row in rows:
        try:
            dec_pwd = security.decrypt_data(row[3], key)
        except:
            dec_pwd = "Ошибка расшифровки"
        result.append({
            "id": row[0], "service": row[1], "login": row[2], 
            "password": dec_pwd, "url": row[4]
        })
    return result

def delete_password_entry(entry_id):
    """Удаление записи по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def get_all_users():
    """Для админа: список всех пользователей."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_logs():
    """Для админа: просмотр логов."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, action, timestamp FROM logs ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return rows

def log_action(user_id, action):
    """Запись действия в лог."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                       (user_id, action, timestamp))
        conn.commit()
    except Exception as e:
        print(f"Warning: Could not log action: {e}")
    finally:
        if conn:
            conn.close()

def create_user(username, password, role):
    """Создание нового пользователя (Админ)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed = security.hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()