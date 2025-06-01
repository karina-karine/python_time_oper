"""
Допоміжні функції та утиліти для програми
"""

import re
from datetime import datetime, timedelta
import calendar
import locale
import os
import json


class DateValidator:
    """Клас для валідації дат"""

    @staticmethod
    def is_valid_date_format(date_string):
        """Перевірка формату дати YYYY-MM-DD"""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, date_string))

    @staticmethod
    def is_valid_date(date_string):
        """Перевірка чи є дата валідною"""
        if not DateValidator.is_valid_date_format(date_string):
            return False

        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def is_future_date(date_string):
        """Перевірка чи є дата в майбутньому"""
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
            return date.date() > datetime.now().date()
        except ValueError:
            return False

    @staticmethod
    def is_past_date(date_string):
        """Перевірка чи є дата в минулому"""
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
            return date.date() < datetime.now().date()
        except ValueError:
            return False


class DateFormatter:
    """Клас для форматування дат"""

    @staticmethod
    def format_ukrainian_date(date_obj):
        """Форматування дати в українському стилі"""
        months_uk = {
            1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
            5: "травня", 6: "червня", 7: "липня", 8: "серпня",
            9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
        }

        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")

        day = date_obj.day
        month = months_uk[date_obj.month]
        year = date_obj.year

        return f"{day} {month} {year} року"

    @staticmethod
    def format_relative_date(date_obj):
        """Форматування відносної дати (вчора, сьогодні, завтра)"""
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")

        today = datetime.now().date()
        target_date = date_obj.date()

        diff = (target_date - today).days

        if diff == 0:
            return "сьогодні"
        elif diff == 1:
            return "завтра"
        elif diff == -1:
            return "вчора"
        elif diff > 1:
            return f"через {diff} днів"
        else:
            return f"{abs(diff)} днів тому"

    @staticmethod
    def format_duration(days):
        """Форматування тривалості в зручному вигляді"""
        if days == 0:
            return "0 днів"

        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        days_left = remaining_days % 30

        parts = []

        if years > 0:
            if years == 1:
                parts.append("1 рік")
            elif years < 5:
                parts.append(f"{years} роки")
            else:
                parts.append(f"{years} років")

        if months > 0:
            if months == 1:
                parts.append("1 місяць")
            elif months < 5:
                parts.append(f"{months} місяці")
            else:
                parts.append(f"{months} місяців")

        if days_left > 0:
            if days_left == 1:
                parts.append("1 день")
            elif days_left < 5:
                parts.append(f"{days_left} дні")
            else:
                parts.append(f"{days_left} днів")

        return " ".join(parts)


class ConfigManager:
    """Менеджер конфігурації програми"""

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Завантаження конфігурації з файлу"""
        default_config = {
            "database": {
                "host": "localhost",
                "database": "datetime_app",
                "user": "root",
                "password": ""
            },
            "ui": {
                "theme": "default",
                "font_size": 10,
                "window_width": 800,
                "window_height": 600
            },
            "locale": {
                "language": "uk_UA",
                "date_format": "%Y-%m-%d"
            }
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Об'єднання з дефолтною конфігурацією
                    self._merge_configs(default_config, loaded_config)
                    return default_config
            except Exception as e:
                print(f"Помилка завантаження конфігурації: {e}")

        return default_config

    def save_config(self):
        """Збереження конфігурації у файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка збереження конфігурації: {e}")

    def _merge_configs(self, default, loaded):
        """Рекурсивне об'єднання конфігурацій"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_configs(default[key], value)
                else:
                    default[key] = value

    def get(self, path, default=None):
        """Отримання значення конфігурації за шляхом (наприклад, 'database.host')"""
        keys = path.split('.')
        current = self.config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def set(self, path, value):
        """Встановлення значення конфігурації за шляхом"""
        keys = path.split('.')
        current = self.config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value


class Logger:
    """Простий логер для програми"""

    def __init__(self, log_file="datetime_app.log"):
        self.log_file = log_file

    def log(self, level, message):
        """Запис повідомлення в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Помилка запису в лог: {e}")

    def info(self, message):
        """Інформаційне повідомлення"""
        self.log("INFO", message)
        print(f"INFO: {message}")

    def error(self, message):
        """Повідомлення про помилку"""
        self.log("ERROR", message)
        print(f"ERROR: {message}")

    def warning(self, message):
        """Попереджувальне повідомлення"""
        self.log("WARNING", message)
        print(f"WARNING: {message}")


