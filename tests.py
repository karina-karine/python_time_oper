"""
Модуль тестування програми роботи з датами та часом
"""

from main import DateTimeCalculator, DatabaseManager
import unittest
from datetime import datetime, timedelta
import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestDateTimeCalculator(unittest.TestCase):
    """Тести для класу DateTimeCalculator"""

    def setUp(self):
        """Підготовка до тестів"""
        self.calculator = DateTimeCalculator()

    def test_calculate_date_difference(self):
        """Тест обчислення різниці між датами"""
        # Тест з рядковими датами
        result = self.calculator.calculate_date_difference(
            "2024-01-01", "2024-12-31")
        self.assertEqual(result['total_days'], 365)  # 2024 - високосний рік

        # Тест з об'єктами datetime
        date1 = datetime(2024, 1, 1)
        date2 = datetime(2024, 1, 31)
        result = self.calculator.calculate_date_difference(date1, date2)
        self.assertEqual(result['total_days'], 30)

        # Тест з однаковими датами
        result = self.calculator.calculate_date_difference(
            "2024-01-01", "2024-01-01")
        self.assertEqual(result['total_days'], 0)

    def test_get_day_of_week(self):
        """Тест визначення дня тижня"""
        # Тест з відомою датою (1 січня 2024 - понеділок)
        result = self.calculator.get_day_of_week("2024-01-01")
        self.assertEqual(result['day_name'], "Понеділок")
        self.assertEqual(result['day_number'], 1)
        self.assertFalse(result['is_weekend'])

        # Тест з вихідним днем (6 січня 2024 - субота)
        result = self.calculator.get_day_of_week("2024-01-06")
        self.assertEqual(result['day_name'], "Субота")
        self.assertTrue(result['is_weekend'])

    def test_add_days_to_date(self):
        """Тест додавання днів до дати"""
        # Додавання позитивної кількості днів
        result = self.calculator.add_days_to_date("2024-01-01", 30)
        self.assertEqual(result['new_date'], "2024-01-31")

        # Додавання негативної кількості днів (віднімання)
        result = self.calculator.add_days_to_date("2024-01-31", -30)
        self.assertEqual(result['new_date'], "2024-01-01")

        # Додавання нуля днів
        result = self.calculator.add_days_to_date("2024-01-15", 0)
        self.assertEqual(result['new_date'], "2024-01-15")

    def test_get_age(self):
        """Тест обчислення віку"""
        # Тест з датою народження 30 років тому
        birth_date = datetime.now() - timedelta(days=365*30)
        birth_date_str = birth_date.strftime("%Y-%m-%d")

        result = self.calculator.get_age(birth_date_str)
        # Вік може бути 29 або 30 залежно від точної дати
        self.assertIn(result['age_years'], [29, 30])
        self.assertGreaterEqual(result['total_days_lived'], 365*29)

    def test_is_leap_year(self):
        """Тест перевірки високосного року"""
        # Високосні роки
        self.assertTrue(self.calculator.is_leap_year(2024))
        self.assertTrue(self.calculator.is_leap_year(2000))

        # Не високосні роки
        self.assertFalse(self.calculator.is_leap_year(2023))
        self.assertFalse(self.calculator.is_leap_year(1900))

    def test_get_working_days(self):
        """Тест обчислення робочих днів"""
        # Тест з тижнем (понеділок-неділя)
        result = self.calculator.get_working_days(
            "2024-01-01", "2024-01-07")  # Пн-Нд
        self.assertEqual(result['working_days'], 5)  # Пн-Пт
        self.assertEqual(result['weekend_days'], 2)  # Сб-Нд
        self.assertEqual(result['total_days'], 7)

        # Тест з одним днем
        result = self.calculator.get_working_days(
            "2024-01-01", "2024-01-01")  # Понеділок
        self.assertEqual(result['working_days'], 1)
        self.assertEqual(result['weekend_days'], 0)
        self.assertEqual(result['total_days'], 1)

    def test_get_calendar_month(self):
        """Тест створення календаря місяця"""
        result = self.calculator.get_calendar_month(2024, 1)  # Січень 2024

        self.assertEqual(result['year'], 2024)
        self.assertEqual(result['days_in_month'], 31)
        self.assertIsInstance(result['calendar'], list)
        self.assertTrue(len(result['calendar']) >= 4)  # Мінімум 4 тижні

    def test_invalid_date_format(self):
        """Тест з невірним форматом дати"""
        with self.assertRaises(ValueError):
            self.calculator.calculate_date_difference(
                "invalid-date", "2024-01-01")

        with self.assertRaises(ValueError):
            self.calculator.get_day_of_week("2024-13-01")  # Невірний місяць


