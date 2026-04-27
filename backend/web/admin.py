from django.contrib import admin

# Register your models here.
from web.models.character import Character
from web.models.user import UserProfile
from web.models.friend import Friend, Message

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',) #,逗号千万不要删除！！！

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',) #,逗号千万不要删除！！！

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    raw_id_fields = ('me', 'character',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    raw_id_fields = ('friend',)