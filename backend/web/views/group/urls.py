from django.urls import path

from web.views.group.create import CreateGroupView, UpdateGroupView, RemoveGroupView
from web.views.group.get_list import GetListGroupView
from web.views.group.get_single import GetSingleGroupView
from web.views.group.member.add import AddMemberView
from web.views.group.member.remove import RemoveMemberView
from web.views.group.character.add import AddCharacterView
from web.views.group.character.remove import RemoveCharacterView
from web.views.group.message.history import GetGroupHistoryView
from web.views.group.message.chat.chat import GroupChatView

urlpatterns = [
    path('create/', CreateGroupView.as_view()),
    path('update/', UpdateGroupView.as_view()),
    path('remove/', RemoveGroupView.as_view()),
    path('get_list/', GetListGroupView.as_view()),
    path('get_single/', GetSingleGroupView.as_view()),
    path('member/add/', AddMemberView.as_view()),
    path('member/remove/', RemoveMemberView.as_view()),
    path('character/add/', AddCharacterView.as_view()),
    path('character/remove/', RemoveCharacterView.as_view()),
    path('message/chat/', GroupChatView.as_view()),
    path('message/history/', GetGroupHistoryView.as_view()),
]
