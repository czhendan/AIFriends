from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.group_chat import GroupChat, GroupMember
from web.models.user import UserProfile


class AddMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            group_id = request.data.get('group_id')
            username = request.data.get('username', '').strip()

            if not username:
                return Response({'result': '用户名不能为空'})

            user_profile = UserProfile.objects.get(user=request.user)
            operator = GroupMember.objects.filter(
                group_id=group_id, user=user_profile, role__in=['owner', 'admin']
            )
            if not operator.exists():
                return Response({'result': '无权操作'})

            target_user = User.objects.filter(username=username).first()
            if not target_user:
                return Response({'result': '用户不存在'})

            target_profile = UserProfile.objects.get(user=target_user)

            if GroupMember.objects.filter(group_id=group_id, user=target_profile).exists():
                return Response({'result': '该用户已在群中'})

            GroupMember.objects.create(
                group_id=group_id,
                user=target_profile,
                role='member',
            )
            return Response({'result': 'success'})
        except:
            return Response({'result': '系统异常，请稍后重试'})
