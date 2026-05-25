import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import time
import os
from datetime import datetime
from validators import validate_email_task, validate_password_task

def log_action(user, action):
    if not os.path.exists('logs'): os.makedirs('logs')
    with open('logs/actions.log', 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] [{user}] {action}\n")

class AutoProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoPro - Ремонт автомобилей")
        self.geometry("600x500")
        self.attempts = 0
        self.show_login()

    def show_login(self):
        self.clear(); tk.Label(self, text="Вход в AutoPro", font=("Arial", 14)).pack(pady=20)
        self.l_ent = tk.Entry(self); self.l_ent.pack(pady=5)
        self.p_ent = tk.Entry(self, show="*"); self.p_ent.pack(pady=5)
        tk.Button(self, text="Войти", command=self.login).pack(pady=20)

    def login(self):
        if self.attempts >= 3:
            messagebox.showerror("Блокировка", "3 ошибки! Ждите 30 секунд.")
            time.sleep(30)
            self.attempts = 0
            return
        
        l, p = self.l_ent.get(), self.p_ent.get()
        if l == "admin" and p == "Admin123!": # Упрощенная проверка для примера
            log_action(l, "LOGIN_SUCCESS")
            self.main_screen(l)
        else:
            self.attempts += 1
            log_action(l, f"LOGIN_FAIL_ATTEMPT_{self.attempts}")
            messagebox.showerror("Ошибка", f"Неверно! Попытка {self.attempts}/3")

    def main_screen(self, user):
        self.clear()
        tk.Label(self, text=f"Привет, {user}! (Администратор)", font=("Arial", 12)).pack(pady=10)
        
        self.tree = ttk.Treeview(self, columns=("ID", "Услуга", "Цена"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.heading("Услуга", text="Услуга"); self.tree.heading("Цена", text="Цена")
        self.tree.pack(fill="x", padx=10)
        self.tree.insert("", "end", values=(1, "Замена масла", 2500))

        tk.Button(self, text="Удалить выбранное", bg="red", fg="white", command=self.delete_item).pack(pady=20)
        tk.Button(self, text="Выйти", command=self.confirm_exit).pack(side="bottom", pady=10)

    def delete_item(self):
        # ТОЧНЫЙ ТЕКСТ ИЗ ТЗ
        msg = "Вы действительно хотите удалить запись №1? Это действие нельзя отменить, и все ваши котики умрут от грусти."
        if messagebox.askyesno("ВНИМАНИЕ", msg):
            log_action("admin", "DELETE_ATTEMPT")
            messagebox.showinfo("Удалено", "Запись удалена. Котики в безопасности.")

    def confirm_exit(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.show_login()

    def clear(self):
        for w in self.winfo_children(): w.destroy()

if __name__ == "__main__":
    app = AutoProApp(); app.mainloop()
