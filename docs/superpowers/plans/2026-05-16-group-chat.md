# 群聊功能 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 1v1 AI 好友聊天基础上新增多用户+多角色的群聊功能。

**Architecture:** 在现有 `web` app 内新增独立文件（不修改已有文件），包括数据模型、REST API、基于 LangGraph 的多角色对话引擎（发言选择器 + 并行生成 + 收敛控制）和群记忆系统。`web/urls.py` 仅追加一条 include 路由。

**Tech Stack:** Django 6.0 + DRF + LangChain + LangGraph + OpenAI-compatible LLM + SSE + Vue 3 + fetchEventSource

---

### Task 1: 数据模型

**Files:**
- Create: `backend/web/models/group_chat.py`

- [ ] **Step 1: 创建 Model 文件**

```python
from django.db import models
from django.utils.timezone import localtime, now

from web.models.character import Character
from web.models.user import UserProfile


class GroupChat(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, default='', blank=True)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.name} - {self.owner.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('owner', '群主'),
        ('admin', '管理员'),
        ('member', '成员'),
    ]
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    join_time = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.group.name} - {self.user.user.username} - {self.role}"


class GroupCharacter(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='characters')
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    added_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    add_time = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('group', 'character')

    def __str__(self):
        return f"{self.group.name} - {self.character.name}"


class GroupMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ('user', '用户'),
        ('character', '角色'),
    ]
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    sender_character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(max_length=2000)
    mentions = models.JSONField(default=list, blank=True)
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        sender = self.sender_character.name if self.sender_type == 'character' else self.sender_user.user.username
        return f"{self.group.name} - {sender} - {self.content[:50]} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"


class GroupMemory(models.Model):
    group = models.OneToOneField(GroupChat, on_delete=models.CASCADE, related_name='memory')
    memory = models.TextField(max_length=5000, default='', blank=True)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.group.name} - memory - {localtime(self.update_time).strftime('%Y-%m-%d %H:%M:%S')}"
```

- [ ] **Step 2: 生成 migration**

Run: `cd backend && python manage.py makemigrations`
Expected: 生成 `web/migrations/0010_group_chat.py`

- [ ] **Step 3: 执行 migration**

Run: `cd backend && python manage.py migrate`
Expected: `Applying web.0010_group_chat... OK`

- [ ] **Step 4: Commit**

```bash
git add backend/web/models/group_chat.py backend/web/migrations/0010_group_chat.py
git commit -m "feat: 添加群聊数据模型 GroupChat/GroupMember/GroupCharacter/GroupMessage/GroupMemory"
```

---

### Task 2: 群聊 CRUD 视图

**Files:**
- Create: `backend/web/views/group/__init__.py` (空文件)
- Create: `backend/web/views/group/create.py`
- Create: `backend/web/views/group/get_list.py`
- Create: `backend/web/views/group/get_single.py`

- [ ] **Step 1: 创建目录和 __init__.py**

```bash
mkdir -p backend/web/views/group/member
mkdir -p backend/web/views/group/character
mkdir -p backend/web/views/group/message/chat/memory
touch backend/web/views/group/__init__.py
touch backend/web/views/group/member/__init__.py
touch backend/web/views/group/character/__init__.py
touch backend/web/views/group/message/__init__.py
touch backend/web/views/group/message/chat/__init__.py
touch backend/web/views/group/message/chat/memory/__init__.py
```

- [ ] **Step 2: 创建群 / 修改群 / 删除群 (`create.py`)**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember, GroupMemory
from web.models.user import UserProfile


class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            name = request.data.get('name', '').strip()
            description = request.data.get('description', '').strip()[:500]

            if not name:
                return Response({'result': '群名不能为空'})

            user_profile = UserProfile.objects.get(user=request.user)
            group = GroupChat.objects.create(
                owner=user_profile,
                name=name,
                description=description,
            )
            GroupMember.objects.create(
                group=group,
                user=user_profile,
                role='owner',
            )
            GroupMemory.objects.create(group=group)

            return Response({
                'result': 'success',
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                }
            })
        except:
            return Response({'result': '系统异常，请稍后重试'})


class UpdateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            groups = GroupChat.objects.filter(pk=group_id, owner__user=request.user)
            if not groups.exists():
                return Response({'result': '群不存在或无权操作'})

            group = groups.first()
            name = request.data.get('name', '').strip()
            description = request.data.get('description', '').strip()[:500]

            if name:
                group.name = name
            if description:
                group.description = description
            group.save()

            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})


class RemoveGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            groups = GroupChat.objects.filter(pk=group_id, owner__user=request.user)
            if not groups.exists():
                return Response({'result': '群不存在或无权操作'})

            groups.first().delete()
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 3: 我的群列表 (`get_list.py`)**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember
from web.models.user import UserProfile


class GetListGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            member_relations = GroupMember.objects.filter(
                user=user_profile
            ).select_related('group').order_by('-group__update_time')

            items_count = int(request.data.get('items_count', 0))
            page = member_relations[items_count:items_count + 20]

            groups = []
            for m in page:
                g = m.group
                member_count = GroupMember.objects.filter(group=g).count()
                character_count = g.characters.count()
                groups.append({
                    'id': g.id,
                    'name': g.name,
                    'description': g.description,
                    'member_count': member_count,
                    'character_count': character_count,
                    'role': m.role,
                    'create_time': g.create_time.isoformat(),
                })

            return Response({
                'result': 'success',
                'groups': groups,
            })
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 4: 单个群详情 (`get_single.py`)**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember


class GetSingleGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            groups = GroupChat.objects.filter(pk=group_id)
            if not groups.exists():
                return Response({'result': '群不存在'})

            group = groups.first()

            # 检查是否在群里
            is_member = GroupMember.objects.filter(
                group=group, user__user=request.user
            ).exists()
            if not is_member:
                return Response({'result': '你不在该群中'})

            members = []
            for m in GroupMember.objects.filter(group=group).select_related('user', 'user__user'):
                members.append({
                    'user_id': m.user.user_id,
                    'username': m.user.user.username,
                    'photo': m.user.photo.url,
                    'role': m.role,
                })

            characters = []
            for gc in group.characters.select_related('character'):
                c = gc.character
                characters.append({
                    'id': c.id,
                    'name': c.name,
                    'photo': c.photo.url,
                    'profile': c.profile,
                })

            return Response({
                'result': 'success',
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'description': group.description,
                    'owner_id': group.owner.user_id,
                    'members': members,
                    'characters': characters,
                }
            })
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 5: Commit**

```bash
git add backend/web/views/group/
git commit -m "feat: 添加群聊 CRUD 视图（创建/修改/删除/列表/详情）"
```

---

### Task 3: 成员管理视图

**Files:**
- Create: `backend/web/views/group/member/add.py`
- Create: `backend/web/views/group/member/remove.py`

- [ ] **Step 1: 拉人进群 (`add.py`)**

```python
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember
from web.models.user import UserProfile


class AddMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            username = request.data.get('username', '').strip()

            if not username:
                return Response({'result': '用户名不能为空'})

            # 校验操作者是群主或管理员
            user_profile = UserProfile.objects.get(user=request.user)
            operator = GroupMember.objects.filter(
                group_id=group_id, user=user_profile, role__in=['owner', 'admin']
            )
            if not operator.exists():
                return Response({'result': '无权操作'})

            # 查找要添加的用户
            target_user = User.objects.filter(username=username).first()
            if not target_user:
                return Response({'result': '用户不存在'})

            target_profile = UserProfile.objects.get(user=target_user)

            # 检查是否已在群中
            if GroupMember.objects.filter(group_id=group_id, user=target_profile).exists():
                return Response({'result': '该用户已在群中'})

            GroupMember.objects.create(
                group_id=group_id,
                user=target_profile,
                role='member',
            )
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 2: 移出成员 (`remove.py`)**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember
from web.models.user import UserProfile


class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            target_user_id = request.data.get('user_id')

            if not target_user_id:
                return Response({'result': '用户ID不能为空'})

            # 校验操作者是群主或管理员
            user_profile = UserProfile.objects.get(user=request.user)
            operator = GroupMember.objects.filter(
                group_id=group_id, user=user_profile, role__in=['owner', 'admin']
            )
            if not operator.exists():
                return Response({'result': '无权操作'})

            # 不能移除群主
            group = GroupChat.objects.get(pk=group_id)
            if group.owner.user_id == target_user_id:
                return Response({'result': '不能移除群主'})

            target = GroupMember.objects.filter(group_id=group_id, user__user_id=target_user_id)
            if not target.exists():
                return Response({'result': '该成员不在群中'})

            target.delete()
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 3: Commit**

```bash
git add backend/web/views/group/member/
git commit -m "feat: 添加群成员管理视图（拉人/移出）"
```

---

### Task 4: 角色管理视图

**Files:**
- Create: `backend/web/views/group/character/add.py`
- Create: `backend/web/views/group/character/remove.py`

- [ ] **Step 1: 拉角色进群 (`add.py`)**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character
from web.models.group_chat import GroupChat, GroupMember, GroupCharacter
from web.models.user import UserProfile


class AddCharacterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            character_id = request.data.get('character_id')

            if not character_id:
                return Response({'result': '角色ID不能为空'})

            # 校验操作者是群主或管理员
            user_profile = UserProfile.objects.get(user=request.user)
            operator = GroupMember.objects.filter(
                group_id=group_id, user=user_profile, role__in=['owner', 'admin']
            )
            if not operator.exists():
                return Response({'result': '无权操作'})

            # 检查角色是否已在群中
            if GroupCharacter.objects.filter(group_id=group_id, character_id=character_id).exists():
                return Response({'result': '该角色已在群中'})

            GroupCharacter.objects.create(
                group_id=group_id,
                character_id=character_id,
                added_by=user_profile,
            )
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 2: 移出角色 (`remove.py`)**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupMember, GroupCharacter
from web.models.user import UserProfile


class RemoveCharacterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            character_id = request.data.get('character_id')

            if not character_id:
                return Response({'result': '角色ID不能为空'})

            # 校验操作者是群主或管理员
            user_profile = UserProfile.objects.get(user=request.user)
            operator = GroupMember.objects.filter(
                group_id=group_id, user=user_profile, role__in=['owner', 'admin']
            )
            if not operator.exists():
                return Response({'result': '无权操作'})

            target = GroupCharacter.objects.filter(group_id=group_id, character_id=character_id)
            if not target.exists():
                return Response({'result': '该角色不在群中'})

            target.delete()
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 3: Commit**

```bash
git add backend/web/views/group/character/
git commit -m "feat: 添加群角色管理视图（拉入/移出角色）"
```

---

### Task 5: 历史消息视图

**Files:**
- Create: `backend/web/views/group/message/history.py`

- [ ] **Step 1: 获取历史消息**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember, GroupMessage
from web.models.user import UserProfile


class GetGroupHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            groups = GroupChat.objects.filter(pk=group_id)
            if not groups.exists():
                return Response({'result': '群不存在'})

            group = groups.first()

            is_member = GroupMember.objects.filter(
                group=group, user__user=request.user
            ).exists()
            if not is_member:
                return Response({'result': '你不在该群中'})

            items_count = int(request.data.get('items_count', 0))
            messages_raw = list(
                GroupMessage.objects.filter(group=group)
                .select_related('sender_user', 'sender_character')
                .order_by('-id')[items_count:items_count + 20]
            )
            messages_raw.reverse()

            messages = []
            for m in messages_raw:
                msg = {
                    'id': m.id,
                    'sender_type': m.sender_type,
                    'content': m.content,
                    'mentions': m.mentions,
                    'create_time': m.create_time.isoformat(),
                }
                if m.sender_type == 'user':
                    msg['sender'] = {
                        'user_id': m.sender_user.user_id,
                        'username': m.sender_user.user.username,
                        'photo': m.sender_user.photo.url,
                    }
                else:
                    msg['sender'] = {
                        'id': m.sender_character.id,
                        'name': m.sender_character.name,
                        'photo': m.sender_character.photo.url,
                    }
                messages.append(msg)

            return Response({
                'result': 'success',
                'messages': messages,
            })
        except:
            return Response({'result': '系统异常，请稍后重试'})
```

