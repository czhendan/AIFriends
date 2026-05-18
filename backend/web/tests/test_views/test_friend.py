class TestGetOrCreateFriend:
    URL = "/api/friend/get_or_create/"

    def test_requires_auth(self, db, api_client):
        resp = api_client.post(self.URL, {"character_id": 1})
        assert resp.status_code == 401

    def test_get_or_create_new(self, db, auth_client, test_character):
        resp = auth_client.post(self.URL, {"character_id": test_character.id})
        assert resp.json()["result"] == "success"
        fid = resp.json()["friend"]["id"]
        assert fid > 0

    def test_get_existing(self, db, auth_client, test_character, test_friend):
        resp = auth_client.post(self.URL, {"character_id": test_character.id})
        assert resp.json()["result"] == "success"
        assert resp.json()["friend"]["id"] == test_friend.id


class TestGetListFriend:
    URL = "/api/friend/get_list/"

    def test_requires_auth(self, db, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401

    def test_returns_friend_list(self, db, auth_client, test_friend):
        resp = auth_client.get(self.URL, {"items_count": 0})
        assert resp.json()["result"] == "success"
        assert "friends" in resp.json()


class TestRemoveFriend:
    URL = "/api/friend/remove/"

    def test_requires_auth(self, db, api_client, test_friend):
        resp = api_client.post(self.URL, {"friend_id": test_friend.id})
        assert resp.status_code == 401

    def test_remove_success(self, db, auth_client, test_friend):
        resp = auth_client.post(self.URL, {"friend_id": test_friend.id})
        assert resp.json()["result"] == "success"
