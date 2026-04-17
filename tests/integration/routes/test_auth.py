from typing import Any

from httpx import AsyncClient

from src.models.user import User
from tests.factories import USER_PASSWORD


class TestRegister:
    URL: str = '/v1/auth/signup'

    def _get_register_data(self, **kwargs) -> dict[str, Any]:
        return {
            'username': kwargs.get('username', 'johndoe'),
            'email': kwargs.get('email', 'johndoe@example.com'),
            'full_name': kwargs.get('full_name', 'John Doe'),
            'password': kwargs.get('password', USER_PASSWORD),
        }

    async def test_success(self, client: AsyncClient):
        user_data = self._get_register_data()
        response = await client.post(self.URL, json=user_data)

        data = response.json()

        assert response.status_code == 201
        assert data['username'] == user_data['username']
        assert data['email'] == user_data['email']
        assert data['full_name'] == user_data['full_name']
        assert 'hashed_password' not in data
        assert 'password' not in data

    async def test_duplicate_username(self, client: AsyncClient, user: User):
        user_data = self._get_register_data(username=user.username)
        response = await client.post(self.URL, json=user_data)

        assert response.status_code == 400

    async def test_duplicate_email(self, client: AsyncClient, user: User):
        user_data = self._get_register_data(email=user.email)
        response = await client.post(self.URL, json=user_data)

        assert response.status_code == 400


class TestLogin:
    URL: str = '/v1/auth/token'

    def _get_login_data(self, **kwargs) -> dict[str, Any]:
        return {
            'username': kwargs.get('username', 'johndoe'),
            'password': kwargs.get('password', USER_PASSWORD),
        }

    async def test_success(self, client: AsyncClient, user: User):
        login_data = self._get_login_data(username=user.username)
        response = await client.post(self.URL, data=login_data)

        data = response.json()

        assert response.status_code == 200
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['type'] == 'bearer'

    async def test_user_not_found(self, client: AsyncClient):
        response = await client.post(self.URL, data=self._get_login_data(username='some_username'))
        assert response.status_code == 401

    async def test_wrong_password(self, client: AsyncClient, user: User):
        login_data = self._get_login_data(username=user.username, password='somepassword')
        response = await client.post(self.URL, data=login_data)

        assert response.status_code == 401


class TestRefresh:
    REFRESH_URL: str = '/v1/auth/refresh'
    LOGIN_URL: str = '/v1/auth/token'

    def _get_login_data(self, **kwargs) -> dict[str, Any]:
        return {
            'username': kwargs.get('username', 'johndoe'),
            'password': kwargs.get('password', USER_PASSWORD),
        }

    async def test_success(self, client: AsyncClient, user: User, auth_headers):
        login_data = self._get_login_data(username=user.username)
        login_response = await client.post(self.LOGIN_URL, data=login_data)

        refresh_token = login_response.json()['refresh_token']

        response = await client.post(
            self.REFRESH_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )

        data = response.json()

        assert response.status_code == 200
        assert 'refresh_token' in data
        assert 'access_token' in data
        assert data['refresh_token'] != refresh_token

    async def test_invalid_token(self, client: AsyncClient, auth_headers):
        response = await client.post(
            self.REFRESH_URL, json={'refresh_token': 'invalid_token'}, headers=auth_headers
        )

        assert response.status_code == 401

    async def test_reuse_revoked_token(self, client: AsyncClient, user: User, auth_headers):
        login_data = self._get_login_data(username=user.username)
        login_response = await client.post(self.LOGIN_URL, data=login_data)

        refresh_token = login_response.json()['refresh_token']

        await client.post(
            self.REFRESH_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )
        response = await client.post(
            self.REFRESH_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )

        assert response.status_code == 401


class TestLogout:
    LOGOUT_URL: str = '/v1/auth/logout'
    LOGOUT_ALL_URL: str = '/v1/auth/logout-all'
    LOGIN_URL: str = '/v1/auth/token'

    async def test_success(self, client: AsyncClient, user: User, auth_headers):
        login_data = {
            'username': user.username,
            'password': USER_PASSWORD
        }
        login_response = await client.post(self.LOGIN_URL, data=login_data)

        refresh_token = login_response.json()['refresh_token']

        response = await client.post(
            self.LOGOUT_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )

        assert response.status_code == 204

    async def test_invalid_token(self, client: AsyncClient, auth_headers):
        response = await client.post(
            self.LOGOUT_URL, json={'refresh_token': 'invalid_token'}, headers=auth_headers
        )
        assert response.status_code == 401

    async def test_reuse_revoked_token(self, client: AsyncClient, user: User, auth_headers):
        login_data = {
            'username': user.username,
            'password': USER_PASSWORD
        }
        login_response = await client.post(self.LOGIN_URL, data=login_data)

        refresh_token = login_response.json()['refresh_token']

        await client.post(
            self.LOGOUT_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )
        await client.post(
            self.LOGOUT_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )

        response = await client.post(
            self.LOGOUT_URL, json={'refresh_token': refresh_token}, headers=auth_headers
        )

        assert response.status_code == 401

    async def test_logout_all(self, client: AsyncClient, auth_headers):
        response = await client.post(self.LOGOUT_ALL_URL, headers=auth_headers)
        assert response.status_code == 204


class TestChangePassword:
    URL: str = '/v1/auth/change-password'

    def _get_update_data(self, **kwargs) -> dict[str, str]:
        return {
            'password': kwargs.get('password', USER_PASSWORD),
            'new_password': kwargs.get('new_password', 'updated_password123'),
        }

    async def test_success(self, user: User, client: AsyncClient, auth_headers):
        update_data = self._get_update_data()
        old_hash = user.hashed_password

        response = await client.post(
            self.URL, json=update_data, headers=auth_headers
        )

        assert response.status_code == 204
        assert old_hash != user.hashed_password

    async def test_wrong_password(self, client: AsyncClient, auth_headers):
        update_data = self._get_update_data(password='somepassword')

        response = await client.post(
            self.URL, json=update_data, headers=auth_headers
        )

        assert response.status_code == 401

    async def test_same_password(self, client: AsyncClient, auth_headers):
        update_data = self._get_update_data(new_password=USER_PASSWORD)

        response = await client.post(
            self.URL, json=update_data, headers=auth_headers
        )

        assert response.status_code == 400
