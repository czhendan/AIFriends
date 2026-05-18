<script setup>
import {onMounted, ref, useTemplateRef} from "vue";
import {useRoute} from "vue-router";
import api from "@/js/http/api.js";
import GroupChatField from "@/views/group/components/GroupChatField.vue";
import GroupInputField from "@/views/group/components/GroupInputField.vue";
import GroupInfoPanel from "@/views/group/components/GroupInfoPanel.vue";

const route = useRoute()
const groupId = Number(route.params.group_id)
const group = ref(null)
const error = ref('')
const chatFieldRef = useTemplateRef('chat-field-ref')

async function loadGroup() {
  try {
    const res = await api.post('api/group/get_single/', {group_id: groupId})
    if (res.data.result === 'success') {
      group.value = res.data.group
    } else {
      error.value = res.data.result
    }
  } catch (err) {
    error.value = '加载群信息失败'
  }
}

function handlePushMessage(msg) {
  chatFieldRef.value.pushMessage(msg)
}

function handleAppendContent(speakerId, speakerName, delta) {
  chatFieldRef.value.appendContent(speakerId, speakerName, delta)
}

function handleMarkSpeakerDone(speakerId) {
  chatFieldRef.value.markSpeakerDone(speakerId)
}

onMounted(loadGroup)
</script>

<template>
  <div v-if="error" class="flex justify-center items-center h-screen text-red-500">{{ error }}</div>
  <div v-else-if="!group" class="flex justify-center items-center h-screen text-gray-500">加载中...</div>
  <div v-else class="flex h-screen">
    <div class="flex-1 flex flex-col">
      <div class="bg-base-200 p-4 flex items-center justify-between">
        <h1 class="text-xl font-bold">{{ group.name }}</h1>
        <span class="text-sm text-gray-500">{{ group.members.length }}人 · {{ group.characters.length }}角色</span>
      </div>
      <GroupChatField
        ref="chat-field-ref"
        :group-id="groupId"
        :characters="group.characters"
        :members="group.members"
      />
      <GroupInputField
        :group-id="groupId"
        :characters="group.characters"
        @pushMessage="handlePushMessage"
        @appendContent="handleAppendContent"
        @markSpeakerDone="handleMarkSpeakerDone"
      />
    </div>
    <GroupInfoPanel :group="group" @update="loadGroup" />
  </div>
</template>

<style scoped></style>
