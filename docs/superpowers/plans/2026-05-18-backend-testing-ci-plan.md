# Backend Automated Testing & CI/CD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete backend test suite (models, API views, utility functions) with pytest-django and wire it into a GitHub Actions CI pipeline with coverage reporting.

**Architecture:** pytest-django with SQLite in-memory database, DRF test client with force_authenticate, coverage via pytest-cov, CI via GitHub Actions on ubuntu-latest with artifact upload. Tests organized as `web/tests/test_models/`, `test_views/`, `test_utils/`.

**Tech Stack:** pytest, pytest-django, pytest-cov, Django 6.0, Django REST Framework 3.17, GitHub Actions

---

### Task 1: Add test dependencies to requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add test dependencies**

```bash
echo "" >> requirements.txt
echo "# test & coverage" >> requirements.txt
echo "pytest==8.4.2" >> requirements.txt
echo "pytest-django==4.11.1" >> requirements.txt
echo "pytest-cov==6.3.0" >> requirements.txt
```

- [ ] **Step 2: Install dependencies**

```bash
cd backend
pip install pytest pytest-django pytest-cov
```

Expected: packages install without error.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add pytest, pytest-django, pytest-cov test dependencies"
```

---

### Task 2: Create pytest.ini configuration

**Files:**
- Create: `backend/pytest.ini`

- [ ] **Step 1: Write pytest.ini**

Create `backend/pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.settings
python_files = test_*.py
addopts = --tb=short --strict-markers -v

; SQLite in-memory override handled in conftest.py
```

- [ ] **Step 2: Verify pytest loads the config**

```bash
cd backend && python -m pytest --collect-only
```

Expected: pytest discovers the project (0 tests initially).

- [ ] **Step 3: Commit**

```bash
git add backend/pytest.ini
git commit -m "chore: add pytest.ini with Django settings module"
```

---

### Task 3: Create test directory structure and conftest fixtures

**Files:**
- Create: `backend/web/tests/__init__.py`
- Create: `backend/web/tests/conftest.py`
- Create: `backend/web/tests/test_models/__init__.py`
- Create: `backend/web/tests/test_views/__init__.py`
- Create: `backend/web/tests/test_utils/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p backend/web/tests/test_models backend/web/tests/test_views backend/web/tests/test_utils
touch backend/web/tests/__init__.py
touch backend/web/tests/test_models/__init__.py
touch backend/web/tests/test_views/__init__.py
touch backend/web/tests/test_utils/__init__.py
```

- [ ] **Step 2: Write conftest.py with fixtures**

Create `backend/web/tests/conftest.py`:

```python
import os
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

import pytest


@pytest.fixture(autouse=True)
def use_sqlite_memory(settings):
    """Override DATABASES to use SQLite in-memory for all tests."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create a test user with UserProfile, return (user, profile)."""
    from web.models.user import UserProfile

    user = User.objects.create_user(username="testuser", password="testpass123")
    profile = UserProfile.objects.get(user=user)
    return user, profile


@pytest.fixture
def auth_client(db, test_user):
    """Authenticated DRF API client with JWT bypass via force_authenticate."""
    client = APIClient()
    client.force_authenticate(user=test_user[0])
    return client


@pytest.fixture
def test_voice(db):
    """Create a Voice instance for test character creation."""
    from web.models.character import Voice

    return Voice.objects.create(name="测试音色", voice_id="default_voice_id")


def _make_test_image(name="test.png"):
    """Create a minimal valid PNG as SimpleUploadedFile."""
    img = Image.new("RGB", (100, 100), color="red")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


@pytest.fixture
def test_image():
    return _make_test_image()


@pytest.fixture
def test_character(db, test_user, test_voice, test_image):
    """Create a test character owned by test_user."""
    from web.models.character import Character

    img2 = _make_test_image("bg.png")
    return Character.objects.create(
        author=test_user[1],
        name="测试角色",
        voice=test_voice,
        profile="这是一个测试角色的简介",
        photo=test_image,
        background_image=img2,
    )


@pytest.fixture
def test_friend(db, test_user, test_character):
    """Create a test friend relationship."""
    from web.models.friend import Friend

    return Friend.objects.create(me=test_user[1], character=test_character)