- [ ] **Step 2: Commit**

```bash
git add backend/web/views/group/message/history.py
git commit -m "feat: 添加群聊历史消息视图"
```

---

### Task 6: 多角色对话引擎 Graph

**Files:**
- Create: `backend/web/views/group/message/chat/graph.py`

- [ ] **Step 1: 实现发言选择器 + 角色回复生成器**

```python
import json
import os
from typing import TypedDict, Annotated, Sequence, List

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph

from web.models.character import Character
from web.models.group_chat import GroupCharacter, GroupMemory


class GroupChatGraph:
    @staticmethod
    def _build_llm(streaming=True):
        kwargs = {
            'model': os.getenv('MODEL'),
            'openai_api_key': os.getenv('API_KEY'),
            'openai_api_base': os.getenv('API_BASE'),
            'streaming': streaming,
        }
        if streaming:
            kwargs['model_kwargs'] = {
                'stream_options': {'include_usage': True}
            }
        return ChatOpenAI(**kwargs)

    @staticmethod
    def create_speaker_picker():
        """发言选择器：根据上下文 + 所有角色人设 + 群记忆 + @信息，决定谁该说话"""
        llm = GroupChatGraph._build_llm(streaming=False)

        class SpeakerState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]
            speakers: Annotated[List[int], lambda x, y: y if y else x]

        def pick_speakers(state: SpeakerState) -> dict:
            res = llm.invoke(state['messages'])
            try:
                content = res.content.strip()
                if content.startswith('```'):
                    content = content.split('```')[1]
                    if content.startswith('json'):
                        content = content[4:]
                speakers = json.loads(content)
                if isinstance(speakers, list) and all(isinstance(s, int) for s in speakers):
                    return {'speakers': speakers, 'messages': [res]}
            except (json.JSONDecodeError, ValueError):
                pass
            return {'speakers': [], 'messages': [res]}

        graph = StateGraph(SpeakerState)
        graph.add_node('pick_speakers', pick_speakers)
        graph.add_edge(START, 'pick_speakers')
        graph.add_edge('pick_speakers', END)

        return graph.compile()

    @staticmethod
    def build_speaker_prompt(group_id: int, mentioned_character_ids: List[int], round_num: int) -> (str, dict):
        """构建发言选择器 prompt 和 character_id -> profile 的映射"""
        group_characters = GroupCharacter.objects.filter(
            group_id=group_id
        ).select_related('character')

        char_map = {}
        char_descriptions = []
        for gc in group_characters:
            c = gc.character
            char_map[c.id] = {
                'id': c.id,
                'name': c.name,
                'profile': c.profile,
            }
            char_descriptions.append(f"- ID:{c.id} | {c.name} | {c.profile[:200]}")

        char_list_text = '\n'.join(char_descriptions) if char_descriptions else '暂无角色'

        mentioned_text = ''
        if mentioned_character_ids:
            mentioned_names = []
            for cid in mentioned_character_ids:
                if cid in char_map:
                    mentioned_names.append(f"ID:{cid}({char_map[cid]['name']})")
            mentioned_text = f"以下角色被@了，本轮必须回复（已在强制列表中）：{', '.join(mentioned_names)}\n"

        round_hint = ''
        if round_num >= 1:
            round_hint = f'当前是第 {round_num + 1} 轮自动触发。尽量不要再触发新角色发言，除非非常必要。'

        prompt = f"""你是群聊调度员。根据当前对话上下文，判断哪些角色应该发言。

群内角色：
{char_list_text}

{mentioned_text}
规则：
1. 被@的角色必须出现在返回列表中
2. 如果当前话题不适合角色发言，或应该等待用户，返回空列表 []
3. 最多推荐3个角色发言
4. {round_hint}
5. 角色可以互相对话，但不要自言自语

请以 JSON 数组格式返回角色ID，例如：[3, 7] 或 []"""

        return prompt, char_map

    @staticmethod
    def build_character_prompt(character_id: int, char_map: dict, group_id: int) -> SystemMessage:
        """为特定角色构建系统 prompt"""
        char_info = char_map.get(character_id, {})
        char_name = char_info.get('name', '未知角色')
        char_profile = char_info.get('profile', '')

        # 获取群记忆
        memory_text = ''
        try:
            gm = GroupMemory.objects.get(group_id=group_id)
            if gm.memory:
                memory_text = f"\n【群聊记忆】\n{gm.memory}\n"
        except GroupMemory.DoesNotExist:
            pass

        prompt = f"""你是 {char_name}，正在参与一个群聊。

【角色性格】
{char_profile}
{memory_text}
【发言要求】
1. 在群聊中看到消息后，判断你是否应该发言
2. 如果需要发言，用自然口语化的方式回复
3. 可以提及和回应其他角色，像真正的群聊一样
4. 回复要简洁，不超过200字
5. 被 @ 时必须回复
6. 维持你的角色设定，不要违背性格"""

        return SystemMessage(prompt)
