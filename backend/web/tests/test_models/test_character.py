from web.models.character import Character, Voice, photo_upload_to, background_image_upload_to


def test_voice_str(db):
    v = Voice.objects.create(name="温柔", voice_id="voice_001")
    assert "温柔" in str(v)
    assert "voice_001" in str(v)


def test_character_str(db, test_character):
    assert "测试角色" in str(test_character)
    assert test_character.author.user.username in str(test_character)


def test_character_cascade_on_user_delete(db, test_user, test_character):
    cid = test_character.id
    test_user[1].delete()
    assert not Character.objects.filter(pk=cid).exists()


def test_photo_upload_to_generates_uuid_filename(test_character):
    result = photo_upload_to(test_character, "avatar.jpg")
    assert result.startswith("character/photos/")
    assert result.endswith(".jpg")
    hex_part = result.split("/")[-1].split(".")[0].split("_")[-1]
    assert len(hex_part) == 10


def test_background_image_upload_to_generates_uuid_filename(test_character):
    result = background_image_upload_to(test_character, "bg.png")
    assert result.startswith("character/background_images/")
    assert result.endswith(".png")


def test_character_fields(db, test_character):
    assert test_character.name == "测试角色"
    assert test_character.profile == "这是一个测试角色的简介"
    assert test_character.create_time is not None
    assert test_character.update_time is not None
