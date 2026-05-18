from django.db import models
from django.utils.timezone import localtime, now

from web.models.character import Character
from web.models.user import UserProfile


class GroupChat(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='owned_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, default='', blank=True)
    create_time = models.DateTimeField(default=now)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.name} - {self.owner.user.username} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('owner', '群主'),
        ('admin', '管理员'),
        ('member', '成员'),
    ]
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    join_time = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.group.name} - {self.user.user.username} - {self.role}"


class GroupCharacter(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='characters')
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    added_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    add_time = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('group', 'character')

    def __str__(self):
        return f"{self.group.name} - {self.character.name}"


class GroupMessage(models.Model):
    SENDER_TYPE_CHOICES = [
        ('user', '用户'),
        ('character', '角色'),
    ]
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPE_CHOICES)
    sender_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    sender_character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(max_length=2000)
    mentions = models.JSONField(default=list, blank=True)
    create_time = models.DateTimeField(default=now)

    def __str__(self):
        sender = self.sender_character.name if self.sender_type == 'character' else self.sender_user.user.username
        return f"{self.group.name} - {sender} - {self.content[:50]} - {localtime(self.create_time).strftime('%Y-%m-%d %H:%M:%S')}"


class GroupMemory(models.Model):
    group = models.OneToOneField(GroupChat, on_delete=models.CASCADE, related_name='memory')
    memory = models.TextField(max_length=5000, default='', blank=True)
    update_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.group.name} - memory - {localtime(self.update_time).strftime('%Y-%m-%d %H:%M:%S')}"