```

- [ ] **Step 2: Commit**

```bash
git add backend/web/views/group/message/chat/graph.py
git commit -m "feat: 添加群聊对话引擎（发言选择器 + 角色回复生成）"
```

---

### Task 7: SSE 群聊视图

**Files:**
- Create: `backend/web/views/group/message/chat/chat.py`

- [ ] **Step 1: 实现 SSE 流视图**

```python
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
    """注入系统提示 + 角色人设 + 群记忆 + 最近消息"""
    msgs = inputs['messages']

    prompt, char_map = GroupChatGraph.build_speaker_prompt(
        group_id, mentioned_ids, round_num=0
    )
    msgs = [SystemMessage(prompt)] + msgs

    # 注入角色人设摘要
    char_summary_parts = []
    for cid, info in char_map.items():
        char_summary_parts.append(f"{info['name']}(ID:{cid}): {info['profile'][:100]}")
    if char_summary_parts:
        msgs = [SystemMessage('群内角色：\n' + '\n'.join(char_summary_parts))] + msgs

    # 注入最近 10 条消息
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

        # 保存用户消息
        GroupMessage.objects.create(
            group=group,
            sender_type='user',
            sender_user=user_profile,
            content=message[:2000],
            mentions=mentions,
        )

        # 构建初始 inputs
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
        final_usages = []
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

            if msg.get('usage'):
                final_usages.append(msg['usage'])

            if msg.get('event'):
                yield f"data: {json.dumps({'event': msg['event'], 'round': msg.get('round', 0)}, ensure_ascii=False)}\n\n"

        yield 'data: [DONE]\n\n'

        # 保存本轮所有角色回复
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

        # 触发记忆更新
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

            # 发言选择
            pick_inputs = {
                'messages': [SystemMessage(prompt)] + current_inputs['messages']
            }
            result = speaker_picker.invoke(pick_inputs)
            speakers = result.get('speakers', [])

            if not speakers:
                break

            # 限制最多3个角色同时发言
            speakers = speakers[:3]

            mq.put_nowait({'event': 'round_start', 'round': round_num + 1})

            # 并行生成
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
        full_content = ''
        usage = {}
        speaker_info = {
            'id': char_id,
            'name': char_map.get(char_id, {}).get('name', '未知'),
        }

        async for chunk in llm.astream(msgs):
            if chunk.content:
                full_content += chunk.content
                mq.put_nowait({
                    'speaker': speaker_info,
                    'content': chunk.content,
                })
            if hasattr(chunk, 'usage_metadata') and chunk.usage_metadata:
                usage = chunk.usage_metadata

        mq.put_nowait({'speaker': speaker_info, 'done': True})
        if usage:
            mq.put_nowait({'usage': usage})
