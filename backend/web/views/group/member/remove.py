from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember
from web.models.user import UserProfile


class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            target_user_id = request.data.get('user_id')

            if not target_user_id:
                return Response({'result': '用户ID不能为空'})

            user_profile = UserProfile.objects.get(user=request.user)
            operator = GroupMember.objects.filter(
                group_id=group_id, user=user_profile, role__in=['owner', 'admin']
            )
            if not operator.exists():
                return Response({'result': '无权操作'})

            group = GroupChat.objects.get(pk=group_id)
            if group.owner.user_id == target_user_id:
                return Response({'result': '不能移除群主'})

            target = GroupMember.objects.filter(group_id=group_id, user__user_id=target_user_id)
            if not target.exists():
                return Response({'result': '该成员不在群中'})

            target.delete()
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
