import database
from gui import LoginWindow

if __name__ == "__main__":
    database.init_db()
    app = LoginWindow()
    app.mainloop()