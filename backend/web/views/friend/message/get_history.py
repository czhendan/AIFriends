from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Message


class GetHistoryView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            last_message_id = int(request.query_params.get('last_message_id'))
            friend_id = request.query_params.get('friend_id')
            queryset = Message.objects.filter(friend_id=friend_id, friend__me__user=request.user)
            if last_message_id > 0:
                queryset = queryset.filter(pk__lt=last_message_id)
            messages_raw = queryset.order_by('-id')[:10]
            messages = []
            for message in messages_raw:
                messages.append({
                    'id': message.id,
                    'user_message': message.user_message,
                    'output': message.output,
                })
            return Response({
                'result': 'success',
                'messages': messages,
            })
        except:
            return Response({
                'result': '系统异常，请稍后再试',
            })