```

- [ ] **Step 2: Commit**

```bash
git add backend/web/views/group/message/chat/chat.py
git commit -m "feat: 添加群聊 SSE 流视图（发言选择 + 并行生成 + 收敛控制）"
```

---

### Task 8: 群记忆系统

**Files:**
- Create: `backend/web/views/group/message/chat/memory/graph.py`
- Create: `backend/web/views/group/message/chat/memory/update.py`

- [ ] **Step 1: 记忆 Graph (`graph.py`)**

```python
import os
from typing import Annotated, TypedDict, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


class GroupMemoryGraph:
    @staticmethod
    def create_app():
        llm = ChatOpenAI(
            model=os.getenv('MODEL'),
            openai_api_key=os.getenv('API_KEY'),
            openai_api_base=os.getenv('API_BASE'),
        )

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        def model_call(state: AgentState):
            res = llm.invoke(state['messages'])
            return {'messages': [res]}

        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)
        graph.add_edge(START, 'agent')
        graph.add_edge('agent', END)

        return graph.compile()
```

- [ ] **Step 2: 记忆更新逻辑 (`update.py`)**

```python
from django.utils.timezone import now
from langchain_core.messages import SystemMessage, HumanMessage

from web.models.group_chat import GroupMessage, GroupMemory
from web.views.group.message.chat.memory.graph import GroupMemoryGraph


def update_group_memory(group):
    app = GroupMemoryGraph.create_app()

    gm, _ = GroupMemory.objects.get_or_create(group=group)

    # 获取最近 20 条消息
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
```

- [ ] **Step 3: Commit**

```bash
git add backend/web/views/group/message/chat/memory/
git commit -m "feat: 添加群聊长期记忆系统"
```

---

### Task 9: URL 路由注册

**Files:**
- Create: `backend/web/views/group/urls.py`
- Modify: `backend/web/urls.py` (追加一行 include)

- [ ] **Step 1: 新建群聊路由文件 (`web/views/group/urls.py`)**

```python
from django.urls import path

from web.views.group.create import CreateGroupView, UpdateGroupView, RemoveGroupView
from web.views.group.get_list import GetListGroupView
from web.views.group.get_single import GetSingleGroupView
from web.views.group.member.add import AddMemberView
from web.views.group.member.remove import RemoveMemberView
from web.views.group.character.add import AddCharacterView
from web.views.group.character.remove import RemoveCharacterView
from web.views.group.message.history import GetGroupHistoryView
from web.views.group.message.chat.chat import GroupChatView

urlpatterns = [
    path('create/', CreateGroupView.as_view()),
    path('update/', UpdateGroupView.as_view()),
    path('remove/', RemoveGroupView.as_view()),
    path('get_list/', GetListGroupView.as_view()),
    path('get_single/', GetSingleGroupView.as_view()),
    path('member/add/', AddMemberView.as_view()),
    path('member/remove/', RemoveMemberView.as_view()),
    path('character/add/', AddCharacterView.as_view()),
    path('character/remove/', RemoveCharacterView.as_view()),
    path('message/chat/', GroupChatView.as_view()),
    path('message/history/', GetGroupHistoryView.as_view()),
]
```

- [ ] **Step 2: 修改 `web/urls.py`，追加一行**

在 `urlpatterns` 列表末尾追加：
```python
    path('api/group/', include('web.views.group.urls')),
```

同时确保顶部已有 import（`include` 已存在于 `django.urls` 导入中，无需改动）。

- [ ] **Step 3: 验证路由**

Run: `cd backend && python manage.py show_urls 2>/dev/null || python -c "from django.urls import get_resolver; [print(p.pattern) for p in get_resolver().url_patterns]"`

- [ ] **Step 4: Commit**

```bash
git add backend/web/views/group/urls.py backend/web/urls.py
git commit -m "feat: 注册群聊 API 路由"
```

---

### Task 10: 前端 — 群列表页

**Files:**
- Create: `frontend/src/views/group/GroupIndex.vue`
- Create: `frontend/src/views/group/components/GroupCreateModal.vue`

- [ ] **Step 1: 群列表页 (`GroupIndex.vue`)**

```vue
<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";
import GroupCreateModal from "@/views/group/components/GroupCreateModal.vue";

