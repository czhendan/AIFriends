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