@pytest.fixture
def test_message(db, test_friend):
    """Create a test message in the friend chat."""
    from web.models.friend import Message

    return Message.objects.create(
        friend=test_friend,
        user_message="你好",
        input='[{"type":"human","content":"你好"}]',
        output="你好！有什么可以帮助你的吗？",
        input_tokens=50,
        output_tokens=30,
        total_tokens=80,
    )
```

- [ ] **Step 3: Verify fixtures load correctly**

```bash
cd backend && python -m pytest --collect-only
```

Expected: 0 tests collected (no test files yet), but fixtures file loads without error.

- [ ] **Step 4: Commit**

```bash
git add backend/web/tests/
git commit -m "chore: create test directory structure and conftest fixtures"
```

---

### Task 4: Test RRF fusion (pure utility, no DB)

**Files:**
- Create: `backend/web/tests/test_utils/test_rrf.py`

- [ ] **Step 1: Write RRF test file**

Create `backend/web/tests/test_utils/test_rrf.py`:

```python
from web.documents.utils.hybrid_search import rrf_fusion


def test_rrf_single_list():
    """RRF with a single list preserves the ranking order."""
    ranked = [("a", 0.9), ("b", 0.7), ("c", 0.5)]
    result = rrf_fusion([ranked], k=60)
    assert [doc_id for doc_id, _ in result] == ["a", "b", "c"]


def test_rrf_two_lists():
    """RRF with two overlapping lists fuses scores correctly."""
    list1 = [("a", 0.9), ("b", 0.7)]
    list2 = [("b", 0.8), ("a", 0.3), ("c", 0.1)]
    result = rrf_fusion([list1, list2], k=60)
    ids = [doc_id for doc_id, _ in result]
    # b appears high in both, should rank at or near top
    assert ids[0] == "b"
    assert set(ids) == {"a", "b", "c"}


def test_rrf_empty_list():
    """RRF with an empty list is handled gracefully."""
    result = rrf_fusion([], k=60)
    assert result == []


def test_rrf_some_empty_sublists():
    """RRF with some empty sublists still works for non-empty ones."""
    result = rrf_fusion([[], [("x", 1.0)], []], k=60)
    assert result == [("x", 1 / (60 + 1))]


def test_rrf_score_values():
    """RRF scores are computed as sum of 1/(k + rank), rank 1-indexed."""
    ranked = [("doc1", 0.99), ("doc2", 0.5)]
    result = rrf_fusion([ranked], k=60)
    expected_doc1 = 1.0 / (60 + 1)
    expected_doc2 = 1.0 / (60 + 2)
    assert result[0] == ("doc1", expected_doc1)
    assert result[1] == ("doc2", expected_doc2)


def test_rrf_different_k():
    """RRF with k=10 gives different scores than k=60."""
    ranked = [("a", 0.9)]
    result = rrf_fusion([ranked], k=10)
    assert result[0][1] == 1.0 / (10 + 1)
```

- [ ] **Step 2: Run RRF tests**

```bash
cd backend && python -m pytest web/tests/test_utils/test_rrf.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_utils/test_rrf.py
git commit -m "test: add RRF fusion unit tests"
```

---

### Task 5: Test BM25 search (utility, graceful skip)

**Files:**
- Create: `backend/web/tests/test_utils/test_bm25.py`

- [ ] **Step 1: Write BM25 test file**

Create `backend/web/tests/test_utils/test_bm25.py`:

```python
import os
import tempfile

import pytest
from web.documents.utils.bm25_search import BM25Searcher


def test_bm25_searcher_creates_index_on_new_path():
    """BM25Searcher creates a new index when path is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        searcher = BM25Searcher(tmpdir)
        assert searcher.count() == 0


def test_bm25_add_and_search():
    """Add documents and retrieve them via BM25 search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        searcher = BM25Searcher(tmpdir)
        searcher.add_documents([
            {"chunk_id": "chunk_0", "content": "Python是一种编程语言"},
            {"chunk_id": "chunk_1", "content": "Java也是一种编程语言"},
            {"chunk_id": "chunk_2", "content": "今天天气真好"},
        ])
        assert searcher.count() == 3

        results = searcher.search("Python编程", k=2)
        assert len(results) >= 1
        assert results[0][0] == "chunk_0"


