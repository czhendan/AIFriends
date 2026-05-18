<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import api from "@/js/http/api.js";

const props = defineProps(['group'])
const emit = defineEmits(['update'])
const user = useUserStore()
const activeTab = ref('members')

// 添加成员
const addMemberUsername = ref('')
const addMemberError = ref('')

// 添加角色
const characterSearchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const addCharacterError = ref('')

function isOwner() {
  return user.id === props.group.owner_id
}

function isAdmin() {
  return props.group.members.some(m => m.user_id === user.id && (m.role === 'owner' || m.role === 'admin'))
}

async function handleAddMember() {
  const username = addMemberUsername.value.trim()
  if (!username) return

  addMemberError.value = ''
  try {
    const res = await api.post('api/group/member/add/', {
      group_id: props.group.id,
      username,
    })
    if (res.data.result === 'success') {
      addMemberUsername.value = ''
      emit('update')
    } else {
      addMemberError.value = res.data.result
    }
  } catch (err) {
    addMemberError.value = '添加失败'
  }
}

async function handleSearchCharacters() {
  const query = characterSearchQuery.value.trim()
  if (!query) {
    searchResults.value = []
    return
  }

  isSearching.value = true
  try {
    const res = await api.get('api/homepage/index/', {
      params: { search_query: query, items_count: 0 }
    })
    if (res.data.result === 'success') {
      // 过滤掉已在群中的角色
      const groupCharIds = props.group.characters.map(c => c.id)
      searchResults.value = res.data.characters.filter(c => !groupCharIds.includes(c.id))
    }
  } catch (err) {
    console.log(err)
  } finally {
    isSearching.value = false
  }
}

async function handleAddCharacter(characterId) {
  addCharacterError.value = ''
  try {
    const res = await api.post('api/group/character/add/', {
      group_id: props.group.id,
      character_id: characterId,
    })
    if (res.data.result === 'success') {
      searchResults.value = searchResults.value.filter(c => c.id !== characterId)
      emit('update')
    } else {
      addCharacterError.value = res.data.result
    }
  } catch (err) {
    addCharacterError.value = '添加失败'
  }
}
</script>

<template>
  <div class="w-72 bg-base-200 p-4 border-l overflow-y-auto flex flex-col">
    <div class="tabs tabs-box mb-4">
      <a class="tab" :class="{'tab-active': activeTab === 'members'}" @click="activeTab = 'members'">成员</a>
      <a class="tab" :class="{'tab-active': activeTab === 'characters'}" @click="activeTab = 'characters'">角色</a>
    </div>

    <!-- 成员列表 -->
    <div v-if="activeTab === 'members'" class="flex-1 space-y-3">
      <div v-for="m in group.members" :key="m.user_id" class="flex items-center gap-3">
        <div class="avatar">
          <div class="w-10 rounded-full">
            <img :src="m.photo" alt="">
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium">{{ m.username }}</div>
          <div class="text-xs text-gray-500">{{ m.role === 'owner' ? '群主' : m.role === 'admin' ? '管理员' : '成员' }}</div>
        </div>
      </div>

      <!-- 添加成员（群主/管理员可见） -->
      <div v-if="isAdmin()" class="pt-3 border-t">
        <div class="text-xs text-gray-500 mb-2">添加成员</div>
        <div class="flex gap-1">
          <input
            v-model="addMemberUsername"
            class="input input-bordered input-sm flex-1"
            placeholder="输入用户名"
            @keyup.enter="handleAddMember"
          >
          <button class="btn btn-sm btn-primary" @click="handleAddMember">添加</button>
        </div>
        <p v-if="addMemberError" class="text-red-500 text-xs mt-1">{{ addMemberError }}</p>
      </div>
    </div>

    <!-- 角色列表 -->
    <div v-if="activeTab === 'characters'" class="flex-1 space-y-3">
      <div v-for="c in group.characters" :key="c.id" class="flex items-center gap-3">
        <div class="avatar">
          <div class="w-10 rounded-full">
            <img :src="c.photo" alt="">
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-medium">{{ c.name }}</div>
          <div class="text-xs text-gray-500 line-clamp-2">{{ c.profile }}</div>
        </div>
      </div>

      <!-- 添加角色（群主/管理员可见） -->
      <div v-if="isAdmin()" class="pt-3 border-t">
        <div class="text-xs text-gray-500 mb-2">添加角色</div>
        <div class="flex gap-1 mb-2">
          <input
            v-model="characterSearchQuery"
            class="input input-bordered input-sm flex-1"
            placeholder="搜索角色名"
            @keyup.enter="handleSearchCharacters"
          >
          <button class="btn btn-sm" @click="handleSearchCharacters">搜索</button>
        </div>

        <!-- 搜索结果 -->
        <div v-if="isSearching" class="text-xs text-gray-400">搜索中...</div>
        <div v-else class="space-y-2">
          <div v-for="c in searchResults" :key="c.id" class="flex items-center gap-2 p-2 rounded hover:bg-base-300 cursor-pointer" @click="handleAddCharacter(c.id)">
            <div class="avatar">
              <div class="w-8 rounded-full">
                <img :src="c.photo" alt="">
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium">{{ c.name }}</div>
              <div class="text-xs text-gray-500 line-clamp-1">{{ c.profile }}</div>
            </div>
            <span class="text-primary text-xs">+添加</span>
          </div>
          <div v-if="characterSearchQuery && searchResults.length === 0 && !isSearching" class="text-xs text-gray-400">
            没有找到可添加的角色
          </div>
        </div>
        <p v-if="addCharacterError" class="text-red-500 text-xs mt-1">{{ addCharacterError }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
