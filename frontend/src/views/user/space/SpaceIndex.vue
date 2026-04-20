<script setup>
import {useRoute} from "vue-router";
import UserInfoField from "@/views/user/space/UserInfoField.vue";
import Character from "@/components/character/Character.vue";
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

const route = useRoute()
const userProfile = ref(null)
const characters = ref([])
const isLoading = ref(false)
const hasCharacters = ref(true)
const sentinelRef = useTemplateRef('sentinel-ref')
let observer = null

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
}

async function loadMore() {
  if (isLoading.value || !hasCharacters.value) return
  isLoading.value = true

  let newCharacters = []
  try {
    const res = await api.get('api/create/character/get_list/', {
      params: {
        items_count: characters.value.length,
        user_id: route.params.user_id
      }
    })
    const data = res.data
    if (data.result === 'success') {
      userProfile.value = data.user_profile
      newCharacters = data.characters
    }
  } catch (err) {
    console.log(err)
  } finally {
    isLoading.value = false
    if (newCharacters.length === 0) {
      hasCharacters.value = false
    } else {
      characters.value.push(...newCharacters)
      await nextTick()

      if (checkSentinelVisible()) {
        await loadMore()
      }
    }
  }
}

onMounted(async () => {
  await loadMore()

  observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            loadMore()
          }
        })
      },
      {root: null, rootMargin: '2px', threshold: 0}
  )

  //监听哨兵元素， 每次哨兵被看到时，都会触发一次
  observer.observe(sentinelRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <div class="flex flex-col items-center">
    <UserInfoField :userProfile="userProfile" />
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">

    </div>
    <!-- 设置哨兵 -->
    <div ref="sentinel-ref" class="h-2 mt-8 w-100 bg-red-500"></div>
    <div v-if="isLoading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasCharacters" class="text-gray-500 mt-4">没有更多角色了</div>
  </div>
</template>

<style scoped>

</style>