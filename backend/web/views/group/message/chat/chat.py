import asyncio
import json
import threading
from queue import Queue

from django.http import StreamingHttpResponse
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from web.models.group_chat import GroupChat, GroupMember, GroupMessage, GroupCharacter, GroupMemory
from web.models.user import UserProfile
from web.views.group.message.chat.graph import GroupChatGraph


class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


def build_char_map(group_id):
    group_characters = GroupCharacter.objects.filter(
        group_id=group_id
    ).select_related('character')

    char_map = {}
    for gc in group_characters:
        c = gc.character
        char_map[c.id] = {
            'id': c.id,
            'name': c.name,
            'profile': c.profile,
        }
    return char_map


def get_group_memory(group_id):
    try:
        gm = GroupMemory.objects.get(group_id=group_id)
        return gm.memory or ''
    except GroupMemory.DoesNotExist:
        return ''


def add_context_messages(inputs, char_map, group_memory):
    msgs = inputs['messages']

    char_summary_parts = []
    for cid, info in char_map.items():
        char_summary_parts.append(f"{info['name']}(ID:{cid}): {info['profile'][:100]}")
    if char_summary_parts:
        msgs = [SystemMessage('群内角色：\n' + '\n'.join(char_summary_parts))] + msgs

    if group_memory:
        msgs = [SystemMessage(f"【群聊记忆】\n{group_memory}")] + msgs

    return {'messages': msgs}


class GroupChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer]

    def post(self, request, *args, **kwargs):
        group_id = request.data.get('group_id')
        message = request.data.get('message', '').strip()
        mentions = request.data.get('mentions', [])

        if not message:
            return Response({'result': '消息不能为空'})

        groups = GroupChat.objects.filter(pk=group_id)
        if not groups.exists():
            return Response({'result': '群不存在'})

        group = groups.first()
        user_profile = UserProfile.objects.get(user=request.user)
        is_member = GroupMember.objects.filter(group=group, user=user_profile).exists()
        if not is_member:
            return Response({'result': '你不在该群中'})

        GroupMessage.objects.create(
            group=group,
            sender_type='user',
            sender_user=user_profile,
            content=message[:2000],
            mentions=mentions,
        )

        # 同步查询所有需要的数据
        char_map = build_char_map(group.id)
        group_memory = get_group_memory(group.id)

        # 注入历史消息
        inputs = {'messages': [HumanMessage(message)]}
        inputs = add_context_messages(inputs, char_map, group_memory)

        messages_raw = list(
            GroupMessage.objects.filter(group_id=group_id)
            .select_related('sender_user', 'sender_character')
            .order_by('-id')[:10]
        )
        messages_raw.reverse()
        history_msgs = []
        for m in messages_raw:
            if m.sender_type == 'user':
                history_msgs.append(HumanMessage(
                    content=m.content,
                    name=m.sender_user.user.username
                ))
            else:
                history_msgs.append(AIMessage(
                    content=m.content,
                    name=m.sender_character.name
                ))

        inputs = {'messages': inputs['messages'][:1] + history_msgs + inputs['messages'][-1:]}

        response = StreamingHttpResponse(
            self.event_stream(group, char_map, group_memory, inputs, mentions),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    def event_stream(self, group, char_map, group_memory, inputs, mentions):
        mq = Queue()
        thread = threading.Thread(
            target=self.worker, args=(char_map, group_memory, inputs, mentions, mq, group.id)
        )
        thread.start()

        full_outputs = {}
        while True:
            msg = mq.get()
            if not msg:
                break

            if msg.get('content'):
                speaker = msg['speaker']
                sid = speaker['id']
                if sid not in full_outputs:
                    full_outputs[sid] = ''
                full_outputs[sid] += msg['content']
                yield f"data: {json.dumps({'speaker': speaker, 'content': msg['content']}, ensure_ascii=False)}\n\n"

            if msg.get('done'):
                speaker = msg['speaker']
                yield f"data: {json.dumps({'speaker': speaker, 'done': True}, ensure_ascii=False)}\n\n"

            if msg.get('event'):
                yield f"data: {json.dumps({'event': msg['event'], 'round': msg.get('round', 0)}, ensure_ascii=False)}\n\n"

        yield 'data: [DONE]\n\n'

        for char_id, content in full_outputs.items():
            if content.strip():
                GroupMessage.objects.create(
                    group=group,
                    sender_type='character',
                    sender_character_id=char_id,
                    content=content[:2000],
                    mentions=[],
                )

        msg_count = GroupMessage.objects.filter(group=group).count()
        if msg_count % 20 == 0:
            from web.views.group.message.chat.memory.update import update_group_memory
            update_group_memory(group)

    def worker(self, char_map, group_memory, inputs, mentions, mq, group_id):
        try:
            asyncio.run(self.run_chat_rounds(char_map, group_memory, inputs, mentions, mq))
        finally:
            mq.put_nowait(None)

    async def run_chat_rounds(self, char_map, group_memory, inputs, mentions, mq):
        MAX_ROUNDS = 2
        current_inputs = inputs

        for round_num in range(MAX_ROUNDS):
            speaker_picker = GroupChatGraph.create_speaker_picker()
            prompt = GroupChatGraph.build_speaker_prompt(
                char_map, mentions if round_num == 0 else [], round_num
            )

            pick_inputs = {
                'messages': [SystemMessage(prompt)] + current_inputs['messages']
            }
            result = speaker_picker.invoke(pick_inputs)
            speakers = result.get('speakers', [])

            # 强制添加被 @ 的角色（仅第 0 轮）
            if round_num == 0 and mentions:
                for cid in mentions:
                    if cid in char_map and cid not in speakers:
                        speakers.append(cid)

            if not speakers:
                break

            speakers = speakers[:3]

            mq.put_nowait({'event': 'round_start', 'round': round_num + 1})

            tasks = []
            for char_id in speakers:
                tasks.append(
                    self.generate_character_response(
                        char_id, char_map, group_memory, current_inputs, mq
                    )
                )
            await asyncio.gather(*tasks)

            mq.put_nowait({'event': 'round_complete', 'round': round_num + 1})

    async def generate_character_response(self, char_id, char_map, group_memory, inputs, mq):
        llm = GroupChatGraph._build_llm(streaming=True)
        system_prompt = GroupChatGraph.build_character_prompt(char_id, char_map, group_memory)

        msgs = [system_prompt] + inputs['messages']
        speaker_info = {
            'id': char_id,
            'name': char_map.get(char_id, {}).get('name', '未知'),
        }

        async for chunk in llm.astream(msgs):
            if chunk.content:
                mq.put_nowait({
                    'speaker': speaker_info,
                    'content': chunk.content,
                })

        mq.put_nowait({'speaker': speaker_info, 'done': True})
