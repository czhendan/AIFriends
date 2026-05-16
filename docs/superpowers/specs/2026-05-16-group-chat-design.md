# 群聊功能设计文档

**日期**: 2026-05-16
**状态**: 已确认

---

## 需求概述

在现有 1v1 AI 好友聊天基础上，新增群聊功能。类似微信群，多个真实用户和多个 AI 角色在同一个群里，任何人都可以发消息触发角色回复。

### 核心决策

| 维度 | 决定 |
|------|------|
| 参与者 | 多用户 + 多角色 |
| 触发机制 | LLM 自主判断 + @强制指定 + 限制自动触发最多 2 轮 |
| 群管理 | 群主制（创建者管理成员和角色） |
| 回复方式 | 并行生成，各角色基于共同初始上下文独立生成，互不可见 |
| 群记忆 | 群级独立记忆，不跨上下文共享 |
| 语音 | 纯文字，无 TTS/ASR |

---

## 数据模型

新建文件 `web/models/group_chat.py`：

### GroupChat
群聊主体。`owner` 指向创建者（UserProfile），群主有管理权限。

### GroupMember
用户-群关系。`role`: owner / admin / member。

### GroupCharacter  
角色-群关系。记录哪个角色被拉入了哪个群。

### GroupMessage
群聊消息。用 `sender_type` (user/character) + `sender_user` + `sender_character` 区分消息来源。`mentions` 字段（JSON）存储被 @ 的角色 id 列表。

### GroupMemory
群的长期记忆。与 GroupChat 一对一。存储由 LLM 总结的群聊话题、角色观点、用户偏好等摘要文本。

---

## 多角色对话引擎

新建文件 `web/views/group/message/chat/graph.py`

### 流程

```
用户发言
  → 发言选择器（SpeakerPicker）：输入上下文 + 角色人设 + 群记忆 + @信息
    → 输出本轮要回复的角色列表
  → asyncio.gather 并行生成（各角色共享相同初始上下文，互不可见）
  → 所有回复通过 SSE 推给前端
  → 收敛检查：
    - 如果当前是第 2 轮自动触发 → 强制结束
    - 如果不足 2 轮 → 再次调用发言选择器判断是否需要继续
    - 选择器返回空列表 → 立即结束，等待用户输入
```

### 收敛控制
- 用户发言后，角色自动触发角色最多 **2 轮**
- 发言选择器判断"该用户说话了"时返回空列表，对话自然暂停
- @ 指定的角色一定会被加入回复列表

### 并行生成
- 发言人选择器输出角色列表后，`asyncio.gather` 并发调用 LLM
- 每个角色拿到相同的初始上下文（不含其他角色本次的回复）
- 所有 chunk 通过共享队列发给主线程

---

## API 设计

所有端点需要 JWT 认证。管理类操作校验群主/管理员权限。

### 群管理
- `POST /api/group/create/` — 创建群
- `POST /api/group/update/` — 修改群信息
- `POST /api/group/remove/` — 解散群
- `POST /api/group/get_list/` — 我的群列表
- `POST /api/group/get_single/` — 单个群详情

### 成员管理
- `POST /api/group/member/add/` — 拉人进群
- `POST /api/group/member/remove/` — 移出群成员

### 角色管理
- `POST /api/group/character/add/` — 拉角色进群
- `POST /api/group/character/remove/` — 移出角色

### 消息
- `POST /api/group/message/chat/` — 群聊 SSE 流
- `POST /api/group/message/history/` — 拉取历史消息

---

## SSE 流格式

一个请求可能多个角色同时回复，每个 chunk 带 speaker 信息区分说话者：

```
data: {"speaker": {"id": 12, "name": "张三"}, "content": "你好"}
data: {"speaker": {"id": 12, "name": "张三"}, "content": "啊"}
data: {"speaker": {"id": 12, "name": "张三"}, "done": true}

data: {"speaker": {"id": 7, "name": "李四"}, "content": "大家好"}
data: {"speaker": {"id": 7, "name": "李四"}, "done": true}

data: {"event": "round_complete", "round": 1}
data: {"event": "round_start", "round": 2}

data: [DONE]
```

多角色并行时 chunk 可能交错到达，前端按 `speaker.id` 路由到对应气泡。

---

## 群聊记忆系统

新建文件 `web/views/group/message/chat/memory.py`

### 触发条件
群聊每轮对话结束后，检查 `GroupMessage` 总数是否为 20 的倍数。是则触发记忆更新。

### 更新方式
使用 LangGraph Chain（类似现有 MemoryGraph），输入旧记忆 + 最近对话，输出不超过 500 字的新记忆。

### 记忆内容重点
- 群聊的主要讨论话题和进展
- 每个角色的重要观点和态度
- 用户的关键信息和偏好

---

## 文件结构

### 后端新增（`backend/web/` 下）

```
web/
├── models/
│   └── group_chat.py
├── views/group/
│   ├── __init__.py
│   ├── create.py
│   ├── get_list.py
│   ├── get_single.py
│   ├── member/
│   │   ├── __init__.py
│   │   ├── add.py
│   │   └── remove.py
│   ├── character/
│   │   ├── __init__.py
│   │   ├── add.py
│   │   └── remove.py
│   └── message/
│       ├── __init__.py
│       ├── history.py
│       └── chat/
│           ├── __init__.py
│           ├── chat.py
│           ├── graph.py
│           └── memory/
│               ├── __init__.py
│               ├── graph.py
│               └── update.py
├── migrations/
│   └── 0010_group_chat.py
```

### 后端修改
`web/urls.py` 新增路由行。

### 前端新增（`frontend/src/` 下）

```
views/group/
├── GroupIndex.vue
├── GroupChat.vue
├── components/
│   ├── GroupCreateModal.vue
│   ├── GroupInfoPanel.vue
│   ├── GroupChatField.vue
│   ├── GroupInputField.vue
│   └── GroupSpeakerBubble.vue
```

---

## 技术约束

- 不修改现有文件（`web/urls.py` 仅追加路由行）
- 沿用现有技术栈：Django + DRF + LangGraph + LangChain + SSE
- 前端沿用 Vue 3 + fetchEventSource
- 已有 Model（Character、UserProfile 等）通过 import 引用，不做修改
