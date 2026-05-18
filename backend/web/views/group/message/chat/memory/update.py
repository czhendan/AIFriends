from django.utils.timezone import now
from langchain_core.messages import SystemMessage, HumanMessage

from web.models.group_chat import GroupMessage, GroupMemory
from web.views.group.message.chat.memory.graph import GroupMemoryGraph


def update_group_memory(group):
    app = GroupMemoryGraph.create_app()

    gm, _ = GroupMemory.objects.get_or_create(group=group)

    messages = list(
        GroupMessage.objects.filter(group=group).order_by('-id')[:20]
    )
    messages.reverse()

    conversation = ''
    for m in messages:
        if m.sender_type == 'user':
            conversation += f"用户 {m.sender_user.user.username}: {m.content}\n"
        else:
            conversation += f"{m.sender_character.name}: {m.content}\n"

    system_prompt = SystemMessage(
        "你是群聊的长期记忆管理员。请阅读【当前记忆】和【最新对话】，用不超过500字更新群聊记忆。"
        "重点记住：1. 群聊的主要讨论话题和进展 2. 每个角色的重要观点和态度 3. 用户的关键信息和偏好"
    )
    human_prompt = HumanMessage(
        f"【当前记忆】\n{gm.memory or '暂无'}\n\n【最新对话】\n{conversation}\n\n请输出更新后的记忆："
    )

    result = app.invoke({
        'messages': [system_prompt, human_prompt],
    })

    gm.memory = result['messages'][-1].content[:5000]
    gm.update_time = now()
    gm.save()
