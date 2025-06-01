"""
Головний модуль програми для роботи з датами та часом
Дата: 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import calendar
import locale
import mysql.connector
from mysql.connector import Error
import hashlib
import json
import os


class DatabaseManager:
    """Клас для управління базою даних користувачів"""

    def __init__(self):
        self.connection = None
        self.create_connection()
        self.create_tables()

    def create_connection(self):
        """Створення з'єднання з базою даних MySQL"""
        try:
            # Спроба підключення до локальної бази даних
            self.connection = mysql.connector.connect(
                host='localhost',
                database='datetime_app',
                user='root',
                password='1111',
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            print("Успішне підключення до MySQL")
        except Error as e:
            print(f"Помилка підключення до MySQL: {e}")
            self.use_file_database()

    def use_file_database(self):
        """Використання файлової бази даних як резервний варіант"""
        print("Використовується файлова база даних")
        self.connection = None

    def create_tables(self):
        """Створення таблиць в базі даних"""
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()

            # Створення таблиці користувачів
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            # Створення таблиці історії обчислень
            create_calculations_table = """
            CREATE TABLE IF NOT EXISTS calculations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                calculation_type VARCHAR(50),
                input_data TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """

            cursor.execute(create_users_table)
            cursor.execute(create_calculations_table)
            self.connection.commit()
            print("Таблиці створено успішно")

        except Error as e:
            print(f"Помилка створення таблиць: {e}")

    def register_user(self, username, password, email=""):
        """Реєстрація нового користувача"""
        if not self.connection:
            return self.file_register_user(username, password, email)

        try:
            cursor = self.connection.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            query = "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, password_hash, email))
            self.connection.commit()
            return True

        except Error as e:
            print(f"Помилка реєстрації: {e}")
            return False

    def login_user(self, username, password):
        """Авторизація користувача"""
        if not self.connection:
            return self.file_login_user(username, password)

        try:
            cursor = self.connection.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            query = "SELECT id, username FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, password_hash))
            result = cursor.fetchone()

            if result:
                return {"id": result[0], "username": result[1]}
            return None

        except Error as e:
            print(f"Помилка авторизації: {e}")
            return None

    def save_calculation(self, user_id, calc_type, input_data, result):
        """Збереження результату обчислення"""
        if not self.connection:
            return self.file_save_calculation(user_id, calc_type, input_data, result)

        try:
            cursor = self.connection.cursor()
            query = """INSERT INTO calculations (user_id, calculation_type, input_data, result) 
                      VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (user_id, calc_type,
                           str(input_data), str(result)))
            self.connection.commit()

        except Error as e:
            print(f"Помилка збереження обчислення: {e}")

    def get_user_calculations(self, user_id):
        """Отримання історії обчислень користувача"""
        if not self.connection:
            return self.file_get_calculations(user_id)

        try:
            cursor = self.connection.cursor()
            query = """SELECT calculation_type, input_data, result, created_at 
                      FROM calculations WHERE user_id = %s ORDER BY created_at DESC LIMIT 10"""
            cursor.execute(query, (user_id,))
            return cursor.fetchall()

        except Error as e:
            print(f"Помилка отримання історії: {e}")
            return []

    # Файлові методи як резервні
    def file_register_user(self, username, password, email=""):
        """Реєстрація користувача у файлі"""
        users_file = "users.json"
        users = {}

        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)

        if username in users:
            return False

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        users[username] = {
            "password_hash": password_hash,
            "email": email,
            "id": len(users) + 1
        }

        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

        return True

    def file_login_user(self, username, password):
        """Авторизація користувача з файлу"""
        users_file = "users.json"

        if not os.path.exists(users_file):
            return None

        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)

        if username not in users:
            return None

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password_hash"] == password_hash:
            return {"id": users[username]["id"], "username": username}

        return None

    def file_save_calculation(self, user_id, calc_type, input_data, result):
        """Збереження обчислення у файл"""
        calc_file = f"calculations_{user_id}.json"
        calculations = []

        if os.path.exists(calc_file):
            with open(calc_file, 'r', encoding='utf-8') as f:
                calculations = json.load(f)

        calculations.append({
            "type": calc_type,
            "input": str(input_data),
            "result": str(result),
            "timestamp": datetime.now().isoformat()
        })

        # Зберігаємо тільки останні 10 обчислень
        calculations = calculations[-10:]

        with open(calc_file, 'w', encoding='utf-8') as f:
            json.dump(calculations, f, ensure_ascii=False, indent=2)

    def file_get_calculations(self, user_id):
        """Отримання історії обчислень з файлу"""
        calc_file = f"calculations_{user_id}.json"

        if not os.path.exists(calc_file):
            return []

        with open(calc_file, 'r', encoding='utf-8') as f:
            calculations = json.load(f)

        return [(calc["type"], calc["input"], calc["result"], calc["timestamp"])
                for calc in reversed(calculations)]


class DateTimeCalculator:
    """Основний клас для обчислень з датами та часом"""

    def __init__(self):
        # Встановлення української локалі
        try:
            locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'Ukrainian')
            except:
                pass

    def calculate_date_difference(self, date1, date2):
        """Обчислення різниці між датами"""
        try:
            if isinstance(date1, str):
                date1 = datetime.strptime(date1, "%Y-%m-%d")
            if isinstance(date2, str):
                date2 = datetime.strptime(date2, "%Y-%m-%d")

            difference = abs((date2 - date1).days)

            # Детальний розрахунок
            years = difference // 365
            remaining_days = difference % 365
            months = remaining_days // 30
            days = remaining_days % 30

            result = {
                "total_days": difference,
                "years": years,
                "months": months,
                "days": days,
                "weeks": difference // 7
            }

            return result

        except Exception as e:
            raise ValueError(f"Помилка обчислення різниці дат: {e}")

    def get_day_of_week(self, date):
        """Визначення дня тижня"""
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d")

            days_uk = [
                "Понеділок", "Вівторок", "Середа", "Четвер",
                "П'ятниця", "Субота", "Неділя"
            ]

            day_number = date.weekday()
            day_name = days_uk[day_number]

            return {
                "day_name": day_name,
                "day_number": day_number + 1,
                "is_weekend": day_number >= 5
            }

        except Exception as e:
            raise ValueError(f"Помилка визначення дня тижня: {e}")

    def add_days_to_date(self, date, days):
        """Додавання днів до дати"""
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d")

            new_date = date + timedelta(days=days)

            return {
                "new_date": new_date.strftime("%Y-%m-%d"),
                "day_of_week": self.get_day_of_week(new_date)["day_name"],
                "formatted_date": new_date.strftime("%d.%m.%Y")
            }

        except Exception as e:
            raise ValueError(f"Помилка додавання днів: {e}")

    def get_age(self, birth_date):
        """Обчислення віку"""
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

            today = datetime.now()
            age = today.year - birth_date.year

            # Перевірка, чи був день народження в цьому році
            if today.month < birth_date.month or \
               (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1

            # Обчислення точного віку
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)

            days_to_birthday = (next_birthday - today).days

            return {
                "age_years": age,
                "days_to_birthday": days_to_birthday,
                "total_days_lived": (today - birth_date).days
            }

        except Exception as e:
            raise ValueError(f"Помилка обчислення віку: {e}")

    def get_calendar_month(self, year, month):
        """Отримання календаря місяця"""
        try:
            cal = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]

            return {
                "calendar": cal,
                "month_name": month_name,
                "year": year,
                "days_in_month": calendar.monthrange(year, month)[1]
            }

        except Exception as e:
            raise ValueError(f"Помилка створення календаря: {e}")

    def is_leap_year(self, year):
        """Перевірка чи є рік високосним"""
        return calendar.isleap(year)

    def get_working_days(self, start_date, end_date):
        """Обчислення робочих днів між датами"""
        try:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")

            working_days = 0
            current_date = start_date

            while current_date <= end_date:
                if current_date.weekday() < 5:  # Понеділок-П'ятниця
                    working_days += 1
                current_date += timedelta(days=1)

            total_days = (end_date - start_date).days + 1
            weekend_days = total_days - working_days

            return {
                "working_days": working_days,
                "weekend_days": weekend_days,
                "total_days": total_days
            }

        except Exception as e:
            raise ValueError(f"Помилка обчислення робочих днів: {e}")


class LoginWindow:
    """Вікно авторизації"""

    def __init__(self, db_manager, on_success_callback):
        self.db_manager = db_manager
        self.on_success_callback = on_success_callback
        self.current_user = None

        self.window = tk.Tk()
        self.window.title("Авторизація - Програма роботи з датами")
        self.window.geometry("400x300")
        self.window.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Центрування вікна на екрані"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"400x300+{x}+{y}")

    def create_widgets(self):
        """Створення віджетів вікна авторизації"""
        # Заголовок
        title_label = tk.Label(
            self.window,
            text="Програма роботи з датами та часом",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=20)

        # Фрейм для форми
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20)

        # Поля вводу
        tk.Label(form_frame, text="Ім'я користувача:", font=(
            "Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(
            form_frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Пароль:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(
            form_frame, width=25, show="*", font=("Arial", 10))
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)

        # Кнопки
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)

        login_btn = tk.Button(
            button_frame,
            text="Увійти",
            command=self.login,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12
        )
        login_btn.pack(side=tk.LEFT, padx=5)

        register_btn = tk.Button(
            button_frame,
            text="Реєстрація",
            command=self.register,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12
        )
        register_btn.pack(side=tk.LEFT, padx=5)

        guest_btn = tk.Button(
            button_frame,
            text="Гостьовий режим",
            command=self.guest_mode,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        )
        guest_btn.pack(side=tk.LEFT, padx=5)

        self.window.bind('<Return>', lambda event: self.login())

    def login(self):
        """Авторизація користувача"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Помилка", "Заповніть всі поля!")
            return

        user = self.db_manager.login_user(username, password)
        if user:
            self.current_user = user
            self.window.destroy()
            self.on_success_callback(user)
        else:
            messagebox.showerror(
                "Помилка", "Невірне ім'я користувача або пароль!")

    def register(self):
        """Реєстрація нового користувача"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Помилка", "Заповніть всі поля!")
            return

        if len(password) < 4:
            messagebox.showerror(
                "Помилка", "Пароль повинен містити мінімум 4 символи!")
            return

        email = simpledialog.askstring(
            "Email", "Введіть email (необов'язково):", initialvalue="")

        if self.db_manager.register_user(username, password, email or ""):
            messagebox.showinfo("Успіх", "Користувач зареєстрований успішно!")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Помилка", "Користувач з таким ім'ям вже існує!")

    def guest_mode(self):
        """Гостьовий режим"""
        guest_user = {"id": 0, "username": "Гість"}
        self.current_user = guest_user
        self.window.destroy()
        self.on_success_callback(guest_user)

    def run(self):
        """Запуск вікна авторизації"""
        self.window.mainloop()
        return self.current_user


class DateTimeApp:
    """Головний клас програми з графічним інтерфейсом"""

    def __init__(self, user, db_manager):
        self.user = user
        self.db_manager = db_manager
        self.calculator = DateTimeCalculator()

        self.root = tk.Tk()
        self.root.title(f"Програма роботи з датами - {user['username']}")
        self.root.geometry("800x600")

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Центрування вікна на екрані"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")

    def create_widgets(self):
        """Створення основного інтерфейсу"""
        # Створення notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладки
        self.create_date_difference_tab()
        self.create_day_of_week_tab()
        self.create_date_operations_tab()
        self.create_age_calculator_tab()
        self.create_calendar_tab()
        self.create_working_days_tab()
        self.create_history_tab()

    def create_date_difference_tab(self):
        """Вкладка обчислення різниці між датами"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Різниця між датами")

        # Заголовок
        title = tk.Label(frame, text="Обчислення різниці між датами",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Фрейм для вводу дат
        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        # Перша дата
        tk.Label(input_frame, text="Перша дата (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.date1_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date1_entry.grid(row=0, column=1, pady=5, padx=10)
        self.date1_entry.insert(0, "2024-01-01")

        # Друга дата
        tk.Label(input_frame, text="Друга дата (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.date2_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date2_entry.grid(row=1, column=1, pady=5, padx=10)
        self.date2_entry.insert(0, "2024-12-31")

        # Кнопка обчислення
        calc_btn = tk.Button(input_frame, text="Обчислити різницю",
                             command=self.calculate_difference,
                             bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        calc_btn.grid(row=2, column=0, columnspan=2, pady=15)

        # Результат
        self.diff_result = tk.Text(
            frame, height=10, width=70, font=("Arial", 10))
        self.diff_result.pack(pady=10)

    def create_day_of_week_tab(self):
        """Вкладка визначення дня тижня"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="День тижня")

        title = tk.Label(frame, text="Визначення дня тижня",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Дата (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.dow_date_entry = tk.Entry(
            input_frame, width=15, font=("Arial", 10))
        self.dow_date_entry.grid(row=0, column=1, pady=5, padx=10)
        self.dow_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        calc_btn = tk.Button(input_frame, text="Визначити день тижня",
                             command=self.calculate_day_of_week,
                             bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        calc_btn.grid(row=1, column=0, columnspan=2, pady=15)

        self.dow_result = tk.Text(
            frame, height=8, width=70, font=("Arial", 10))
        self.dow_result.pack(pady=10)

    def create_date_operations_tab(self):
        """Вкладка операцій з датами"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Операції з датами")

        title = tk.Label(frame, text="Додавання/віднімання днів",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Початкова дата (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.ops_date_entry = tk.Entry(
            input_frame, width=15, font=("Arial", 10))
        self.ops_date_entry.grid(row=0, column=1, pady=5, padx=10)
        self.ops_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(input_frame, text="Кількість днів (+ або -):",
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.days_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.days_entry.grid(row=1, column=1, pady=5, padx=10)
        self.days_entry.insert(0, "30")

        calc_btn = tk.Button(input_frame, text="Обчислити нову дату",
                             command=self.calculate_date_operations,
                             bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        calc_btn.grid(row=2, column=0, columnspan=2, pady=15)

        self.ops_result = tk.Text(
            frame, height=8, width=70, font=("Arial", 10))
        self.ops_result.pack(pady=10)

    def create_age_calculator_tab(self):
        """Вкладка калькулятора віку"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Калькулятор віку")

        title = tk.Label(frame, text="Обчислення віку",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Дата народження (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.birth_date_entry = tk.Entry(
            input_frame, width=15, font=("Arial", 10))
        self.birth_date_entry.grid(row=0, column=1, pady=5, padx=10)
        self.birth_date_entry.insert(0, "1990-01-01")

        calc_btn = tk.Button(input_frame, text="Обчислити вік",
                             command=self.calculate_age,
                             bg="#9C27B0", fg="white", font=("Arial", 10, "bold"))
        calc_btn.grid(row=1, column=0, columnspan=2, pady=15)

        self.age_result = tk.Text(
            frame, height=8, width=70, font=("Arial", 10))
        self.age_result.pack(pady=10)

    def create_calendar_tab(self):
        """Вкладка календаря"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Календар")

        title = tk.Label(frame, text="Календар місяця",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Рік:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=5)
        self.year_entry = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.year_entry.grid(row=0, column=1, pady=5, padx=10)
        self.year_entry.insert(0, str(datetime.now().year))

        tk.Label(input_frame, text="Місяць (1-12):", font=("Arial", 10)
                 ).grid(row=0, column=2, sticky="w", pady=5)
        self.month_entry = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.month_entry.grid(row=0, column=3, pady=5, padx=10)
        self.month_entry.insert(0, str(datetime.now().month))

        calc_btn = tk.Button(input_frame, text="Показати календар",
                             command=self.show_calendar,
                             bg="#607D8B", fg="white", font=("Arial", 10, "bold"))
        calc_btn.grid(row=1, column=0, columnspan=4, pady=15)

        self.calendar_result = tk.Text(
            frame, height=12, width=70, font=("Courier", 10))
        self.calendar_result.pack(pady=10)

    def create_working_days_tab(self):
        """Вкладка робочих днів"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Робочі дні")

        title = tk.Label(frame, text="Обчислення робочих днів",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        input_frame = tk.Frame(frame)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Початкова дата (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.work_start_entry = tk.Entry(
            input_frame, width=15, font=("Arial", 10))
        self.work_start_entry.grid(row=0, column=1, pady=5, padx=10)
        self.work_start_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(input_frame, text="Кінцева дата (РРРР-ММ-ДД):",
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.work_end_entry = tk.Entry(
            input_frame, width=15, font=("Arial", 10))
        self.work_end_entry.grid(row=1, column=1, pady=5, padx=10)
        end_date = datetime.now() + timedelta(days=30)
        self.work_end_entry.insert(0, end_date.strftime("%Y-%m-%d"))

        calc_btn = tk.Button(input_frame, text="Обчислити робочі дні",
                             command=self.calculate_working_days,
                             bg="#795548", fg="white", font=("Arial", 10, "bold"))
        calc_btn.grid(row=2, column=0, columnspan=2, pady=15)

        self.work_result = tk.Text(
            frame, height=8, width=70, font=("Arial", 10))
        self.work_result.pack(pady=10)

    def create_history_tab(self):
        """Вкладка історії обчислень"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Історія")

        title = tk.Label(frame, text="Історія обчислень",
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)

        refresh_btn = tk.Button(frame, text="Оновити історію",
                                command=self.load_history,
                                bg="#3F51B5", fg="white", font=("Arial", 10, "bold"))
        refresh_btn.pack(pady=10)

        self.history_text = tk.Text(
            frame, height=20, width=80, font=("Arial", 9))
        self.history_text.pack(pady=10, fill=tk.BOTH, expand=True)

        # Завантаження історії при створенні
        self.load_history()

    def calculate_difference(self):
        """Обчислення різниці між датами"""
        try:
            date1 = self.date1_entry.get().strip()
            date2 = self.date2_entry.get().strip()

            result = self.calculator.calculate_date_difference(date1, date2)

            output = f"Різниця між датами {date1} та {date2}:\n\n"
            output += f"Загальна кількість днів: {result['total_days']}\n"
            output += f"Років: {result['years']}\n"
            output += f"Місяців: {result['months']}\n"
            output += f"Днів: {result['days']}\n"
            output += f"Тижнів: {result['weeks']}\n\n"

            if result['total_days'] > 365:
                output += f"Це приблизно {result['total_days']/365:.1f} років\n"

            self.diff_result.delete(1.0, tk.END)
            self.diff_result.insert(1.0, output)

            # Збереження в історію
            self.save_calculation("Різниця дат", f"{date1} - {date2}",
                                  f"{result['total_days']} днів")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def calculate_day_of_week(self):
        """Визначення дня тижня"""
        try:
            date = self.dow_date_entry.get().strip()
            result = self.calculator.get_day_of_week(date)

            output = f"Інформація про дату {date}:\n\n"
            output += f"День тижня: {result['day_name']}\n"
            output += f"Номер дня тижня: {result['day_number']}\n"
            output += f"Вихідний день: {'Так' if result['is_weekend'] else 'Ні'}\n\n"

            # Додаткова інформація
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            output += f"Форматована дата: {date_obj.strftime('%d.%m.%Y')}\n"
            output += f"Високосний рік: {'Так' if self.calculator.is_leap_year(date_obj.year) else 'Ні'}\n"

            self.dow_result.delete(1.0, tk.END)
            self.dow_result.insert(1.0, output)

            self.save_calculation("День тижня", date, result['day_name'])

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def calculate_date_operations(self):
        """Операції з датами"""
        try:
            date = self.ops_date_entry.get().strip()
            days = int(self.days_entry.get().strip())

            result = self.calculator.add_days_to_date(date, days)

            operation = "додавання" if days >= 0 else "віднімання"
            output = f"Результат {operation} {abs(days)} днів до дати {date}:\n\n"
            output += f"Нова дата: {result['new_date']}\n"
            output += f"Форматована дата: {result['formatted_date']}\n"
            output += f"День тижня: {result['day_of_week']}\n"

            self.ops_result.delete(1.0, tk.END)
            self.ops_result.insert(1.0, output)

            self.save_calculation("Операції з датами", f"{date} + {days} днів",
                                  result['new_date'])

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def calculate_age(self):
        """Обчислення віку"""
        try:
            birth_date = self.birth_date_entry.get().strip()
            result = self.calculator.get_age(birth_date)

            output = f"Інформація про вік (дата народження: {birth_date}):\n\n"
            output += f"Повних років: {result['age_years']}\n"
            output += f"Днів до наступного дня народження: {result['days_to_birthday']}\n"
            output += f"Загальна кількість прожитих днів: {result['total_days_lived']}\n\n"

            # Додаткові розрахунки
            hours_lived = result['total_days_lived'] * 24
            minutes_lived = hours_lived * 60

            output += f"Прожито годин: {hours_lived:,}\n"
            output += f"Прожито хвилин: {minutes_lived:,}\n"

            self.age_result.delete(1.0, tk.END)
            self.age_result.insert(1.0, output)

            self.save_calculation(
                "Вік", birth_date, f"{result['age_years']} років")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def show_calendar(self):
        """Показ календаря"""
        try:
            year = int(self.year_entry.get().strip())
            month = int(self.month_entry.get().strip())

            if month < 1 or month > 12:
                raise ValueError("Місяць повинен бути від 1 до 12")

            result = self.calculator.get_calendar_month(year, month)

            months_uk = [
                "", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
                "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
            ]

            output = f"{months_uk[month]} {year}\n"
            output += "=" * 30 + "\n\n"
            output += "Пн  Вт  Ср  Чт  Пт  Сб  Нд\n"
            output += "-" * 30 + "\n"

            for week in result['calendar']:
                week_str = ""
                for day in week:
                    if day == 0:
                        week_str += "    "
                    else:
                        week_str += f"{day:2d}  "
                output += week_str + "\n"

            output += f"\nДнів у місяці: {result['days_in_month']}\n"
            output += f"Високосний рік: {'Так' if self.calculator.is_leap_year(year) else 'Ні'}\n"

            self.calendar_result.delete(1.0, tk.END)
            self.calendar_result.insert(1.0, output)

            self.save_calculation("Календар", f"{month}/{year}",
                                  f"{months_uk[month]} {year}")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def calculate_working_days(self):
        """Обчислення робочих днів"""
        try:
            start_date = self.work_start_entry.get().strip()
            end_date = self.work_end_entry.get().strip()

            result = self.calculator.get_working_days(start_date, end_date)

            output = f"Аналіз періоду з {start_date} по {end_date}:\n\n"
            output += f"Робочих днів (Пн-Пт): {result['working_days']}\n"
            output += f"Вихідних днів (Сб-Нд): {result['weekend_days']}\n"
            output += f"Загальна кількість днів: {result['total_days']}\n\n"

            # Додаткова статистика
            work_percentage = (
                result['working_days'] / result['total_days']) * 100
            output += f"Відсоток робочих днів: {work_percentage:.1f}%\n"

            if result['working_days'] > 0:
                work_hours = result['working_days'] * \
                    8  # 8-годинний робочий день
                output += f"Робочих годин (8 год/день): {work_hours}\n"

            self.work_result.delete(1.0, tk.END)
            self.work_result.insert(1.0, output)

            self.save_calculation("Робочі дні", f"{start_date} - {end_date}",
                                  f"{result['working_days']} робочих днів")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def save_calculation(self, calc_type, input_data, result):
        """Збереження обчислення в історію"""
        if self.user['id'] != 0:  # Не зберігаємо для гостя
            self.db_manager.save_calculation(
                self.user['id'], calc_type, input_data, result)

    def load_history(self):
        """Завантаження історії обчислень"""
        if self.user['id'] == 0:  # Гостьовий режим
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(1.0, "Історія недоступна в гостьовому режимі.\n"
                                          "Увійдіть в систему для збереження історії обчислень.")
            return

        calculations = self.db_manager.get_user_calculations(self.user['id'])

        self.history_text.delete(1.0, tk.END)

        if not calculations:
            self.history_text.insert(1.0, "Історія обчислень порожня.")
            return

        output = f"Історія обчислень користувача {self.user['username']}:\n"
        output += "=" * 60 + "\n\n"

        for i, (calc_type, input_data, result, timestamp) in enumerate(calculations, 1):
            output += f"{i}. {calc_type}\n"
            output += f"   Вхідні дані: {input_data}\n"
            output += f"   Результат: {result}\n"
            output += f"   Час: {timestamp}\n"
            output += "-" * 40 + "\n"

        self.history_text.insert(1.0, output)

    def run(self):
        """Запуск програми"""
        self.root.mainloop()


def main():
    """Головна функція програми"""
    print("Запуск програми роботи з датами та часом...")

    # Ініціалізація бази даних
    db_manager = DatabaseManager()

    def on_login_success(user):
        """Callback після успішної авторизації"""
        app = DateTimeApp(user, db_manager)
        app.run()

    # Запуск вікна авторизації
    login_window = LoginWindow(db_manager, on_login_success)
    user = login_window.run()

    print("Програма завершена.")


if __name__ == "__main__":
    main()
