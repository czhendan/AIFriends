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
