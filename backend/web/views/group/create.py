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
