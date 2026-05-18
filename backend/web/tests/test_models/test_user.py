from django.contrib.auth.models import User
from web.models.user import UserProfile


def test_user_profile_auto_created(db):
    user = User.objects.create_user(username="newuser", password="pass123")
    UserProfile.objects.create(user=user)
    assert UserProfile.objects.filter(user=user).exists()


def test_user_profile_str(db, test_user):
    user, profile = test_user
    assert user.username in str(profile)


def test_user_profile_defaults(db):
    user = User.objects.create_user(username="defaults", password="pass123")
    profile = UserProfile.objects.create(user=user)
    assert profile.profile == "谢谢你的关注"
    assert "default.png" in profile.photo.name


def test_user_profile_cascade_on_user_delete(db, test_user):
    user, _ = test_user
    uid = user.id
    user.delete()
    assert not UserProfile.objects.filter(user_id=uid).exists()
