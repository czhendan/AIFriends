from langchain_core.messages import HumanMessage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend
from web.views.friend.message.chat.graph import ChatGraph


class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        friend_id = request.data.get('friend_id')
        message = request.data.get('message').strip()
        if not message:
            return Response({
                'result': '消息不能位空'
            })
        friends = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friends.exists():
            return Response({
                'result': '好友不存在'
            })
        friend = friends.first()
        app = ChatGraph.create_app()

        input = {
            'messages': [HumanMessage(message=message)],
        }
        res = app.invoke(input)
        print(res['messages'][-1].content)

        return Response({
            'result': 'success',
        })

