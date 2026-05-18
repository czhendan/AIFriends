<script setup>
import {computed, ref, watch} from "vue";
import streamApi from "@/js/http/streamApi.js";

const props = defineProps(['groupId', 'characters'])
const emit = defineEmits(['pushMessage', 'appendContent', 'markSpeakerDone'])
const message = ref('')
const inputRef = ref(null)
const showMentionList = ref(false)
const mentionQuery = ref('')
const selectedMentionIndex = ref(0)

let processId = 0

const filteredCharacters = computed(() => {
  if (!mentionQuery.value) return props.characters || []
  const q = mentionQuery.value.toLowerCase()
  return (props.characters || []).filter(c =>
    c.name.toLowerCase().includes(q)
  )
})

function onInput(event) {
  showMentionList.value = false
  mentionQuery.value = ''

  const textarea = event.target
  const pos = textarea.selectionStart
  const beforeCursor = textarea.value.substring(0, pos)
  const atMatch = beforeCursor.match(/@([^\s@]*)$/)

  if (atMatch) {
    mentionQuery.value = atMatch[1]
    showMentionList.value = true
    selectedMentionIndex.value = 0
  }
}

function insertMention(character) {
  const textarea = inputRef.value
  const pos = textarea.selectionStart
  const beforeCursor = textarea.value.substring(0, pos)
  const afterCursor = textarea.value.substring(pos)
  const atIdx = beforeCursor.lastIndexOf('@')
  const newBefore = beforeCursor.substring(0, atIdx) + `@${character.name} `
  message.value = newBefore + afterCursor
  showMentionList.value = false
  mentionQuery.value = ''
  // 把光标放到插入文本后面
  setTimeout(() => {
    textarea.selectionStart = textarea.selectionEnd = newBefore.length
    textarea.focus()
  }, 0)
}

function onKeyDown(event) {
  if (!showMentionList.value || filteredCharacters.value.length === 0) return

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    selectedMentionIndex.value = Math.min(
      selectedMentionIndex.value + 1,
      filteredCharacters.value.length - 1
    )
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    selectedMentionIndex.value = Math.max(selectedMentionIndex.value - 1, 0)
  } else if (event.key === 'Enter' || event.key === 'Tab') {
    event.preventDefault()
    insertMention(filteredCharacters.value[selectedMentionIndex.value])
  } else if (event.key === 'Escape') {
    showMentionList.value = false
  }
}

async function handleSend() {
  const content = message.value.trim()
  if (!content) return

  const curId = ++processId

  const mentionPattern = /@(\S+)/g
  const mentionedNames = [...content.matchAll(mentionPattern)].map(m => m[1])
  const mentions = props.characters
    .filter(c => mentionedNames.includes(c.name))
    .map(c => c.id)

  showMentionList.value = false
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
  <div class="p-4 bg-base-200 relative">
    <form @submit.prevent="handleSend" class="flex items-center gap-2">
      <div class="flex-1 relative">
        <input
          ref="inputRef"
          v-model="message"
          class="input input-bordered flex-1"
          type="text"
          placeholder="输入消息（@角色名 可以指定回复对象）..."
          @input="onInput"
          @keydown="onKeyDown"
        >

        <!-- @ 自动补全列表 -->
        <ul
          v-if="showMentionList && filteredCharacters.length > 0"
          class="absolute bottom-full left-0 mb-1 w-64 bg-base-100 border rounded-lg shadow-lg max-h-48 overflow-y-auto z-50"
        >
          <li
            v-for="(c, idx) in filteredCharacters"
            :key="c.id"
            class="flex items-center gap-2 px-3 py-2 cursor-pointer"
            :class="idx === selectedMentionIndex ? 'bg-primary/20' : 'hover:bg-base-200'"
            @mousedown.prevent="insertMention(c)"
          >
            <div class="avatar">
              <div class="w-6 rounded-full">
                <img :src="c.photo" alt="">
              </div>
            </div>
            <span class="text-sm">{{ c.name }}</span>
          </li>
        </ul>
      </div>
      <button type="submit" class="btn btn-primary">发送</button>
    </form>
    <div v-if="characters.length" class="text-xs text-gray-400 mt-1">
      可@角色：<span v-for="c in characters" :key="c.id" class="mr-2">@{{ c.name }}</span>
    </div>
  </div>
</template>

<style scoped></style>