class TestDatabaseManager(unittest.TestCase):
    """Тести для класу DatabaseManager"""

    def setUp(self):
        """Підготовка до тестів"""
        self.db_manager = DatabaseManager()
        # Використовуємо файлову базу даних для тестів
        self.db_manager.connection = None

    def test_file_register_and_login(self):
        """Тест реєстрації та авторизації через файли"""
        # Очищення тестових файлів
        test_files = ["users.json", "calculations_999.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

        # Тест реєстрації
        result = self.db_manager.file_register_user(
            "test_user", "test_password", "test@example.com")
        self.assertTrue(result)

        # Тест повторної реєстрації з тим же ім'ям
        result = self.db_manager.file_register_user(
            "test_user", "another_password", "test2@example.com")
        self.assertFalse(result)

        # Тест авторизації з правильними даними
        user = self.db_manager.file_login_user("test_user", "test_password")
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "test_user")

        # Тест авторизації з неправильними даними
        user = self.db_manager.file_login_user("test_user", "wrong_password")
        self.assertIsNone(user)

        # Очищення після тестів
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_file_calculations(self):
        """Тест збереження та отримання обчислень через файли"""
        user_id = 999
        calc_file = f"calculations_{user_id}.json"

        # Очищення тестового файлу
        if os.path.exists(calc_file):
            os.remove(calc_file)

        # Збереження обчислень
        self.db_manager.file_save_calculation(
            user_id, "test_type", "test_input", "test_result")
        self.db_manager.file_save_calculation(
            user_id, "test_type2", "test_input2", "test_result2")

        # Отримання обчислень
        calculations = self.db_manager.file_get_calculations(user_id)
        self.assertEqual(len(calculations), 2)

        # Перевірка порядку (останні спочатку)
        self.assertEqual(calculations[0][0], "test_type2")
        self.assertEqual(calculations[1][0], "test_type")

        # Очищення після тестів
        if os.path.exists(calc_file):
            os.remove(calc_file)


class TestIntegration(unittest.TestCase):
    """Інтеграційні тести"""

    def setUp(self):
        """Підготовка до тестів"""
        self.calculator = DateTimeCalculator()
        self.db_manager = DatabaseManager()
        self.db_manager.connection = None

    def test_full_workflow(self):
        """Тест повного робочого процесу"""
        # Очищення тестових файлів
        test_files = ["users.json", "calculations_1.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

        # Реєстрація користувача
        self.assertTrue(self.db_manager.file_register_user(
            "integration_user", "password123"))

        # Авторизація
        user = self.db_manager.file_login_user(
            "integration_user", "password123")
        self.assertIsNotNone(user)

        # Виконання обчислень
        diff_result = self.calculator.calculate_date_difference(
            "2024-01-01", "2024-12-31")
        self.assertEqual(diff_result['total_days'], 365)

        # Збереження результату
        self.db_manager.file_save_calculation(
            user['id'],
            "Різниця дат",
            "2024-01-01 - 2024-12-31",
            f"{diff_result['total_days']} днів"
        )

        # Перевірка збереження
        calculations = self.db_manager.file_get_calculations(user['id'])
        self.assertEqual(len(calculations), 1)
        self.assertEqual(calculations[0][0], "Різниця дат")

        # Очищення після тестів
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)


def run_tests():
    """Запуск всіх тестів"""
    print("Запуск тестів програми роботи з датами та часом...")
    print("=" * 60)

    # Створення test suite
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # Додавання тестів
    test_suite.addTests(loader.loadTestsFromTestCase(TestDateTimeCalculator))
    test_suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    test_suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Запуск тестів
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Виведення результатів
    print("\n" + "=" * 60)
    print(f"Тестів запущено: {result.testsRun}")
    print(f"Помилок: {len(result.errors)}")
    print(f"Невдач: {len(result.failures)}")

    if result.errors:
        print("\nПомилки:")
        for test, error in result.errors:
            print(f"- {test}: {error}")

    if result.failures:
        print("\nНевдачі:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")

    success_rate = ((result.testsRun - len(result.errors) -
                    len(result.failures)) / result.testsRun) * 100
    print(f"\nУспішність: {success_rate:.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
