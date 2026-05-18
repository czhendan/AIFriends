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
