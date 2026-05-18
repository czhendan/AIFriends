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

from web.models.group_chat import GroupChat, GroupMember, GroupMessage
from web.models.user import UserProfile
from web.views.group.message.chat.graph import GroupChatGraph


class SSERenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


def add_context_messages(inputs, group_id, mentioned_ids):
    msgs = inputs['messages']

    prompt, char_map = GroupChatGraph.build_speaker_prompt(
        group_id, mentioned_ids, round_num=0
    )
    msgs = [SystemMessage(prompt)] + msgs

    char_summary_parts = []
    for cid, info in char_map.items():
        char_summary_parts.append(f"{info['name']}(ID:{cid}): {info['profile'][:100]}")
    if char_summary_parts:
        msgs = [SystemMessage('群内角色：\n' + '\n'.join(char_summary_parts))] + msgs

    messages_raw = list(
        GroupMessage.objects.filter(group_id=group_id)
        .select_related('sender_user', 'sender_character')
        .order_by('-id')[:10]
    )
    messages_raw.reverse()
    history_msgs = []
    for m in messages_raw:
        if m.sender_type == 'user':
            name = m.sender_user.user.username
            text = f"[用户 {name}]: {m.content}"
            history_msgs.append(HumanMessage(text))
        else:
            name = m.sender_character.name
            text = f"[{name}]: {m.content}"
            history_msgs.append(AIMessage(text))

    return {'messages': msgs[:1] + history_msgs + msgs[-1:]}


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

        inputs = {'messages': [HumanMessage(message)]}
        inputs = add_context_messages(inputs, group_id, mentions)

        response = StreamingHttpResponse(
            self.event_stream(group, user_profile, inputs, mentions),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    def event_stream(self, group, user_profile, inputs, mentions):
        mq = Queue()
        thread = threading.Thread(
            target=self.worker, args=(group.id, inputs, mentions, mq)
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

        char_map = {}
        for gc in group.characters.select_related('character'):
            char_map[gc.character.id] = gc.character

        for char_id, content in full_outputs.items():
            if content.strip():
                GroupMessage.objects.create(
                    group=group,
                    sender_type='character',
                    sender_character=char_map.get(char_id),
                    content=content[:2000],
                    mentions=[],
                )

        msg_count = GroupMessage.objects.filter(group=group).count()
        if msg_count % 20 == 0:
            from web.views.group.message.chat.memory.update import update_group_memory
            update_group_memory(group)

    def worker(self, group_id, inputs, mentions, mq):
        try:
            asyncio.run(self.run_chat_rounds(group_id, inputs, mentions, mq))
        finally:
            mq.put_nowait(None)

    async def run_chat_rounds(self, group_id, inputs, mentions, mq):
        MAX_ROUNDS = 2
        current_inputs = inputs

        for round_num in range(MAX_ROUNDS):
            speaker_picker = GroupChatGraph.create_speaker_picker()
            prompt, char_map = GroupChatGraph.build_speaker_prompt(
                group_id, mentions if round_num == 0 else [], round_num
            )

            pick_inputs = {
                'messages': [SystemMessage(prompt)] + current_inputs['messages']
            }
            result = speaker_picker.invoke(pick_inputs)
            speakers = result.get('speakers', [])

            if not speakers:
                break

            speakers = speakers[:3]

            mq.put_nowait({'event': 'round_start', 'round': round_num + 1})

            tasks = []
            for char_id in speakers:
                tasks.append(
                    self.generate_character_response(
                        char_id, char_map, group_id, current_inputs, mq
                    )
                )
            await asyncio.gather(*tasks)

            mq.put_nowait({'event': 'round_complete', 'round': round_num + 1})

    async def generate_character_response(self, char_id, char_map, group_id, inputs, mq):
        llm = GroupChatGraph._build_llm(streaming=True)
        system_prompt = GroupChatGraph.build_character_prompt(char_id, char_map, group_id)

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
