import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3, time, os, csv
from datetime import datetime
from validators import validate_email_task, validate_password_task

def log_action(user, role, action, result="SUCCESS"):
    if not os.path.exists('logs'): os.makedirs('logs')
    with open('logs/actions.log', 'a', encoding='utf-8') as f:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{ts}] [{user}] [{role}] [{action}] [{result}]\n")

class AutoProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoPro PR5 Final")
        self.geometry("800x650")
        self.attempts = 0
        self.dark_mode = False
        self.show_login()

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        color, text = ("#2b2b2b", "white") if self.dark_mode else ("#f0f0f0", "black")
        self.configure(bg=color)
        messagebox.showinfo("Тема", "Цветовая схема изменена!")

    def show_login(self):
        self.clear()
        tk.Label(self, text="Вход в AutoPro", font=("Arial", 18, "bold")).pack(pady=30)
        self.l_ent = tk.Entry(self, width=30); self.l_ent.insert(0, "admin"); self.l_ent.pack(pady=5)
        self.p_ent = tk.Entry(self, show="*", width=30); self.p_ent.insert(0, "Admin123!"); self.p_ent.pack(pady=5)
        tk.Button(self, text="Войти", command=self.login_logic).pack(pady=10)
        tk.Button(self, text="Регистрация", fg="blue", command=self.show_registration).pack()

    def show_registration(self):
        reg = tk.Toplevel(self); reg.title("Регистрация"); reg.geometry("400x500")
        fields = ["Логин", "Email", "Пароль", "Подтверждение пароля", "Марка авто"]
        ents = {}
        for f in fields:
            tk.Label(reg, text=f).pack()
            e = tk.Entry(reg, show="*" if "пароль" in f.lower() else ""); e.pack(pady=2); ents[f] = e
        
        def save():
            d = {k: v.get() for k, v in ents.items()}
            if d["Пароль"] != d["Подтверждение пароля"]: return messagebox.showerror("!", "Пароли разные")
            if not validate_email_task(d["Email"]) or not validate_password_task(d["Пароль"]):
                return messagebox.showerror("!", "Ошибка валидации Email или Пароля")
            messagebox.showinfo("!", "Успешно!"); reg.destroy()
        tk.Button(reg, text="Создать", command=save).pack(pady=20)

    def login_logic(self):
        if self.attempts >= 3:
            messagebox.showerror("!", "Ждите 30 сек"); time.sleep(30); self.attempts = 0; return
        l, p = self.l_ent.get(), self.p_ent.get()
        if l == "admin" and p == "Admin123!":
            log_action(l, "Админ", "LOGIN")
            self.main_screen(l)
        else:
            self.attempts += 1; messagebox.showerror("!", f"Ошибка {self.attempts}/3")

    def main_screen(self, user):
        self.clear()
        tk.Checkbutton(self, text="Тёмная тема", command=self.toggle_theme).pack(anchor="ne")
        tk.Label(self, text=f"Привет, {user}!", font=("Arial", 14)).pack()
        tk.Label(self, text="Мастеров: 4 | Услуг: 12", fg="gray").pack()

        tabs = ttk.Notebook(self)
        t1 = ttk.Frame(tabs); tabs.add(t1, text="Услуги"); tabs.pack(expand=1, fill="both", padx=10)
        
        tree = ttk.Treeview(t1, columns=("ID", "Имя", "Цена"), show="headings")
        for c in ("ID", "Имя", "Цена"): tree.heading(c, text=c)
        tree.pack(fill="x"); tree.insert("", "end", values=(1, "Ремонт ДВС", 15000))

        tk.Button(t1, text="Удалить запись", bg="red", fg="white", command=lambda: self.del_item(tree)).pack(pady=10)
        tk.Button(self, text="Экспорт в CSV", command=self.export_csv).pack(pady=5)
        tk.Button(self, text="Выйти", command=lambda: self.confirm_exit()).pack(side="bottom", pady=10)

    def del_item(self, tree):
        if not tree.selection(): return
        msg = "Вы действительно хотите удалить запись №1? Это действие нельзя отменить, и все ваши котики умрут от грусти."
        if messagebox.askyesno("Удаление", msg):
            tree.delete(tree.selection())
            log_action("admin", "Админ", "DELETE")

    def export_csv(self):
        with open('export.csv', 'w', newline='') as f:
            csv.writer(f).writerow(["ID", "Name", "Price"])
            csv.writer(f).writerow([1, "Ремонт ДВС", 15000])
        log_action("admin", "Админ", "EXPORT")
        messagebox.showinfo("CSV", "Файл создан!")

    def confirm_exit(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"): self.show_login()

if __name__ == "__main__":
    app = AutoProApp(); app.mainloop()
