import sqlite3

def init_db():
    conn = sqlite3.connect('autopro.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS roles (id INTEGER PRIMARY KEY, name TEXT)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT UNIQUE, 
        password TEXT, email TEXT, role_id INTEGER,
        FOREIGN KEY(role_id) REFERENCES roles(id))''')
    cursor.execute('CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, name TEXT, price REAL)')
    
    cursor.execute('INSERT OR IGNORE INTO roles VALUES (1, "Администратор"), (2, "Пользователь")')
    cursor.execute('INSERT OR IGNORE INTO users (login, password, role_id) VALUES ("admin", "Admin123!", 1)')
    conn.commit(); conn.close()

if __name__ == "__main__":
    init_db()
