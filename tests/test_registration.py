import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_authenticate_user_successfully(setup_database):
    """Пользователь с правильным паролем проходит аутентификацию."""
    add_user('authuser', 'authuser@example.com', 'secure-password')

    assert authenticate_user('authuser', 'secure-password') is True


def test_authenticate_nonexistent_user(setup_database):
    """Несуществующий пользователь не проходит аутентификацию."""
    assert authenticate_user('missing-user', 'any-password') is False


def test_authenticate_user_with_wrong_password(setup_database):
    """Неправильный пароль не проходит аутентификацию."""
    add_user('wrongpassuser', 'wrongpassuser@example.com', 'correct-password')

    assert authenticate_user('wrongpassuser', 'incorrect-password') is False


def test_display_users(setup_database, capsys):
    """Отображение списка включает добавленного пользователя."""
    add_user('displayuser', 'displayuser@example.com', 'password123')

    result = display_users()
    output = capsys.readouterr().out + str(result)

    assert 'displayuser' in output
    assert 'displayuser@example.com' in output