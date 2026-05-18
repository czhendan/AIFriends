from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character
from web.models.group_chat import GroupChat, GroupMember, GroupCharacter
from web.models.user import UserProfile


class AddCharacterView(APIView):
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

            if GroupCharacter.objects.filter(group_id=group_id, character_id=character_id).exists():
                return Response({'result': '该角色已在群中'})

            GroupCharacter.objects.create(
                group_id=group_id,
                character_id=character_id,
                added_by=user_profile,
            )
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
