from django.contrib import admin

from web.models.character import Character
# Register your models here.
from web.models.user import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',) #,逗号千万不要删除！！！

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',) #,逗号千万不要删除！！！