class HolidayCalculator:
    """Калькулятор свят та вихідних днів"""

    def __init__(self):
        # Фіксовані свята України
        self.fixed_holidays = {
            (1, 1): "Новий рік",
            (1, 7): "Різдво Христове",
            (3, 8): "Міжнародний жіночий день",
            (5, 1): "День праці",
            (5, 9): "День перемоги",
            (6, 28): "День Конституції України",
            (8, 24): "День незалежності України",
            (10, 14): "День захисника України",
            (12, 25): "Католицьке Різдво"
        }

    def is_holiday(self, date):
        """Перевірка чи є дата святом"""
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")

        # Перевірка фіксованих свят
        if (date.month, date.day) in self.fixed_holidays:
            return True, self.fixed_holidays[(date.month, date.day)]

        # Перевірка Великодня (спрощена логіка)
        easter_date = self.calculate_easter(date.year)
        if date.date() == easter_date:
            return True, "Великдень"

        return False, None

    def calculate_easter(self, year):
        """Обчислення дати Великодня (православного)"""
        # Спрощений алгоритм для православного Великодня
        a = year % 19
        b = year % 4
        c = year % 7
        d = (19 * a + 15) % 30
        e = (2 * b + 4 * c + 6 * d + 6) % 7

        if d + e < 10:
            day = d + e + 22
            month = 3
        else:
            day = d + e - 9
            month = 4

        # Корекція для григоріанського календаря
        easter = datetime(year, month, day)
        # Різниця між юліанським та григоріанським календарями
        easter += timedelta(days=13)

        return easter.date()

    def get_holidays_in_year(self, year):
        """Отримання всіх свят у році"""
        holidays = []

        # Додавання фіксованих свят
        for (month, day), name in self.fixed_holidays.items():
            holidays.append((datetime(year, month, day).date(), name))

        # Додавання Великодня
        easter_date = self.calculate_easter(year)
        holidays.append((easter_date, "Великдень"))

        # Сортування за датою
        holidays.sort(key=lambda x: x[0])

        return holidays


class StatisticsCalculator:
    """Калькулятор статистики використання програми"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_user_statistics(self, user_id):
        """Отримання статистики користувача"""
        calculations = self.db_manager.get_user_calculations(user_id)

        if not calculations:
            return {
                "total_calculations": 0,
                "most_used_function": "Немає даних",
                "calculation_types": {}
            }

        # Підрахунок типів обчислень
        calc_types = {}
        for calc in calculations:
            calc_type = calc[0]
            calc_types[calc_type] = calc_types.get(calc_type, 0) + 1

        # Найбільш використовувана функція
        most_used = max(calc_types.items(),
                        key=lambda x: x[1]) if calc_types else ("Немає", 0)

        return {
            "total_calculations": len(calculations),
            "most_used_function": most_used[0],
            "calculation_types": calc_types,
            "last_calculation": calculations[0][3] if calculations else "Немає"
        }


def create_sample_data():
    """Створення зразкових даних для демонстрації"""
    sample_dates = [
        ("2024-01-01", "2024-12-31", "Повний рік 2024"),
        ("2024-02-14", "2024-02-14", "День Святого Валентина"),
        ("2024-03-08", "2024-03-08", "Міжнародний жіночий день"),
        ("2024-05-01", "2024-05-01", "День праці"),
        ("2024-08-24", "2024-08-24", "День незалежності України")
    ]

    return sample_dates


def export_calculations_to_csv(calculations, filename="calculations_export.csv"):
    """Експорт обчислень у CSV файл"""
    try:
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['Тип обчислення', 'Вхідні дані', 'Результат', 'Дата'])

            for calc in calculations:
                writer.writerow(calc)

        return True
    except Exception as e:
        print(f"Помилка експорту: {e}")
        return False


def import_calculations_from_csv(filename="calculations_import.csv"):
    """Імпорт обчислень з CSV файлу"""
    try:
        import csv
        calculations = []

        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропускаємо заголовок

            for row in reader:
                if len(row) >= 4:
                    calculations.append(tuple(row))

        return calculations
    except Exception as e:
        print(f"Помилка імпорту: {e}")
        return []


if __name__ == "__main__":
    # Тестування утиліт
    print("Тестування допоміжних функцій...")

    # Тест валідатора дат
    validator = DateValidator()
    print(
        f"Валідна дата '2024-01-01': {validator.is_valid_date('2024-01-01')}")
    print(
        f"Невалідна дата '2024-13-01': {validator.is_valid_date('2024-13-01')}")

    # Тест форматувальника
    formatter = DateFormatter()
    test_date = datetime(2024, 3, 8)
    print(
        f"Українське форматування: {formatter.format_ukrainian_date(test_date)}")
    print(
        f"Відносне форматування: {formatter.format_relative_date(test_date)}")
    print(f"Тривалість 365 днів: {formatter.format_duration(365)}")

    # Тест калькулятора свят
    holiday_calc = HolidayCalculator()
    is_holiday, holiday_name = holiday_calc.is_holiday("2024-01-01")
    print(f"1 січня 2024 - свято: {is_holiday}, назва: {holiday_name}")

    print("Тестування завершено.")
