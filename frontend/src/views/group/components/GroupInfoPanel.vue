<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";

const props = defineProps(['group'])
const user = useUserStore()
const activeTab = ref('members')

function isOwner() {
  return user.id === props.group.owner_id
}
</script>

<template>
  <div class="w-72 bg-base-200 p-4 border-l overflow-y-auto">
    <div class="tabs tabs-box mb-4">
      <a class="tab" :class="{'tab-active': activeTab === 'members'}" @click="activeTab = 'members'">成员</a>
      <a class="tab" :class="{'tab-active': activeTab === 'characters'}" @click="activeTab = 'characters'">角色</a>
    </div>

    <div v-if="activeTab === 'members'" class="space-y-3">
      <div v-for="m in group.members" :key="m.user_id" class="flex items-center gap-3">
        <div class="avatar">
          <div class="w-10 rounded-full">
            <img :src="m.photo" alt="">
          </div>
        </div>
        <div>
          <div class="text-sm font-medium">{{ m.username }}</div>
          <div class="text-xs text-gray-500">{{ m.role === 'owner' ? '群主' : m.role === 'admin' ? '管理员' : '成员' }}</div>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'characters'" class="space-y-3">
      <div v-for="c in group.characters" :key="c.id" class="flex items-center gap-3">
        <div class="avatar">
          <div class="w-10 rounded-full">
            <img :src="c.photo" alt="">
          </div>
        </div>
        <div>
          <div class="text-sm font-medium">{{ c.name }}</div>
          <div class="text-xs text-gray-500 line-clamp-2">{{ c.profile }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
