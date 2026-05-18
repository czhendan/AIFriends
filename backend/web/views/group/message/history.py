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
