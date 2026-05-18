class TestMessageChat:
    URL = "/api/friend/message/chat/"

    def test_requires_auth(self, db, api_client):
        resp = api_client.post(self.URL)
        assert resp.status_code == 401

    def test_empty_message_rejected(self, db, auth_client):
        resp = auth_client.post(self.URL, {
            "friend_id": 1,
            "message": "",
        }, format="json")
        assert resp.data["result"] == "消息不能位空"

    def test_invalid_friend_id_rejected(self, db, auth_client):
        resp = auth_client.post(self.URL, {
            "friend_id": 99999,
            "message": "你好",
        }, format="json")
        assert resp.data["result"] == "好友不存在"


class TestGetHistory:
    URL = "/api/friend/message/get_history/"

    def test_requires_auth(self, db, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401

    def test_returns_messages(self, db, auth_client, test_friend, test_message):
        resp = auth_client.get(self.URL, {
            "friend_id": test_friend.id,
            "last_message_id": 0,
        })
        assert resp.json()["result"] == "success"
        assert len(resp.json()["messages"]) >= 1


class TestASR:
    URL = "/api/friend/message/asr/asr/"

    def test_requires_auth(self, db, api_client):
        resp = api_client.post(self.URL)
        assert resp.status_code == 401

    def test_missing_audio_rejected(self, db, auth_client):
        resp = auth_client.post(self.URL)
        assert resp.json()["result"] == "音频不存在"
