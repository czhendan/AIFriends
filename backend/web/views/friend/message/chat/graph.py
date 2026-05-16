import os
from typing import TypedDict, Annotated, Sequence

from django.utils.timezone import localtime, now
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode

class ChatGraph:
    @staticmethod
    def create_app():
        @tool
        def get_time() -> str:
            """当需要查询精确时间时，调用此函数，返回格式为 {年-月-日 时:分:秒}"""
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        @tool
        def search_knowledge_base(query: str) -> str:
            """当用户查询阿里云百炼平台或者千问（qwen）的相关信息时，调用此函数，输入为要查询的问题，输出为查询结果。"""
            from web.documents.utils.hybrid_search import hybrid_search
            results = hybrid_search(query, k_vector=10, k_bm25=10, final_k=5)
            context = '\n\n'.join([
                f"内容片段 {i + 1}：\n{r['content']}" for i, r in enumerate(results)
            ])
            return f"从知识库中找到以下相关信息：\n\n{context}\n"


        tools = [get_time, search_knowledge_base]

        llm = ChatOpenAI(
            model=os.getenv('MODEL'),
            # model="deepseek-v4-flash",
            # model="gpt-4.1-free",
            openai_api_key =os.getenv('API_KEY'),
            openai_api_base=os.getenv('API_BASE'),
            streaming=True,
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出token消耗数量
                }
            }
        ).bind_tools(tools)

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages'])
            return {'messages': [res]}

        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"

        tool_node = ToolNode(tools)

        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)
        graph.add_node('tools', tool_node)
        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            should_continue,
            path_map= {
                "tools": 'tools',
                "end": END,
            },
        )
        graph.add_edge('tools', 'agent')

        return graph.compile()