def test_bm25_search_with_content():
    """search_with_content returns (chunk_id, content) tuples."""
    with tempfile.TemporaryDirectory() as tmpdir:
        searcher = BM25Searcher(tmpdir)
        searcher.add_documents([
            {"chunk_id": "c1", "content": "机器学习是人工智能的一个分支"},
        ])
        results = searcher.search_with_content("机器学习", k=5)
        assert len(results) == 1
        chunk_id, content = results[0]
        assert chunk_id == "c1"
        assert "机器学习" in content


def test_bm25_empty_query_returns_empty():
    """An empty or unparseable query returns an empty list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        searcher = BM25Searcher(tmpdir)
        searcher.add_documents([
            {"chunk_id": "c1", "content": "测试内容"},
        ])
        results = searcher.search("", k=5)
        assert results == []


def test_bm25_segment_chinese():
    """The _segment method tokenizes Chinese text with jieba."""
    tokens = BM25Searcher._segment("你好世界")
    assert " " in tokens
    assert len(tokens) >= 2
```

- [ ] **Step 2: Run BM25 tests**

```bash
cd backend && python -m pytest web/tests/test_utils/test_bm25.py -v
```

Expected: 5 passed.

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_utils/test_bm25.py
git commit -m "test: add BM25 search unit tests"
```

---

### Task 6: Test hybrid search (utility, graceful skip)

**Files:**
- Create: `backend/web/tests/test_utils/test_hybrid_search.py`

- [ ] **Step 1: Write hybrid search test file**

Create `backend/web/tests/test_utils/test_hybrid_search.py`:

```python
import os

import pytest

from web.documents.utils.hybrid_search import (
    hybrid_search,
    vector_search_only,
    bm25_search_only,
    LANCE_URI,
    TANTIVY_PATH,
)


def _has_lancedb_data():
    return os.path.isdir(LANCE_URI)


def _has_tantivy_data():
    return os.path.isdir(TANTIVY_PATH) and os.listdir(TANTIVY_PATH)


@pytest.mark.skipif(not _has_lancedb_data(), reason="LanceDB index not found")
def test_vector_search_only_returns_tuples():
    results = vector_search_only("测试", k=3)
    assert isinstance(results, list)
    if results:
        assert len(results[0]) == 2


@pytest.mark.skipif(not _has_tantivy_data(), reason="Tantivy index not found")
def test_bm25_search_only_returns_tuples():
    results = bm25_search_only("测试", k=3)
    assert isinstance(results, list)
    if results:
        assert len(results[0]) == 2


@pytest.mark.skipif(
    not (_has_lancedb_data() and _has_tantivy_data()),
    reason="Both LanceDB and Tantivy indexes required",
)
def test_hybrid_search_returns_list_of_dicts():
    results = hybrid_search("Python编程", k_vector=5, k_bm25=5, final_k=3)
    assert isinstance(results, list)
    assert len(results) <= 3
    if results:
        assert "chunk_id" in results[0]
        assert "content" in results[0]
        assert "score" in results[0]


@pytest.mark.skipif(
    not (_has_lancedb_data() and _has_tantivy_data()),
    reason="Both LanceDB and Tantivy indexes required",
)
def test_hybrid_search_respects_final_k():
    results = hybrid_search("测试", k_vector=10, k_bm25=10, final_k=2)
    assert len(results) <= 2


def test_module_imports():
    """Verify all public functions are importable."""
    assert callable(hybrid_search)
    assert callable(vector_search_only)
    assert callable(bm25_search_only)
```

- [ ] **Step 2: Run hybrid search tests**

```bash
cd backend && python -m pytest web/tests/test_utils/test_hybrid_search.py -v
```

Expected: tests pass (some may be skipped if indexes don't exist).

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_utils/test_hybrid_search.py
git commit -m "test: add hybrid search tests with graceful skip"
```

---

### Task 7: Test models (Character, Voice, Friend, Message, SystemPrompt, UserProfile)

**Files:**
- Create: `backend/web/tests/test_models/test_character.py`
- Create: `backend/web/tests/test_models/test_friend.py`
- Create: `backend/web/tests/test_models/test_user.py`

- [ ] **Step 1: Write Character and Voice model tests**

Create `backend/web/tests/test_models/test_character.py`:

```python
import uuid

from web.models.character import Character, Voice, photo_upload_to, background_image_upload_to


def test_voice_str(db):
    v = Voice.objects.create(name="温柔", voice_id="voice_001")
    assert "温柔" in str(v)
    assert "voice_001" in str(v)


def test_character_str(db, test_character):
    assert "测试角色" in str(test_character)
    assert test_character.author.user.username in str(test_character)


def test_character_cascade_on_user_delete(db, test_user, test_character):
    """Characters are deleted when their author UserProfile is deleted."""
    cid = test_character.id
    test_user[1].delete()
    assert not Character.objects.filter(pk=cid).exists()


def test_photo_upload_to_generates_uuid_filename():
    result = photo_upload_to(None, "avatar.jpg")
    assert result.startswith("character/photos/")
    assert result.endswith(".jpg")
    hex_part = result.split("/")[-1].split(".")[0].split("_")[-1]
    assert len(hex_part) == 10


def test_background_image_upload_to_generates_uuid_filename():
    result = background_image_upload_to(None, "bg.png")
    assert result.startswith("character/background_images/")
    assert result.endswith(".png")


def test_character_fields(db, test_character):
    assert test_character.name == "测试角色"
    assert test_character.profile == "这是一个测试角色的简介"
    assert test_character.create_time is not None
    assert test_character.update_time is not None
```

- [ ] **Step 2: Write Friend, Message, SystemPrompt model tests**

Create `backend/web/tests/test_models/test_friend.py`:

```python
from web.models.friend import Friend, Message, SystemPrompt


def test_friend_str(db, test_friend):
    s = str(test_friend)
    assert "测试角色" in s
    assert test_friend.me.user.username in s


def test_friend_cascade_on_character_delete(db, test_friend):
    """Friends are deleted when their Character is deleted."""
    fid = test_friend.id
    test_friend.character.delete()
    assert not Friend.objects.filter(pk=fid).exists()


def test_message_str(db, test_message):
    s = str(test_message)
    assert "你好" in s


def test_message_fields(db, test_message):
    assert test_message.user_message == "你好"
    assert test_message.output == "你好！有什么可以帮助你的吗？"
    assert test_message.input_tokens == 50
    assert test_message.output_tokens == 30
    assert test_message.total_tokens == 80
    assert test_message.create_time is not None


def test_message_cascade_on_friend_delete(db, test_message):
    mid = test_message.id
    test_message.friend.delete()
    assert not Message.objects.filter(pk=mid).exists()


def test_friend_memory_defaults_to_empty(db, test_friend):
    assert test_friend.memory == ""


def test_system_prompt_str(db):
    sp = SystemPrompt.objects.create(
        title="回复", order_number=1, prompt="你是一个友好的AI助手"
    )
    assert "回复" in str(sp)
    assert "你是一个友好的AI助手" in str(sp)


def test_system_prompt_ordering(db):
    SystemPrompt.objects.create(title="A", order_number=2, prompt="prompt A")
    SystemPrompt.objects.create(title="B", order_number=1, prompt="prompt B")
    items = list(SystemPrompt.objects.order_by("order_number"))
    assert items[0].title == "B"
    assert items[1].title == "A"
```

- [ ] **Step 3: Write UserProfile model test**

Create `backend/web/tests/test_models/test_user.py`:

```python
from django.contrib.auth.models import User
from web.models.user import UserProfile


def test_user_profile_auto_created(db):
    """UserProfile is created together with User (via signal or create logic)."""
    user = User.objects.create_user(username="newuser", password="pass123")
    assert UserProfile.objects.filter(user=user).exists()


def test_user_profile_str(db, test_user):
    user, profile = test_user
    assert user.username in str(profile)


def test_user_profile_defaults(db):
    user = User.objects.create_user(username="defaults", password="pass123")
    profile = UserProfile.objects.get(user=user)
    assert profile.profile == "谢谢你的关注"
    assert "default.png" in profile.photo.name


def test_user_profile_cascade_on_user_delete(db, test_user):
    user, _ = test_user
    uid = user.id
    user.delete()
    assert not UserProfile.objects.filter(user_id=uid).exists()
```

- [ ] **Step 4: Run all model tests**

```bash
cd backend && python -m pytest web/tests/test_models/ -v
```

Expected: ~13 tests passed.

- [ ] **Step 5: Commit**

```bash
git add backend/web/tests/test_models/
git commit -m "test: add model unit tests for Character, Voice, Friend, Message, SystemPrompt, UserProfile"
```

---

### Task 8: Test auth views (register, login, logout, refresh token)

**Files:**
- Create: `backend/web/tests/test_views/test_auth.py`

- [ ] **Step 1: Write auth view tests**

Create `backend/web/tests/test_views/test_auth.py`:

```python
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
```

- [ ] **Step 2: Run auth tests**

```bash
cd backend && python -m pytest web/tests/test_views/test_auth.py -v
```

Expected: 8 passed.

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_views/test_auth.py
git commit -m "test: add auth view tests (register, login, logout)"
```

---

### Task 9: Test character views (create, list, get single, update, delete)

**Files:**
- Create: `backend/web/tests/test_views/test_character.py`

- [ ] **Step 1: Write character view tests**

Create `backend/web/tests/test_views/test_character.py`:

```python
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


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

    def test_returns_character(self, db, api_client, test_character):
        resp = api_client.get(self.URL, {"character_id": test_character.id})
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
```

- [ ] **Step 2: Run character view tests**

```bash
cd backend && python -m pytest web/tests/test_views/test_character.py -v
```

Expected: 8 passed.

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_views/test_character.py
git commit -m "test: add character view CRUD tests"
```

---

### Task 10: Test friend views (get or create, list, remove)

**Files:**
- Create: `backend/web/tests/test_views/test_friend.py`

- [ ] **Step 1: Write friend view tests**

Create `backend/web/tests/test_views/test_friend.py`:

```python
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
```

- [ ] **Step 2: Run friend view tests**

```bash
cd backend && python -m pytest web/tests/test_views/test_friend.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_views/test_friend.py
git commit -m "test: add friend view tests"
```

---

### Task 11: Test chat and message views (SSE chat, history, ASR)

**Files:**
- Create: `backend/web/tests/test_views/test_chat.py`

- [ ] **Step 1: Write chat view tests**

Create `backend/web/tests/test_views/test_chat.py`:

```python
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
        assert resp.json()["result"] == "消息不能位空"

    def test_invalid_friend_id_rejected(self, db, auth_client):
        resp = auth_client.post(self.URL, {
            "friend_id": 99999,
            "message": "你好",
        }, format="json")
        assert resp.json()["result"] == "好友不存在"


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
```

- [ ] **Step 2: Run chat view tests**

```bash
cd backend && python -m pytest web/tests/test_views/test_chat.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add backend/web/tests/test_views/test_chat.py
git commit -m "test: add chat and message view tests"
```

---

### Task 12: Create GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Write workflow file**

Create `.github/workflows/test.yml`:

```yaml
name: Backend Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          cd backend
          python -m pytest --cov=web --cov-report=xml --cov-report=html --cov-report=term

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: backend/htmlcov/
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions backend test workflow with coverage"
```

---

### Task 13: Full suite verification

- [ ] **Step 1: Run the complete test suite locally**

```bash
cd backend && python -m pytest -v --cov=web --cov-report=term
```

Expected: All ~40+ tests pass. Coverage output shows at least partial coverage of `web/` modules.

- [ ] **Step 2: Verify the workflow YAML syntax**

```bash
git add -A && git commit --dry-run
```

No YAML syntax errors in test.yml.

- [ ] **Step 3: Push to GitHub (if ready)**

The user pushes manually. Verify on GitHub Actions tab that the workflow runs successfully.

- [ ] **Step 4: Commit any final adjustments**

```bash
git add -A && git commit -m "chore: finalize test suite and CI workflow"
```
