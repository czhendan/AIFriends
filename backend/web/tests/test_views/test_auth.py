from django.contrib.auth.models import User


class TestRegister:
    URL = "/api/user/account/register/"

    def test_register_success(self, db, api_client):
        resp = api_client.post(self.URL, {
            "username": "newuser",
            "password": "securepass123",
        }, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] == "success"
        assert data["username"] == "newuser"
        assert "access" in data
        assert User.objects.filter(username="newuser").exists()

    def test_register_duplicate_username(self, db, api_client, test_user):
        resp = api_client.post(self.URL, {
            "username": test_user[0].username,
            "password": "pass123",
        }, format="json")
        assert resp.json()["result"] == "用户名已存在"

    def test_register_missing_username(self, db, api_client):
        resp = api_client.post(self.URL, {
            "username": "",
            "password": "pass123",
        }, format="json")
        assert resp.json()["result"] == "用户名和密码不能为空"

    def test_register_missing_password(self, db, api_client):
        resp = api_client.post(self.URL, {
            "username": "someone",
            "password": "",
        }, format="json")
        assert resp.json()["result"] == "用户名和密码不能为空"


class TestLogin:
    URL = "/api/user/account/login/"

    def test_login_success(self, db, api_client, test_user):
        resp = api_client.post(self.URL, {
            "username": "testuser",
            "password": "testpass123",
        }, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] == "success"
        assert "access" in data

    def test_login_wrong_password(self, db, api_client, test_user):
        resp = api_client.post(self.URL, {
            "username": "testuser",
            "password": "wrongpassword",
        }, format="json")
        assert resp.json()["result"] == "用户名或密码错误"

    def test_login_nonexistent_user(self, db, api_client):
        resp = api_client.post(self.URL, {
            "username": "nobody",
            "password": "pass123",
        }, format="json")
        assert resp.json()["result"] == "用户名或密码错误"


class TestLogout:
    URL = "/api/user/account/logout/"

    def test_logout_requires_auth(self, db, api_client):
        resp = api_client.post(self.URL)
        assert resp.status_code == 401

    def test_logout_success(self, db, auth_client):
        resp = auth_client.post(self.URL)
        assert resp.status_code == 200
        assert resp.json()["result"] == "success"
