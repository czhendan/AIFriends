<script setup>
import {ref} from "vue";
import streamApi from "@/js/http/streamApi.js";

const props = defineProps(['groupId', 'characters'])
const emit = defineEmits(['pushMessage', 'appendContent', 'markSpeakerDone'])
const message = ref('')

let processId = 0

async function handleSend() {
  const content = message.value.trim()
  if (!content) return

  const curId = ++processId

  const mentionPattern = /@(\S+)/g
  const mentionedNames = [...content.matchAll(mentionPattern)].map(m => m[1])
  const mentions = props.characters
    .filter(c => mentionedNames.includes(c.name))
    .map(c => c.id)

  message.value = ''

  emit('pushMessage', {speakerId: null, speakerName: '你', content, done: true})

  try {
    await streamApi('/api/group/message/chat/', {
      body: {
        group_id: props.groupId,
        message: content,
        mentions,
      },
      onmessage(data, isDone) {
        if (curId !== processId) return
        if (isDone) return

        if (data.speaker && data.content) {
          emit('appendContent', data.speaker.id, data.speaker.name, data.content)
        }
        if (data.speaker && data.done) {
          emit('markSpeakerDone', data.speaker.id)
        }
      },
      onerror(err) {
        console.error(err)
      },
    })
  } catch (err) {
    console.log(err)
  }
}
</script>

<template>
  <form @submit.prevent="handleSend" class="p-4 bg-base-200">
    <div class="flex items-center gap-2">
      <input
        v-model="message"
        class="input input-bordered flex-1"
        type="text"
        placeholder="输入消息（@角色名 可以指定回复对象）..."
      >
      <button type="submit" class="btn btn-primary">发送</button>
    </div>
    <div v-if="characters.length" class="text-xs text-gray-400 mt-1">
      可@角色：<span v-for="c in characters" :key="c.id" class="mr-2">@{{ c.name }}</span>
    </div>
  </form>
</template>

<style scoped></style>
