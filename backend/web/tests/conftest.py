from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

import pytest


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Override DATABASES to use SQLite in-memory before Django DB setup."""
    from django.conf import settings

    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
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
    profile = UserProfile.objects.create(user=user)
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
