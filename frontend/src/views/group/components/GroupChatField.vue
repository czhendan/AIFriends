<script setup>
import {ref, watch, useTemplateRef, nextTick} from "vue";
import api from "@/js/http/api.js";

const props = defineProps(['groupId', 'characters', 'members'])
const history = ref([])
const isLoadingHistory = ref(false)
const chatContainerRef = useTemplateRef('chat-container-ref')

async function loadHistory() {
  isLoadingHistory.value = true
  try {
    const res = await api.post('api/group/message/history/', {
      group_id: props.groupId,
      items_count: 0,
    })
    if (res.data.result === 'success') {
      history.value = res.data.messages.map(m => {
        if (m.sender_type === 'user') {
          return {
            speakerId: null,
            speakerName: '你',
            content: m.content,
            done: true,
          }
        } else {
          return {
            speakerId: m.sender.id,
            speakerName: m.sender.name,
            content: m.content,
            done: true,
          }
        }
      })
      await nextTick()
      scrollToBottom()
    }
  } catch (err) {
    console.log(err)
  } finally {
    isLoadingHistory.value = false
  }
}

function pushMessage(msg) {
  history.value.push(msg)
  scrollToBottom()
}

function appendContent(speakerId, speakerName, delta) {
  const last = history.value.findLast(m => m.speakerId === speakerId && !m.done)
  if (last) {
    last.content += delta
  } else {
    history.value.push({
      speakerId,
      speakerName,
      content: delta,
      done: false,
    })
  }
  scrollToBottom()
}

function markSpeakerDone(speakerId) {
  const msg = history.value.find(m => m.speakerId === speakerId && !m.done)
  if (msg) msg.done = true
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainerRef.value) {
      chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
    }
  })
}

defineExpose({
  pushMessage,
  appendContent,
  markSpeakerDone,
})

watch(() => props.groupId, () => {
  history.value = []
  loadHistory()
}, {immediate: true})
</script>

<template>
  <div ref="chat-container-ref" class="flex-1 overflow-y-auto p-4 space-y-4">
    <div v-if="history.length === 0 && !isLoadingHistory" class="text-center text-gray-400 mt-32">
      暂无消息，发送第一条消息吧
    </div>
    <div v-for="(msg, idx) in history" :key="idx">
      <div v-if="msg.content" class="chat" :class="msg.speakerId ? 'chat-start' : 'chat-end'">
        <div class="chat-header text-xs text-gray-500 mb-1">
          {{ msg.speakerId ? (msg.speakerName || '未知') : '你' }}
        </div>
        <div class="chat-bubble" :class="msg.speakerId ? '' : 'chat-bubble-primary'">
          {{ msg.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
