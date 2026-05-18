from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


def _make_image(name="test.png"):
    img = Image.new("RGB", (100, 100), color="blue")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


class TestCreateCharacter:
    URL = "/api/create/character/create/"

    def test_requires_auth(self, db, api_client):
        resp = api_client.post(self.URL)
        assert resp.status_code == 401

    def test_missing_name(self, db, auth_client):
        resp = auth_client.post(self.URL, {"name": "", "profile": "简介", "voice_id": 1})
        assert resp.json()["result"] == "角色名不能为空"

    def test_missing_profile(self, db, auth_client):
        resp = auth_client.post(self.URL, {"name": "角色A", "profile": "", "voice_id": 1})
        assert resp.json()["result"] == "角色介绍不能为空"

    def test_create_success(self, db, auth_client, test_voice):
        resp = auth_client.post(self.URL, {
            "name": "新角色",
            "voice_id": test_voice.id,
            "profile": "一个新角色的介绍",
            "photo": _make_image("photo.png"),
            "background_image": _make_image("bg.png"),
        })
        assert resp.json()["result"] == "success"


class TestGetListCharacter:
    URL = "/api/create/character/get_list/"

    def test_returns_success(self, db, api_client, test_user, test_character):
        resp = api_client.get(self.URL, {"items_count": 0, "user_id": test_user[0].id})
        assert resp.json()["result"] == "success"
        assert "characters" in resp.json()


class TestGetSingleCharacter:
    URL = "/api/create/character/get_single/"

    def test_returns_character(self, db, auth_client, test_character):
        resp = auth_client.get(self.URL, {"character_id": test_character.id})
        assert resp.json()["result"] == "success"
        assert resp.json()["character"]["name"] == "测试角色"


class TestUpdateCharacter:
    URL = "/api/create/character/update/"

    def test_requires_auth(self, db, api_client, test_character):
        resp = api_client.post(self.URL, {"character_id": test_character.id})
        assert resp.status_code == 401

    def test_update_success(self, db, auth_client, test_character, test_voice):
        resp = auth_client.post(self.URL, {
            "character_id": test_character.id,
            "name": "更新后的角色",
            "voice_id": test_voice.id,
            "profile": "更新后的简介",
        })
        assert resp.json()["result"] == "success"
        test_character.refresh_from_db()
        assert test_character.name == "更新后的角色"


class TestRemoveCharacter:
    URL = "/api/create/character/remove/"

    def test_requires_auth(self, db, api_client, test_character):
        resp = api_client.post(self.URL, {"character_id": test_character.id})
        assert resp.status_code == 401

    def test_remove_success(self, db, auth_client, test_character):
        resp = auth_client.post(self.URL, {"character_id": test_character.id})
        assert resp.json()["result"] == "success"
