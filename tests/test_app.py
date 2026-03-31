import pytest
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, username='testuser', email='test@example.com', password='password123'):
    return client.post('/auth/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password,
    }, follow_redirects=True)


def login(client, login_input='testuser', password='password123'):
    return client.post('/auth/login', data={
        'login': login_input,
        'password': password,
    }, follow_redirects=True)


class TestAuth:
    def test_register(self, client):
        rv = register(client)
        assert rv.status_code == 200
        assert 'Регистрация прошла успешно' in rv.data.decode()

    def test_register_duplicate_username(self, client):
        register(client)
        client.get('/auth/logout', follow_redirects=True)
        rv = register(client)
        assert 'уже занято' in rv.data.decode()

    def test_register_duplicate_email(self, client):
        register(client)
        client.get('/auth/logout', follow_redirects=True)
        rv = register(client, username='other')
        assert 'уже зарегистрирован' in rv.data.decode()

    def test_login(self, client):
        register(client)
        rv = login(client)
        assert rv.status_code == 200
        assert 'testuser' in rv.data.decode() or 'Добро пожаловать' in rv.data.decode()

    def test_login_wrong_password(self, client):
        register(client)
        client.get('/auth/logout', follow_redirects=True)
        rv = login(client, password='wrongpassword')
        assert 'Неверные данные' in rv.data.decode()

    def test_logout(self, client):
        register(client)
        rv = client.get('/auth/logout', follow_redirects=True)
        assert rv.status_code == 200


class TestSettings:
    def test_settings_requires_auth(self, client):
        rv = client.get('/profile/settings', follow_redirects=True)
        assert rv.status_code == 200
        assert 'Войти' in rv.data.decode() or 'login' in rv.request.path

    def test_settings_page_accessible(self, client):
        register(client)
        login(client)
        rv = client.get('/profile/settings')
        assert rv.status_code == 200
        assert 'Настройки профиля' in rv.data.decode()

    def test_update_profile(self, client, app):
        register(client)
        login(client)
        rv = client.post('/profile/settings/profile', data={
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'bio': 'Тестовая биография',
            'phone': '+7 999 000-00-00',
            'birth_date': '1990-01-15',
            'profile_public': 'on',
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Профиль обновлён' in rv.data.decode()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.first_name == 'Иван'
            assert user.last_name == 'Иванов'

    def test_update_account(self, client, app):
        register(client)
        login(client)
        rv = client.post('/profile/settings/account', data={
            'username': 'newusername',
            'email': 'newemail@example.com',
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Данные аккаунта обновлены' in rv.data.decode()
        with app.app_context():
            user = User.query.filter_by(username='newusername').first()
            assert user is not None
            assert user.email == 'newemail@example.com'

    def test_change_password(self, client):
        register(client)
        login(client)
        rv = client.post('/profile/settings/password', data={
            'current_password': 'password123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Пароль успешно изменён' in rv.data.decode()

    def test_change_password_wrong_current(self, client):
        register(client)
        login(client)
        rv = client.post('/profile/settings/password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456',
        }, follow_redirects=True)
        assert 'Текущий пароль введён неверно' in rv.data.decode()

    def test_change_password_mismatch(self, client):
        register(client)
        login(client)
        rv = client.post('/profile/settings/password', data={
            'current_password': 'password123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentpassword',
        }, follow_redirects=True)
        assert 'не совпадают' in rv.data.decode()

    def test_update_notifications(self, client, app):
        register(client)
        login(client)
        rv = client.post('/profile/settings/notifications', data={},
                         follow_redirects=True)
        assert rv.status_code == 200
        assert 'Настройки уведомлений сохранены' in rv.data.decode()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.email_notifications is False

    def test_delete_account(self, client, app):
        register(client)
        login(client)
        rv = client.post('/profile/settings/delete', data={
            'password': 'password123',
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Аккаунт удалён' in rv.data.decode()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is None

    def test_delete_account_wrong_password(self, client, app):
        register(client)
        login(client)
        rv = client.post('/profile/settings/delete', data={
            'password': 'wrongpassword',
        }, follow_redirects=True)
        assert 'Аккаунт не удалён' in rv.data.decode()
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
