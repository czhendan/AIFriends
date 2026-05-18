<script setup>
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";
import GroupCreateModal from "@/views/group/components/GroupCreateModal.vue";

const groups = ref([])
const isLoading = ref(false)
const hasMore = ref(true)
const sentinelRef = useTemplateRef('sentinel-ref')
const groupCreateModalRef = useTemplateRef('group-create-modal-ref')
const router = useRouter()

function checkSentinelVisible() {
  if (!sentinelRef.value) return false
  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

async function loadMore() {
  if (isLoading.value || !hasMore.value) return
  isLoading.value = true

  let newGroups = []
  try {
    const res = await api.post('api/group/get_list/', {
      items_count: groups.value.length,
    })
    const data = res.data
    if (data.result === 'success') {
      newGroups = data.groups
    }
  } catch (err) {
    console.log(err)
  } finally {
    isLoading.value = false
    if (newGroups.length === 0) {
      hasMore.value = false
    } else {
      groups.value.push(...newGroups)
      await nextTick()
      if (checkSentinelVisible()) {
        await loadMore()
      }
    }
  }
}

let observer = null
onMounted(async () => {
  await loadMore()
  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) loadMore()
      })
    },
    {root: null, rootMargin: '2px', threshold: 0}
  )
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

function openChat(groupId) {
  router.push({name: 'group-chat', params: {group_id: groupId}})
}

async function handleRemoveGroup(groupId, event) {
  event.stopPropagation()
  if (!confirm('确定要解散这个群聊吗？')) return

  try {
    const res = await api.post('api/group/remove/', {group_id: groupId})
    if (res.data.result === 'success') {
      groups.value = groups.value.filter(g => g.id !== groupId)
    }
  } catch (err) {
    console.log(err)
  }
}

function handleCreated(newGroup) {
  groups.value.unshift(newGroup)
}
</script>

<template>
  <div class="flex flex-col items-center">
    <div class="flex justify-between items-center w-full max-w-3xl mt-8 px-9">
      <h1 class="text-2xl font-bold">群聊</h1>
      <button class="btn btn-primary" @click="groupCreateModalRef.showModal()">创建群聊</button>
    </div>

    <div v-if="groups.length === 0 && !isLoading" class="text-gray-500 mt-16">
      暂无群聊，创建一个吧
    </div>

    <div class="w-full max-w-3xl px-9 mt-6 space-y-4">
      <div
        v-for="g in groups" :key="g.id"
        class="card bg-base-100 shadow-md cursor-pointer hover:bg-base-200 transition relative"
        @click="openChat(g.id)"
      >
        <button
          v-if="g.role === 'owner'"
          class="btn btn-ghost btn-xs btn-circle absolute top-2 right-2 z-10"
          @click="handleRemoveGroup(g.id, $event)"
        >✕</button>
        <div class="card-body p-6">
          <div class="flex justify-between items-center">
            <h2 class="card-title text-lg">{{ g.name }}</h2>
            <span class="text-sm text-gray-500">{{ g.member_count }}人 · {{ g.character_count }}角色</span>
          </div>
          <p v-if="g.description" class="text-sm text-gray-500 mt-1">{{ g.description }}</p>
        </div>
      </div>
    </div>

    <div ref="sentinel-ref" class="h-2 mt-8"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>

    <GroupCreateModal ref="group-create-modal-ref" @created="handleCreated" />
  </div>
</template>

<style scoped></style>