const groups = ref([])
const isLoading = ref(false)
const hasMore = ref(true)
const sentinelRef = useTemplateRef('sentinel-ref')
const groupCreateModalRef = useTemplateRef('group-create-modal-ref')
const router = useRouter()

function checkSentinelVisible() {
  if (!sentinelRef.value) return false
  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

async function loadMore() {
  if (isLoading.value || !hasMore.value) return
  isLoading.value = true

  let newGroups = []
  try {
    const res = await api.post('api/group/get_list/', {
      items_count: groups.value.length,
    })
    const data = res.data
    if (data.result === 'success') {
      newGroups = data.groups
    }
  } catch (err) {
    console.log(err)
  } finally {
    isLoading.value = false
    if (newGroups.length === 0) {
      hasMore.value = false
    } else {
      groups.value.push(...newGroups)
      await nextTick()
      if (checkSentinelVisible()) {
        await loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()
  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) loadMore()
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

function openChat(groupId) {
  router.push({name: 'group-chat', params: {group_id: groupId}})
}

function handleCreated(newGroup) {
  groups.value.unshift(newGroup)
}
</script>

<template>
  <div class="flex flex-col items-center">
    <div class="flex justify-between items-center w-full max-w-3xl mt-8 px-9">
      <h1 class="text-2xl font-bold">群聊</h1>
      <button class="btn btn-primary" @click="groupCreateModalRef.showModal()">创建群聊</button>
    </div>

    <div v-if="groups.length === 0 && !isLoading" class="text-gray-500 mt-16">
      暂无群聊，创建一个吧
    </div>

    <div class="w-full max-w-3xl px-9 mt-6 space-y-4">
      <div
        v-for="g in groups" :key="g.id"
        class="card bg-base-100 shadow-md cursor-pointer hover:bg-base-200 transition"
        @click="openChat(g.id)"
      >
        <div class="card-body p-6">
          <div class="flex justify-between items-center">
            <h2 class="card-title text-lg">{{ g.name }}</h2>
            <span class="text-sm text-gray-500">{{ g.member_count }}人 · {{ g.character_count }}角色</span>
          </div>
          <p v-if="g.description" class="text-sm text-gray-500 mt-1">{{ g.description }}</p>
        </div>
      </div>
    </div>

    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>

    <GroupCreateModal ref="group-create-modal-ref" @created="handleCreated" />
  </div>
</template>

<style scoped></style>
```

- [ ] **Step 2: 创建群弹窗 (`GroupCreateModal.vue`)**

```vue
<script setup>
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

const emit = defineEmits(['created'])
const modalRef = useTemplateRef('modal-ref')
const name = ref('')
const description = ref('')
const error = ref('')

async function handleSubmit() {
  error.value = ''
  if (!name.value.trim()) {
    error.value = '群名不能为空'
    return
  }
  try {
    const res = await api.post('api/group/create/', {
      name: name.value.trim(),
      description: description.value.trim(),
    })
    if (res.data.result === 'success') {
      emit('created', res.data.group)
      name.value = ''
      description.value = ''
      modalRef.value.close()
    } else {
      error.value = res.data.result
    }
  } catch (err) {
    error.value = '创建失败，请重试'
  }
}

function showModal() {
  modalRef.value.showModal()
}

defineExpose({showModal})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box">
      <h3 class="text-lg font-bold mb-4">创建群聊</h3>
      <div class="form-control">
        <label class="label"><span class="label-text">群名</span></label>
        <input v-model="name" class="input input-bordered" placeholder="输入群名" maxlength="100">
      </div>
      <div class="form-control mt-4">
        <label class="label"><span class="label-text">群简介</span></label>
        <textarea v-model="description" class="textarea textarea-bordered" placeholder="介绍一下这个群" maxlength="500"></textarea>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
      <div class="modal-action">
        <button class="btn" @click="modalRef.close()">取消</button>
        <button class="btn btn-primary" @click="handleSubmit">创建</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped></style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/group/
git commit -m "feat: 添加群聊列表页和创建群弹窗"
```

---

### Task 11: 前端 — 群聊页核心组件

**Files:**
- Create: `frontend/src/views/group/GroupChat.vue`
- Create: `frontend/src/views/group/components/GroupChatField.vue`
- Create: `frontend/src/views/group/components/GroupSpeakerBubble.vue`

- [ ] **Step 1: 群聊页 (`GroupChat.vue`)**

```vue
<script setup>
import {onMounted, ref} from "vue";
import {useRoute} from "vue-router";
import api from "@/js/http/api.js";
import GroupChatField from "@/views/group/components/GroupChatField.vue";
import GroupInputField from "@/views/group/components/GroupInputField.vue";
import GroupInfoPanel from "@/views/group/components/GroupInfoPanel.vue";

const route = useRoute()
const groupId = Number(route.params.group_id)
const group = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    const res = await api.post('api/group/get_single/', {group_id: groupId})
    if (res.data.result === 'success') {
      group.value = res.data.group
    } else {
      error.value = res.data.result
    }
  } catch (err) {
    error.value = '加载群信息失败'
  }
})
</script>

<template>
  <div v-if="error" class="flex justify-center items-center h-screen text-red-500">{{ error }}</div>
  <div v-else-if="!group" class="flex justify-center items-center h-screen text-gray-500">加载中...</div>
  <div v-else class="flex h-screen">
    <div class="flex-1 flex flex-col">
      <div class="bg-base-200 p-4 flex items-center justify-between">
        <h1 class="text-xl font-bold">{{ group.name }}</h1>
        <span class="text-sm text-gray-500">{{ group.members.length }}人 · {{ group.characters.length }}角色</span>
      </div>
      <GroupChatField :group-id="groupId" :characters="group.characters" :members="group.members" />
      <GroupInputField :group-id="groupId" :characters="group.characters" />
    </div>
    <GroupInfoPanel :group="group" />
  </div>
</template>

<style scoped></style>
```

- [ ] **Step 2: 聊天区域 (`GroupChatField.vue`)**

```vue
<script setup>
import {ref, watch} from "vue";
import api from "@/js/http/api.js";

const props = defineProps(['groupId', 'characters', 'members'])
const history = ref([])
const isLoadingHistory = ref(false)

function getSenderInfo(sender) {
  if (!sender) return {name: '未知', photo: ''}
  if (sender.name) return {name: sender.name, photo: sender.photo || ''}
  return {name: sender.username, photo: sender.photo || ''}
}

async function loadHistory() {
  isLoadingHistory.value = true
  try {
    const res = await api.post('api/group/message/history/', {
      group_id: props.groupId,
      items_count: 0,
    })
    if (res.data.result === 'success') {
      history.value = res.data.messages
    }
  } catch (err) {
    console.log(err)
  } finally {
    isLoadingHistory.value = false
  }
}

function pushMessage(msg) {
  history.value.push(msg)
  scrollToBottom()
}

function appendContent(speakerId, speakerName, delta) {
  const last = history.value.findLast(m => m.speakerId === speakerId && !m.done)
  if (last) {
    last.content += delta
  } else {
    history.value.push({
      speakerId,
      speakerName,
      content: delta,
      done: false,
    })
  }
  scrollToBottom()
}

function markSpeakerDone(speakerId) {
  const msg = history.value.find(m => m.speakerId === speakerId && !m.done)
  if (msg) msg.done = true
}

function scrollToBottom() {
  // 通过 ref 滚动，简化处理
}

watch(() => props.groupId, () => {
  history.value = []
  loadHistory()
}, {immediate: true})
</script>

<template>
  <div class="flex-1 overflow-y-auto p-4 space-y-4">
    <div v-if="history.length === 0 && !isLoadingHistory" class="text-center text-gray-400 mt-32">
      暂无消息，发送第一条消息吧
    </div>
    <div v-for="(msg, idx) in history" :key="idx">
      <div v-if="msg.content" class="chat" :class="msg.senderId ? 'chat-start' : 'chat-end'">
        <div class="chat-header text-xs text-gray-500 mb-1">
          {{ msg.senderId ? msg.speakerName : '你' }}
        </div>
        <div class="chat-bubble" :class="msg.senderId ? '' : 'chat-bubble-primary'">
          {{ msg.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/group/GroupChat.vue frontend/src/views/group/components/GroupChatField.vue
git commit -m "feat: 添加群聊页面和聊天区域组件"
```

---

### Task 12: 前端 — 输入框和信息面板

**Files:**
- Create: `frontend/src/views/group/components/GroupInputField.vue`
- Create: `frontend/src/views/group/components/GroupInfoPanel.vue`

- [ ] **Step 1: 输入框 (`GroupInputField.vue`)**

```vue
<script setup>
import {ref} from "vue";
import streamApi from "@/js/http/streamApi.js";

const props = defineProps(['groupId', 'characters'])
const emit = defineEmits(['pushMessage', 'appendContent', 'markSpeakerDone'])
const message = ref('')

let processId = 0

async function handleSend() {
  const content = message.value.trim()
  if (!content) return

  const curId = ++processId

  // 解析 @ 提及
  const mentionPattern = /@(\S+)/g
  const mentionedNames = [...content.matchAll(mentionPattern)].map(m => m[1])
  const mentions = props.characters
    .filter(c => mentionedNames.includes(c.name))
    .map(c => c.id)

  message.value = ''

  emit('pushMessage', {speakerId: null, speakerName: '你', content, done: true})

  try {
    await streamApi('/api/group/message/chat/', {
      body: {
        group_id: props.groupId,
        message: content,
        mentions,
      },
      onmessage(data, isDone) {
        if (curId !== processId) return
        if (isDone) return

        if (data.speaker && data.content) {
          emit('appendContent', data.speaker.id, data.speaker.name, data.content)
        }
        if (data.speaker && data.done) {
          emit('markSpeakerDone', data.speaker.id)
        }
        // round_start / round_complete events 可以用于 UI 状态展示
      },
      onerror(err) {
        console.error(err)
      },
    })
  } catch (err) {
    console.log(err)
  }
}
</script>

<template>
  <form @submit.prevent="handleSend" class="p-4 bg-base-200">
    <div class="flex items-center gap-2">
      <input
        v-model="message"
        class="input input-bordered flex-1"
        type="text"
        placeholder="输入消息（@角色名 可以指定回复对象）..."
      >
      <button type="submit" class="btn btn-primary">发送</button>
    </div>
    <div v-if="characters.length" class="text-xs text-gray-400 mt-1">
      可@角色：<span v-for="c in characters" :key="c.id" class="mr-2">@{{ c.name }}</span>
    </div>
  </form>
</template>

<style scoped></style>
```

- [ ] **Step 2: 信息面板 (`GroupInfoPanel.vue`)**

```vue
<script setup>
import {ref} from "vue";
import api from "@/js/http/api.js";
import {useUserStore} from "@/stores/user.js";

const props = defineProps(['group'])
const user = useUserStore()
const activeTab = ref('members')

function isOwner() {
  return user.id === props.group.owner_id
}
</script>

<template>
  <div class="w-72 bg-base-200 p-4 border-l overflow-y-auto">
    <div class="tabs tabs-box mb-4">
      <a class="tab" :class="{'tab-active': activeTab === 'members'}" @click="activeTab = 'members'">成员</a>
      <a class="tab" :class="{'tab-active': activeTab === 'characters'}" @click="activeTab = 'characters'">角色</a>
    </div>

    <div v-if="activeTab === 'members'" class="space-y-3">
      <div v-for="m in group.members" :key="m.user_id" class="flex items-center gap-3">
        <div class="avatar">
          <div class="w-10 rounded-full">
            <img :src="m.photo" alt="">
          </div>
        </div>
        <div>
          <div class="text-sm font-medium">{{ m.username }}</div>
          <div class="text-xs text-gray-500">{{ m.role === 'owner' ? '群主' : m.role === 'admin' ? '管理员' : '成员' }}</div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'characters'" class="space-y-3">
      <div v-for="c in group.characters" :key="c.id" class="flex items-center gap-3">
        <div class="avatar">
          <div class="w-10 rounded-full">
            <img :src="c.photo" alt="">
          </div>
        </div>
        <div>
          <div class="text-sm font-medium">{{ c.name }}</div>
          <div class="text-xs text-gray-500 line-clamp-2">{{ c.profile }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/group/components/GroupInputField.vue frontend/src/views/group/components/GroupInfoPanel.vue
git commit -m "feat: 添加群聊输入框和信息面板组件"
```

---

### Task 13: 前端 — 路由注册

**Files:**
- Modify: `frontend/src/router/index.js` (追加两行路由)

- [ ] **Step 1: 追加群聊路由**

在 `routes` 数组中追加：
```javascript
    {
      path: '/group/',
      component: () => import('@/views/group/GroupIndex.vue'),
      name: 'group-index',
      meta: { needLogin: true }
    },
    {
      path: '/group/:group_id/chat/',
      component: () => import('@/views/group/GroupChat.vue'),
      name: 'group-chat',
      meta: { needLogin: true }
    },
```

- [ ] **Step 2: 在导航栏中添加群聊入口**

在 `NavBar.vue` 中找一个合适位置添加群聊导航项。但用户要求不修改现有文件，所以暂时通过 URL 直接访问 `/group/`。后续可以单独调整。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/index.js
git commit -m "feat: 注册群聊前端路由"
```

---

### Task 14: 联调验证

- [ ] **Step 1: 启动后端**

Run: `cd backend && python manage.py runserver`
Expected: `Starting development server at http://127.0.0.1:8000/`

- [ ] **Step 2: 验证 API — 创建群**

```bash
curl -X POST http://127.0.0.1:8000/api/group/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试群","description":"测试"}'
```
Expected: `{"result":"success","group":{"id":1,...}}`

- [ ] **Step 3: 验证 API — 群聊 SSE**

```bash
curl -X POST http://127.0.0.1:8000/api/group/message/chat/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"group_id":1,"message":"大家好","mentions":[]}'
```
Expected: SSE 流式返回角色回复

- [ ] **Step 4: 验证前端**

打开 `http://localhost:5173/group/`，创建群、进入群聊、发送消息、观察角色并行回复。

- [ ] **Step 5: Commit any fixes**

```bash
git add -A
git commit -m "fix: 联调修复"
```
