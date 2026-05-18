<script setup>
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";

const emit = defineEmits(['created'])
const modalRef = useTemplateRef('modal-ref')
const name = ref('')
const description = ref('')
const error = ref('')

async function handleSubmit() {
  error.value = ''
  if (!name.value.trim()) {
    error.value = '群名不能为空'
    return
  }
  try {
    const res = await api.post('api/group/create/', {
      name: name.value.trim(),
      description: description.value.trim(),
    })
    if (res.data.result === 'success') {
      emit('created', res.data.group)
      name.value = ''
      description.value = ''
      modalRef.value.close()
    } else {
      error.value = res.data.result
    }
  } catch (err) {
    error.value = '创建失败，请重试'
  }
}

function showModal() {
  modalRef.value.showModal()
}

defineExpose({showModal})
</script>

<template>
  <dialog ref="modal-ref" class="modal">
    <div class="modal-box">
      <h3 class="text-lg font-bold mb-4">创建群聊</h3>
      <div class="form-control">
        <label class="label"><span class="label-text">群名</span></label>
        <input v-model="name" class="input input-bordered" placeholder="输入群名" maxlength="100">
      </div>
      <div class="form-control mt-4">
        <label class="label"><span class="label-text">群简介</span></label>
        <textarea v-model="description" class="textarea textarea-bordered" placeholder="介绍一下这个群" maxlength="500"></textarea>
      </div>
      <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
      <div class="modal-action">
        <button class="btn" @click="modalRef.close()">取消</button>
        <button class="btn btn-primary" @click="handleSubmit">创建</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped></style>
