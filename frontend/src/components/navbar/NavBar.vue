<script setup>

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
import {useUserStore} from "@/stores/user.js";
import UserMenu from "@/components/navbar/UserMenu.vue";

const user = useUserStore()
</script>

<template>
<div class="drawer lg:drawer-open">
  <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- Navbar -->
    <nav class="navbar w-full bg-base-100 shadow-sm">
      <!-- 左侧：图标 + 标题（固定不压缩） -->
      <div class="flex items-center gap-1 shrink-0">
        <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
          <MenuIcon />
        </label>
        <div class="px-1 font-bold text-lg md:text-xl whitespace-nowrap">AIFriends</div>
      </div>

      <!-- 中间：使用 margin auto 实现居中，不占满剩余空间 -->
      <div class="mx-auto px-2 shrink min-w-0">
        <div class="join w-auto max-w-xl min-w-50">
          <input
            class="input join-item rounded-l-full w-40 sm:w-80 md:w-96 grow"
            placeholder="搜索你感兴趣的内容"
          />
          <button class="btn join-item rounded-r-full gap-0">
            <SearchIcon />
            <span class="hidden sm:inline">搜索</span>
          </button>
        </div>
      </div>

      <!-- 右侧：登录按钮（固定不压缩） -->
      <div class="shrink-0 ">
        <RouterLink v-if="user.isLogin()" :to="{name: 'create-index'}" active-class="btn-active" class="btn btn-ghost text-base px-1 mx-1">
          <CreateIcon />
            创作
        </RouterLink>
        <RouterLink v-if="!user.isLogin()" :to="{name: 'user-account-login-index'}" active-class="btn-active" class="btn btn-ghost text-base whitespace-nowrap">
          登录
        </RouterLink>
        <UserMenu v-else />
      </div>
    </nav>
    <!-- Page content here -->
    <slot ></slot>
  </div>

  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
    <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-40">
      <!-- Sidebar content here -->
      <ul class="menu w-full grow">
        <!-- List item -->
        <li>
          <RouterLink :to="{name: 'homepage-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="首页">
            <!-- Home icon -->
            <HomepageIcon />
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap py-1.5">首页</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{name: 'friend-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="好友">
            <!-- Home icon -->
            <FriendIcon />
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap py-1.5">好友</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{name: 'create-index'}" active-class="menu-focus" class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="创作">
            <!-- Home icon -->
            <CreateIcon />
            <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap py-1.5">创作</span>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</div>
</template>

<style scoped>

</style>