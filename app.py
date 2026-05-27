import csv
import datetime
import os
import re
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


# ==========================================
# 1. ЛОГИРОВАНИЕ СТРОГО ПО ШАБЛОНУ ТЗ
# ==========================================
def log_action(user, role, action, result="SUCCESS"):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Строгий формат по ТЗ: [дата и время] [имя пользователя] [роль] [действие] [результат]
    log_line = f"[{now}] [{user}] [{role}] [{action}] [{result}]\n"
    with open(os.path.join(log_dir, "actions.log"), "a", encoding="utf-8") as f:
        f.write(log_line)


# ==========================================
# 2. ВАЛИДАТОРЫ ПО ТЗ (С ПРОВЕРКОЙ ADMIN)
# ==========================================
def validate_email_local(email: str) -> bool:
    base_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(base_regex, email):
        return False
    if "@" in email:
        _, domain = email.split("@", 1)
        if "admin" in domain.lower():
            return False  # Блокируем 'admin' в домене по ТЗ
    return True


def validate_password_local(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    return True


# ==========================================
# 3. ИНИЦИАЛИЗАЦИЯ БД (3 СУЩНОСТИ)
# ==========================================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Roles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT UNIQUE, password TEXT, email TEXT, role_id INTEGER, specialization TEXT, FOREIGN KEY(role_id) REFERENCES Roles(id))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Services (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Technicians (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, grade TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Orders (id INTEGER PRIMARY KEY AUTOINCREMENT, car_model TEXT, service_id INTEGER, tech_id INTEGER, FOREIGN KEY(service_id) REFERENCES Services(id), FOREIGN KEY(tech_id) REFERENCES Technicians(id))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Settings (key TEXT PRIMARY KEY, value TEXT)"
    )

    cursor.execute("INSERT OR IGNORE INTO Roles (name) VALUES ('administrator')")
    cursor.execute("INSERT OR IGNORE INTO Roles (name) VALUES ('user')")
    cursor.execute(
        "INSERT OR IGNORE INTO Users (login, password, email, role_id, specialization) VALUES ('admin', 'Admin123!', 'boss@autopro.ru', 1, 'Главный инженер')"
    )

    cursor.execute("SELECT COUNT(*) FROM Services")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Services (name, price) VALUES ('Ремонт ДВС', 15000)")
        cursor.execute("INSERT INTO Services (name, price) VALUES ('Диагностика подвески', 1200)")
        cursor.execute("INSERT INTO Services (name, price) VALUES ('Замена масла', 800)")

    cursor.execute("SELECT COUNT(*) FROM Technicians")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Technicians (name, grade) VALUES ('Иванов А.А.', 'Старший мастер')")
        cursor.execute("INSERT INTO Technicians (name, grade) VALUES ('Петров И.С.', 'Электрик')")

    cursor.execute("SELECT COUNT(*) FROM Orders")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Orders (car_model, service_id, tech_id) VALUES ('Toyota Camry', 1, 1)")
        cursor.execute("INSERT INTO Orders (car_model, service_id, tech_id) VALUES ('Lada Vesta', 3, 2)")

    conn.commit()
    conn.close()
class AutoProApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AutoPro")
        self.geometry("850x650")
        self.attempts = 0
        self.lock_remaining = 0

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM Settings WHERE key='dark_mode'")
        row = cursor.fetchone()
        self.dark_mode = True if row and row[0] == "1" else False
        conn.close()

        self.current_user = None
        self.current_role = None
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO Settings (key, value) VALUES ('dark_mode', ?)",
            ("1" if self.dark_mode else "0",),
        )
        conn.commit()
        conn.close()
        self.main_screen(self.current_user)

    def apply_theme_styles(self):
        if self.dark_mode:
            self.bg = "#2b2b2b"
            self.fg = "white"
            self.entry_bg = "#3c3f41"
        else:
            self.bg = "#f0f0f0"
            self.fg = "black"
            self.entry_bg = "white"
        self.configure(bg=self.bg)

    def show_login(self):
        self.clear()
        self.apply_theme_styles()
        tk.Label(
            self,
            text="Вход в AutoPro",
            font=("Arial", 18, "bold"),
            bg=self.bg,
            fg=self.fg,
        ).pack(pady=30)
        tk.Label(self, text="Логин:", bg=self.bg, fg=self.fg).pack()
        self.l_ent = tk.Entry(self, width=30, bg=self.entry_bg, fg=self.fg, insertbackground=self.fg)
        self.l_ent.insert(0, "admin")
        self.l_ent.pack(pady=5)

        tk.Label(self, text="Пароль:", bg=self.bg, fg=self.fg).pack()
        self.p_ent = tk.Entry(
            self, show="*", width=30, bg=self.entry_bg, fg=self.fg, insertbackground=self.fg
        )
        self.p_ent.insert(0, "Admin123!")
        self.p_ent.pack(pady=5)

        self.btn_login = tk.Button(self, text="Войти", command=self.login_logic)
        self.btn_login.pack(pady=10)
        tk.Button(
            self,
            text="Регистрация",
            fg="blue",
            bd=0,
            bg=self.bg,
            command=self.show_registration,
        ).pack()
        self.lbl_lockout = tk.Label(self, text="", fg="red", bg=self.bg, font=("Arial", 11, "bold"))
        self.lbl_lockout.pack(pady=5)
    def show_registration(self):
        reg = tk.Toplevel(self)
        reg.title("Регистрация")
        reg.geometry("400x530")
        fields = ["Логин", "Email", "Пароль", "Подтверждение пароля", "Кастомное поле"]
        ents = {}
        for f in fields:
            tk.Label(reg, text=f).pack()
            e = tk.Entry(reg, show="*" if "пароль" in f.lower() else "")
            e.pack(pady=2)
            ents[f] = e

        def save():
            d = {k: v.get().strip() for k, v in ents.items()}
            if not all(d.values()):
                return messagebox.showerror("Ошибка", "Заполните все поля!")
            if d["Пароль"] != d["Подтверждение пароля"]:
                return messagebox.showerror("Ошибка", "Пароли не совпадают!")
            if not validate_email_local(d["Email"]):
                return messagebox.showerror(
                    "Ошибка", "Неверный Email (или содержит 'admin' в доменном имени)!"
                )
            if not validate_password_local(d["Пароль"]):
                return messagebox.showerror(
                    "Ошибка", "Пароль должен содержать от 8 знаков, заглавную букву и цифру!"
                )

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Users (login, password, email, role_id, specialization) VALUES (?, ?, ?, 2, ?)",
                    (d["Логин"], d["Пароль"], d["Email"], d["Кастомное поле"]),
                )
                conn.commit()
                messagebox.showinfo("Успех", "Аккаунт успешно создан!")
                log_action(d["Логин"], "user", "REGISTRATION")
                reg.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Этот логин уже занят!")
            finally:
                conn.close()

        tk.Button(reg, text="Создать аккаунт", command=save).pack(pady=20)

    def login_logic(self):
        if self.lock_remaining > 0:
            return
        l, p = self.l_ent.get().strip(), self.p_ent.get()
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Users.login, Roles.name FROM Users JOIN Roles ON Users.role_id = Roles.id WHERE Users.login = ? AND Users.password = ?",
            (l, p),
        )
        user_row = cursor.fetchone()
        conn.close()

        if user_row:
            self.attempts = 0
            self.current_user, self.current_role = user_row[0], user_row[1]
            log_action(self.current_user, self.current_role, "LOGIN", "SUCCESS")
            self.main_screen(self.current_user)
        else:
            self.attempts += 1
            log_action(l if l else "unknown", "none", "LOGIN_ATTEMPT", "FAIL")
            if self.attempts >= 3:
                messagebox.showerror("Ошибка", "3 неверные попытки! Блокировка 30 секунд")
                self.start_lockout()
            else:
                messagebox.showerror("Ошибка", f"Неверные данные! Попытка {self.attempts}/3")

    def start_lockout(self):
        self.lock_remaining = 30
        self.btn_login.config(state="disabled")
        self.update_lockout_timer()

    def update_lockout_timer(self):
        if self.lock_remaining > 0:
            self.lbl_lockout.config(text=f"Система заблокирована: {self.lock_remaining} сек.")
            self.lock_remaining -= 1
            self.after(1000, self.update_lockout_timer)
        else:
            self.lbl_lockout.config(text="")
            self.btn_login.config(state="normal")
            self.attempts = 0
    def main_screen(self, user):
        self.clear()
        self.geometry("850x600")
        self.apply_theme_styles()

        top = tk.Frame(self, bg=self.bg)
        top.pack(fill="x", padx=15, pady=5)
        tk.Label(
            top,
            text=f"Добро пожаловать, {user}!",
            font=("Arial", 14, "bold"),
            bg=self.bg,
            fg=self.fg,
        ).pack(side="left")
        tk.Label(top, text=f" Роль: [{self.current_role}]", fg="blue", bg=self.bg).pack(side="left")

        self.theme_var = tk.BooleanVar(value=self.dark_mode)
        tk.Checkbutton(
            top,
            text="Тёмная тема",
            variable=self.theme_var,
            command=self.toggle_theme,
            bg=self.bg,
            fg=self.fg,
            selectcolor=self.bg,
        ).pack(side="right")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        s_cnt = cursor.execute("SELECT COUNT(*) FROM Services").fetchone()[0]
        t_cnt = cursor.execute("SELECT COUNT(*) FROM Technicians").fetchone()[0]
        o_cnt = cursor.execute("SELECT COUNT(*) FROM Orders").fetchone()[0]
        conn.close()

        self.stats_lbl = tk.Label(
            self,
            text=f"Статистика | Услуг: {s_cnt} | Мастеров: {t_cnt} | Активных заказов: {o_cnt}",
            fg="gray",
            bg=self.bg,
        )
        self.stats_lbl.pack(anchor="w", padx=15, pady=5)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill="both", padx=10, pady=5)

        self.setup_services_tab()
        self.setup_tech_tab()
        self.setup_orders_tab()

        tk.Button(self, text="Выйти из системы", command=self.confirm_exit).pack(side="bottom", pady=10)

    def setup_services_tab(self):
        t1 = ttk.Frame(self.tabs)
        self.tabs.add(t1, text="Услуги")

        search_frame = tk.Frame(t1)
        search_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(search_frame, text="Поиск услуги:").pack(side="left")
        se = tk.Entry(search_frame, width=20)
        se.pack(side="left", padx=5)

        def do_search():
            q = se.get().strip().lower()
            for item in self.tree_s.get_children(): self.tree_s.delete(item)
            conn = sqlite3.connect("database.db"); cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM Services")
            for row in cursor.fetchall():
                if q in str(row).lower(): self.tree_s.insert("", "end", values=row)
            conn.close()

        tk.Button(search_frame, text="Искать", command=do_search).pack(side="left")
        tk.Button(search_frame, text="Сброс", command=lambda: [se.delete(0, "end"), self.refresh_all()]).pack(side="left", padx=5)

        self.tree_s = ttk.Treeview(t1, columns=("ID", "Имя", "Цена"), show="headings")
        for c in ("ID", "Имя", "Цена"): self.tree_s.heading(c, text=c)
        self.tree_s.pack(fill="both", expand=True, padx=5, pady=5)

        bf = tk.Frame(t1); bf.pack(pady=5)
        if self.current_role == "administrator":
            tk.Button(bf, text="+ Добавить", bg="green", fg="white", command=self.add_service_win).pack(side="left", padx=5)
            tk.Button(bf, text="Удалить запись", bg="red", fg="white", command=lambda: self.del_item(self.tree_s, "Services")).pack(side="left", padx=5)
        tk.Button(bf, text="Экспорт в CSV", command=lambda: self.export_csv("Services")).pack(side="left", padx=5)

    def setup_tech_tab(self):
        t2 = ttk.Frame(self.tabs); self.tabs.add(t2, text="Мастера")
        self.tree_t = ttk.Treeview(t2, columns=("ID", "ФИО", "Квалификация"), show="headings")
        for c in ("ID", "ФИО", "Квалификация"): self.tree_t.heading(c, text=c)
        self.tree_t.pack(fill="both", expand=True, padx=5, pady=5)

        bf = tk.Frame(t2); bf.pack(pady=5)
        if self.current_role == "administrator":
            tk.Button(bf, text="Удалить запись", bg="red", fg="white", command=lambda: self.del_item(self.tree_t, "Technicians")).pack(side="left", padx=5)
        tk.Button(bf, text="Экспорт в CSV", command=lambda: self.export_csv("Technicians")).pack(side="left", padx=5)

    def setup_orders_tab(self):
        t3 = ttk.Frame(self.tabs); self.tabs.add(t3, text="Заказы")
        self.tree_o = ttk.Treeview(t3, columns=("ID", "Автомобиль", "Услуга", "Мастер"), show="headings")
        for c in ("ID", "Автомобиль", "Услуга", "Мастер"): self.tree_o.heading(c, text=c)
        self.tree_o.pack(fill="both", expand=True, padx=5, pady=5)

        bf = tk.Frame(t3); bf.pack(pady=5)
        if self.current_role == "administrator":
            tk.Button(bf, text="Удалить запись", bg="red", fg="white", command=lambda: self.del_item(self.tree_o, "Orders")).pack(side="left", padx=5)
        tk.Button(bf, text="Экспорт в CSV", command=lambda: self.export_csv("Orders")).pack(side="left", padx=5)
        self.refresh_all()

    def refresh_all(self):
        for t in (self.tree_s, self.tree_t, self.tree_o):
            for item in t.get_children(): t.delete(item)
        conn = sqlite3.connect("database.db"); cursor = conn.cursor()
        for r in cursor.execute("SELECT id, name, price FROM Services").fetchall(): self.tree_s.insert("", "end", values=r)
        for r in cursor.execute("SELECT id, name, grade FROM Technicians").fetchall(): self.tree_t.insert("", "end", values=r)
        for r in cursor.execute("SELECT Orders.id, Orders.car_model, Services.name, Technicians.name FROM Orders JOIN Services ON Orders.service_id = Services.id JOIN Technicians ON Orders.tech_id = Technicians.id").fetchall(): self.tree_o.insert("", "end", values=r)
        
        s_cnt = cursor.execute("SELECT COUNT(*) FROM Services").fetchone()[0]
        t_cnt = cursor.execute("SELECT COUNT(*) FROM Technicians").fetchone()[0]
        o_cnt = cursor.execute("SELECT COUNT(*) FROM Orders").fetchone()[0]
        if hasattr(self, "stats_lbl"):
            self.stats_lbl.config(text=f"Статистика | Услуг: {s_cnt} | Мастеров: {t_cnt} | Активных заказов: {o_cnt}")
        conn.close()

    def add_service_win(self):
        win = tk.Toplevel(self); win.title("Добавить услугу"); win.geometry("300x230")
        tk.Label(win, text="Название услуги:").pack(pady=5)
        ne = tk.Entry(win, width=25); ne.pack()
        tk.Label(win, text="Цена:").pack(pady=5)
        pe = tk.Entry(win, width=25); pe.pack()
        lbl_err = tk.Label(win, text="", fg="red"); lbl_err.pack()

        def save():
            n, p = ne.get().strip(), pe.get().strip()
            if not n or not p: return messagebox.showerror("Ошибка", "Заполните все поля!")
            if len(n) < 3: return messagebox.showerror("Ошибка", "Название от 3 символов!")
            try:
                p_val = float(p)
                conn = sqlite3.connect("database.db"); cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM Services WHERE name = ?", (n,))
                if cursor.fetchone()[0] > 0:
                    lbl_err.config(text="Ошибка: Название уже дублируется в БД!")
                    conn.close(); return
                cursor.execute("INSERT INTO Services (name, price) VALUES (?, ?)", (n, p_val))
                conn.commit(); conn.close()
                log_action(self.current_user, self.current_role, "CREATE_SERVICE")
                self.refresh_all(); win.destroy()
            except ValueError: messagebox.showerror("Ошибка", "Цена должна быть числом!")
        tk.Button(win, text="Сохранить", command=save).pack(pady=10)

    def del_item(self, tree, table):
        selected = tree.selection()
        if not selected: return messagebox.showwarning("Внимание", "Выберите строку!")
        row_id = tree.item(selected)["values"][0]
        msg = f"Вы действительно хотите удалить запись №{row_id}? Это действие нельзя отменить, и все ваши котики умрут от грусти."
        if messagebox.askyesno("Подтверждение удаления", msg):
            conn = sqlite3.connect("database.db"); cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
            conn.commit(); conn.close()
            log_action(self.current_user, self.current_role, f"DELETE_{table.upper()}_ID_{row_id}")
            self.refresh_all()

    def export_csv(self, table):
        conn = sqlite3.connect("database.db"); cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table}"); rows = cursor.fetchall(); conn.close()
        filename = f"export_{table.lower()}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Field1", "Field2" if table != "Orders" else "Field3"])
            writer.writerows(rows)
        log_action(self.current_user, self.current_role, f"EXPORT_{table.upper()}")
        messagebox.showinfo("Успешно", f"Данные выгружены в файл {filename}!")

    def confirm_exit(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            log_action(self.current_user, self.current_role, "LOGOUT", "SUCCESS")
            self.show_login()


if __name__ == "__main__":
    init_db()
    app = AutoProApp()
    app.mainloop()
