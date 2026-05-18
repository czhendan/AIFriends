from web.models.friend import Friend, Message, SystemPrompt


def test_friend_str(db, test_friend):
    s = str(test_friend)
    assert "测试角色" in s
    assert test_friend.me.user.username in s


def test_friend_cascade_on_character_delete(db, test_friend):
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
