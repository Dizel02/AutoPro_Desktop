import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import time
from validators import validate_email_task, validate_password_task # импорт ваших функций

class AutoProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoPro - Система управления")
        self.geometry("600x400")
        self.attempts = 0 # Счетчик попыток для блокировки
        self.current_user = None
        self.show_login_screen()

    # --- ЭКРАН ВХОДА ---
    def show_login_screen(self):
        self.clear_screen()
        tk.Label(self, text="Вход в систему", font=("Arial", 16)).pack(pady=20)
        
        self.login_entry = tk.Entry(self); self.login_entry.pack(pady=5)
        self.pass_entry = tk.Entry(self, show="*"); self.pass_entry.pack(pady=5)
        
        tk.Button(self, text="Войти", command=self.login_logic).pack(pady=10)
        tk.Button(self, text="Нет аккаунта? Регистрация", command=self.show_register_screen, fg="blue").pack()

    def login_logic(self):
        if self.attempts >= 3:
            messagebox.showerror("Блокировка", "3 ошибки! Приложение заблокировано на 30 секунд.")
            time.sleep(30) # Прямое требование ТЗ
            self.attempts = 0
            return

        login = self.login_entry.get()
        password = self.pass_entry.get()
        
        # Проверка в БД
        conn = sqlite3.connect('autopro.db')
        cursor = conn.cursor()
        cursor.execute('SELECT users.login, roles.name FROM users JOIN roles ON users.role_id = roles.id WHERE login=? AND password=?', (login, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.current_user = {"login": user[0], "role": user[1]}
            self.show_main_screen()
        else:
            self.attempts += 1
            messagebox.showerror("Ошибка", f"Неверный логин или пароль! Попытка: {self.attempts}/3")

    # --- ГЛАВНЫЙ ЭКРАН ---
    def show_main_screen(self):
        self.clear_screen()
        # Приветствие (п. 4 ТЗ)
        tk.Label(self, text=f"Привет, {self.current_user['login']}! ({self.current_user['role']})", font=("Arial", 12)).pack(pady=10)
        
        # Пример таблицы CRUD
        tk.Label(self, text="Список услуг:").pack()
        self.tree = ttk.Treeview(self, columns=("ID", "Название", "Цена"), show="headings", height=5)
        self.tree.heading("ID", text="ID"); self.tree.heading("Название", text="Услуга"); self.tree.heading("Цена", text="Цена")
        self.tree.pack(fill="x", padx=20)
        self.tree.insert("", "end", values=(1, "Замена масла", 2500)) # Тестовые данные

        # Кнопка удаления с текстом про котиков (п. 5 ТЗ)
        if self.current_user['role'] == "Администратор":
            tk.Button(self, text="Удалить выбранное", command=self.delete_with_cats, bg="red", fg="white").pack(pady=10)
        
        tk.Button(self, text="Выйти", command=self.confirm_exit).pack(side="bottom", pady=20)

    def delete_with_cats(self):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected)['values'][0]
        # Строгий текст из задания!
        msg = f"Вы действительно хотите удалить запись №{item}? Это действие нельзя отменить, и все ваши котики умрут от грусти."
        if messagebox.askyesno("Подтверждение", msg):
            self.tree.delete(selected)
            messagebox.showinfo("Удалено", "Запись удалена...")

    def confirm_exit(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.show_login_screen()

    def show_register_screen(self):
        # Здесь будет логика регистрации с вашими валидаторами
        messagebox.showinfo("Инфо", "Используйте validators.is_valid_email и is_valid_password здесь!")
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.winfo_children(): widget.destroy()

if __name__ == "__main__":
    app = AutoProApp()
    app.mainloop()
