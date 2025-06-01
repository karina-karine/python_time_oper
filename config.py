"""
Конфігураційний файл програми
"""

# Налаштування бази даних MySQL
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'datetime_app',
    'user': 'root',
    'password': '1111',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Налаштування інтерфейсу
UI_CONFIG = {
    'window_width': 800,
    'window_height': 600,
    'login_window_width': 400,
    'login_window_height': 300,
    'font_family': 'Arial',
    'font_size': 10
}

# Кольори інтерфейсу
COLORS = {
    'primary': '#4CAF50',
    'secondary': '#2196F3',
    'warning': '#FF9800',
    'danger': '#F44336',
    'info': '#9C27B0',
    'dark': '#607D8B',
    'brown': '#795548',
    'indigo': '#3F51B5'
}

# Налаштування локалізації
LOCALE_CONFIG = {
    'language': 'uk_UA',
    'date_format': '%Y-%m-%d',
    'datetime_format': '%Y-%m-%d %H:%M:%S',
    'display_date_format': '%d.%m.%Y'
}

# Повідомлення інтерфейсу
MESSAGES = {
    'login_success': 'Успішна авторизація!',
    'login_error': 'Невірне ім\'я користувача або пароль!',
    'register_success': 'Користувач зареєстрований успішно!',
    'register_error': 'Користувач з таким ім\'ям вже існує!',
    'validation_error': 'Заповніть всі поля!',
    'password_length_error': 'Пароль повинен містити мінімум 4 символи!',
    'date_format_error': 'Невірний формат дати! Використовуйте РРРР-ММ-ДД',
    'calculation_error': 'Помилка обчислення: {error}',
    'database_error': 'Помилка бази даних: {error}'
}

# Налаштування історії
HISTORY_CONFIG = {
    'max_records': 10,
    'file_prefix': 'calculations_',
    'file_extension': '.json'
}
