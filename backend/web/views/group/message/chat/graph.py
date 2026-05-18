import json
import os
from typing import TypedDict, Annotated, Sequence, List

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


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
    def build_speaker_prompt(char_map: dict, mentioned_character_ids: List[int], round_num: int) -> str:
        char_descriptions = []
        for cid, info in char_map.items():
            char_descriptions.append(f"- ID:{cid} | {info['name']} | {info['profile'][:200]}")

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

        return f"""你是群聊调度员。根据当前对话上下文，判断哪些角色应该发言。

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

    @staticmethod
    def build_character_prompt(character_id: int, char_map: dict, group_memory: str) -> SystemMessage:
        char_info = char_map.get(character_id, {})
        char_name = char_info.get('name', '未知角色')
        char_profile = char_info.get('profile', '')

        memory_text = ''
        if group_memory:
            memory_text = f"\n【群聊记忆】\n{group_memory}\n"

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
